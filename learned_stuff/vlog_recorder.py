#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
import time
from datetime import datetime

def check_ffmpeg():
    if not shutil.which("ffmpeg"):
        print("❌ Error: ffmpeg is not installed on your system.")
        print("💡 Solution: Install it using Homebrew by running:")
        print("   brew install ffmpeg")
        sys.exit(1)

def get_devices():
    print("🔍 Scanning for screen and audio recording devices...")
    # ffmpeg outputs device list to stderr, and exits with code 1 when listing devices
    result = subprocess.run(
        ["ffmpeg", "-f", "avfoundation", "-list_devices", "true", "-i", ""],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )
    output = result.stderr
    
    screens = []
    audios = []
    
    current_section = None
    for line in output.split("\n"):
        if "AVFoundation video devices" in line:
            current_section = "video"
            continue
        elif "AVFoundation audio devices" in line:
            current_section = "audio"
            continue
            
        if current_section == "video" and "[" in line and "]" in line:
            parts = line.split("]")
            if len(parts) >= 2:
                device_info = parts[-1].strip()
                device_idx = line.split("[")[1].split("]")[0].strip()
                screens.append((device_idx, device_info))
        elif current_section == "audio" and "[" in line and "]" in line:
            parts = line.split("]")
            if len(parts) >= 2:
                device_info = parts[-1].strip()
                device_idx = line.split("[")[1].split("]")[0].strip()
                audios.append((device_idx, device_info))
                
    return screens, audios

def main():
    check_ffmpeg()
    
    screens, audios = get_devices()
    
    if not screens:
        print("❌ No screen capture device found.")
        sys.exit(1)
        
    print("\n🖥️  Available Screens:")
    for idx, name in screens:
        print(f"  [{idx}] {name}")
        
    if not audios:
        print("⚠️  Warning: No audio input/microphone device found.")
        mic_idx = "none"
    else:
        print("\n🎙️  Available Audio Inputs (Microphones):")
        for idx, name in audios:
            print(f"  [{idx}] {name}")
            
        # Default to the first audio device
        mic_idx = audios[0][0]
        
    # Default to the first screen (usually 1 or 0)
    screen_idx = screens[0][0]
    
    output_dir = os.path.expanduser("~/Movies/CodingVlogs")
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = os.path.join(output_dir, f"coding_session_{timestamp}.mp4")
    
    print("\n--------------------------------------------------")
    print(f"🎬 Ready to record:")
    print(f"   - Screen device index: {screen_idx}")
    print(f"   - Audio device index: {mic_idx}")
    print(f"   - Saving to: {output_file}")
    print("--------------------------------------------------")
    print("🔴 Press Ctrl+C to STOP recording.")
    print("   Starting in 3 seconds...")
    time.sleep(3)
    
    # FFmpeg command for recording screen + mic on macOS
    # -f avfoundation specifies the macOS input framework
    # -i "screen_idx:mic_idx" selects the inputs
    # -pix_fmt yuv420p ensures compatibility with standard players
    # -vsync 2 helps keep video and audio in sync
    cmd = [
        "ffmpeg",
        "-f", "avfoundation",
        "-r", "30",  # Capture at 30 FPS
        "-i", f"{screen_idx}:{mic_idx}",
        "-pix_fmt", "yuv420p",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "22",  # Constant Rate Factor (low is higher quality)
        "-c:a", "aac",
        "-b:a", "192k",  # Audio bitrate
        output_file
    ]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n❇️  Recording stopped successfully.")
        print(f"📂 Video saved to: {output_file}")

if __name__ == "__main__":
    main()
