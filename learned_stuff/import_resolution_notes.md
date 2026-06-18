# Import Resolution Notes

When working with files inside subdirectory folders like `learned_stuff/` that need to import local helper modules (such as `utils.py`), you might encounter static analysis errors (e.g., `Cannot find module 'utils'`) or runtime import errors. This document outlines the solutions for both the IDE linter (Pyright/Pylance) and the Python runtime.

## 1. Fixing the IDE Linter (Pyright/Pylance)

Because the project layout has `src/` as the default import root, Pyright/Pylance does not resolve imports relative to subdirectories like `learned_stuff/` automatically.

To fix this, add `learned_stuff` to the `extraPaths` configuration in [pyproject.toml](file:///Users/nitinaggarwal/Documents/learning/langgraph_deep_agents/pyproject.toml):

```toml
[tool.pyright]
extraPaths = ["learned_stuff"]
```

This tells the static analyzer to also search for modules directly inside the `learned_stuff` directory.

---

## 2. Fixing the Python Runtime

If you execute the script from the project root directory (e.g., running `python learned_stuff/0_create_agent.py`), the python path (`sys.path`) will not include the `learned_stuff/` directory by default. 

To resolve this at runtime, you can choose one of two patterns:

### Option A: Dynamic path appending (Recommended in scripts)
Add the directory of the running script to the Python path dynamically before importing the module:

```python
import sys
from pathlib import Path

# Add the directory containing this script to the Python path
sys.path.append(str(Path(__file__).parent))

from utils import format_messages
```

### Option B: Executing with PYTHONPATH
Define the `PYTHONPATH` environment variable inline when executing the script from the command line:

```bash
PYTHONPATH=learned_stuff python learned_stuff/0_create_agent.py
```
