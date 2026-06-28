import csv
import io
import base64
import hashlib

from daytona import Daytona, DaytonaError
from langchain_daytona import DaytonaSandbox
from pathlib import Path


def list_sandboxes() -> list[dict]:
    d = Daytona()
    raw = d.list(limit=50)
    boxes = []
    for item in (raw.items or []):
        sid = getattr(item, "id", None)
        state = getattr(item, "state", None)
        boxes.append({"id": sid, "state": state, "_sandbox": item})
    return boxes


def cleanup_stale_sandboxes() -> int:
    d = Daytona()
    boxes = list_sandboxes()
    if not boxes:
        return 0

    count = 0
    for box in boxes:
        sb = box.get("_sandbox")
        if not sb:
            continue
        try:
            d.stop(sb)
            d.delete(sb)
            count += 1
        except Exception:
            pass
    return count




def upload_skills_to_daytona(backend: DaytonaSandbox, src_skill_folder_path: str, sandbox_dest_path: str = "/skills") -> dict:
    try:
        skills_dir = Path(src_skill_folder_path).resolve()
        if not skills_dir.exists() or not skills_dir.is_dir():
            return {
                "status": "failed",
                "error": f"Local skill directory does not exist or is not a directory: {src_skill_folder_path}",
                "uploaded_files": [],
                "missing_files": []
            }

        # Normalize the destination path prefix (ensure it starts with / and has no trailing /)
        dest_prefix = "/" + sandbox_dest_path.strip("/")

        skill_files: list[tuple[str, bytes]] = []
        destinations: list[str] = []
        for path in sorted(skills_dir.rglob("*")):
            if not path.is_file():
                continue

            rel = path.resolve().relative_to(skills_dir)
            sandbox_destination = f"{dest_prefix}/{rel.as_posix()}"
            skill_files.append((sandbox_destination, path.read_bytes()))
            destinations.append(sandbox_destination)

        if not skill_files:
            return {
                "status": "failed",
                "error": "No files found to upload in the specified skill directory",
                "uploaded_files": [],
                "missing_files": []
            }

        # Pre-create all parent directories in the sandbox before upload
        unique_parents = sorted(list({str(Path(dest).parent) for dest in destinations}))
        for parent in unique_parents:
            mkdir_r = backend.execute(f"mkdir -p '{parent}'")
            if mkdir_r.exit_code != 0:
                return {
                    "status": "failed",
                    "error": f"Failed to create directory '{parent}' in sandbox: {mkdir_r.output.strip()}. "
                             f"This usually means the path is not writable by the sandbox user (e.g. root '/' permissions). "
                             f"Try using a path inside '/home/daytona/' or the workspace folder.",
                    "uploaded_files": [],
                    "missing_files": []
                }

        backend.upload_files(skill_files)

        # Verification step: check that all files exist in the sandbox
        missing_files = []
        for dest in destinations:
            verify_r = backend.execute(f"test -s '{dest}'")
            if verify_r.exit_code != 0:
                missing_files.append(dest)

        if missing_files:
            return {
                "status": "failed",
                "error": f"Verification failed. Some files were not found or are empty in the sandbox: {missing_files}",
                "uploaded_files": [d for d in destinations if d not in missing_files],
                "missing_files": missing_files
            }

        return {
            "status": "success",
            "uploaded_files": destinations,
            "missing_files": []
        }
    except Exception as e:
        return {
            "status": "failed",
            "error": f"An error occurred during upload: {str(e)}",
            "uploaded_files": [],
            "missing_files": []
        }



def connect_with_existing_sandbox_with_daytona(sandbox_id: str, max_retries: int = 1) -> DaytonaSandbox:
    for attempt in range(max_retries + 1):
        try:
            if sandbox_id:
                sandbox = Daytona().get(sandbox_id)
                backend = DaytonaSandbox(sandbox=sandbox)
                return backend
            else:
                raise ValueError("sandbox_id is required")
        except DaytonaError as e:
            err = str(e).lower()
            if "disk limit" in err or "quota" in err or "disk" in err:
                cleanup_stale_sandboxes()
                if attempt < max_retries:
                    continue
            raise


def create_new_sandbox_with_daytona(max_retries: int = 1) -> DaytonaSandbox:
    for attempt in range(max_retries + 1):
        try:
            sandbox = Daytona().create()
            backend = DaytonaSandbox(sandbox=sandbox)
            return backend
        except DaytonaError as e:
            err = str(e).lower()
            if "disk limit" in err or "quota" in err or "disk" in err:
                cleanup_stale_sandboxes()
                if attempt < max_retries:
                    continue
            raise


def write_csv_to_sandbox(
    backend: DaytonaSandbox,
    data: list[list[str | int | float]],
    path: str = "/tmp/data.csv",
    overwrite: bool = True,
) -> dict:
    if not data:
        return {
            "status": "failed",
            "path": path,
            "rows_written": 0,
            "lines_on_sandbox": 0,
            "content_match": False,
            "error": "no data provided",
        }

    if not overwrite:
        check = backend.execute(f"test -f {path}")
        if check.exit_code == 0:
            return {
                "status": "failed",
                "path": path,
                "rows_written": 0,
                "lines_on_sandbox": 0,
                "content_match": False,
                "error": f"file already exists at {path} (set overwrite=True to replace)",
            }

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerows(data)
    csv_bytes = buf.getvalue().encode("utf-8")
    sent_md5 = hashlib.md5(csv_bytes).hexdigest()
    csv_base64 = base64.b64encode(csv_bytes).decode()

    result: dict = {
        "status": "failed",
        "path": path,
        "rows_written": len(data),
        "lines_on_sandbox": 0,
        "content_match": False,
        "error": None,
    }

    try:
        write_r = backend.execute(f"echo {csv_base64} | base64 -d > {path}")
        if write_r.exit_code != 0:
            result["error"] = f"write failed: {write_r.output}"
            return result

        cat_r = backend.execute(f"cat {path}")
        if cat_r.exit_code != 0:
            result["error"] = f"read-back failed: {cat_r.output}"
            return result

        read_back = cat_r.output
        read_md5 = hashlib.md5(read_back.encode("utf-8")).hexdigest()
        result["content_match"] = sent_md5 == read_md5

        wc_r = backend.execute(f"wc -l < {path}")
        if wc_r.exit_code == 0:
            result["lines_on_sandbox"] = int(wc_r.output.strip())

        if result["content_match"]:
            result["status"] = "success"
        else:
            result["status"] = "data_corrupted"
            result["error"] = "MD5 checksum mismatch between sent content and read-back content"

    except Exception as e:
        result["error"] = str(e)

    return result
