# Guide: Recording Coding Sessions on macOS

This guide provides setup instructions for recording high-quality coding vlogs (crisp screen captures and clear voice audio) on macOS.

---

## 🎥 Option A: OBS Studio (Recommended)

OBS Studio is the gold standard for screen recording and streaming. It is free, open-source, and allows advanced audio processing (like removing fan noise and keyboard clicks).

### 1. Installation
1. Download and install [OBS Studio for macOS](https://obsproject.com/).
2. Open OBS Studio.

### 2. Video Settings (For Crisp Text)
To make sure your code is readable:
1. Go to **Settings** > **Video**.
2. Set **Base (Canvas) Resolution** to match your screen resolution (e.g., `2560x1440` or `1920x1080`).
3. Set **Output (Scaled) Resolution** to the same as base resolution (to avoid blurriness from scaling down).
4. Set **Common FPS Values** to `30` or `60` (30 FPS is usually perfect for coding vlogs and saves file size).
5. Go to **Settings** > **Output** > **Recording** tab:
   - **Output Mode**: Simple
   - **Recording Quality**: High Quality, Medium File Size (or Indistinguishable Quality if you have plenty of disk space).
   - **Recording Format**: `mp4` or `mkv` (mkv is safer as it won't corrupt if OBS crashes, but mp4 is easier to edit immediately).
   - **Encoder**: Hardware (Apple VT H.264 or HEVC) for optimal performance.

### 3. Screen Capture Source
1. Under the **Sources** dock at the bottom, click the **`+`** icon.
2. Select **macOS Screen Capture**.
3. Name it "Screen Capture" and click OK.
4. Set **Method** to `Display Capture` to record your entire screen, or `Window Capture` if you only want to record VS Code.
5. Click OK. Drag the corners in the preview window to fit the canvas if needed.

### 4. Audio Settings & Filters (Crisp Voice & No Keyboard Clatter)
1. Go to **Settings** > **Audio** > **Global Audio Devices**.
2. Set **Mic/Auxiliary Audio** to your microphone.
3. Click OK. You will see the audio levels green/yellow bars moving in the **Audio Mixer** dock when you speak.
4. To remove keyboard noise and fan hum:
   - Click the three dots `...` next to your Mic/Aux track in the **Audio Mixer**.
   - Select **Filters**.
   - Click the **`+`** icon at the bottom left of the filters window.
   - Add **Noise Suppression** (use RNNoise for high quality, or Speex if you have CPU constraints).
   - Add **Noise Gate** (adjust the open/close thresholds so it only registers when you speak, silencing keyboard clicks when you are silent).
   - Add **Gain** if your microphone is too quiet.

### 5. Keyboard Shortcuts
1. Go to **Settings** > **Hotkeys**.
2. Assign keys (e.g., `Option+Cmd+R` to start and `Option+Cmd+S` to stop recording) so you don't have to switch to OBS to control it.

---

## 🍏 Option B: QuickTime Player (Built-in & Simple)

If you do not want to install any third-party software:

1. Open **QuickTime Player** (built-in on macOS).
2. Go to **File** > **New Screen Recording** (or press `Cmd+Shift+5`).
3. In the recording controls toolbar at the bottom:
   - Click **Options**.
   - Under **Microphone**, select your microphone (by default it might be set to "None").
   - Under **Save to**, select where you want the recording to go.
4. Click **Record** to start.
5. To stop, click the **Stop button** in the macOS menu bar at the top right of your screen (or press `Cmd+Ctrl+Esc`).
