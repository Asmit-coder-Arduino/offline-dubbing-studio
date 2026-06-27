# Offline Video Dubbing Studio

A production-quality Android application for AI-powered video dubbing — **100% offline** after installation. Built with Python, Kivy, and Buildozer.

---

## Features

| Feature | Details |
|---|---|
| Video import | MP4, MKV, MOV, AVI, WEBM, 3GP |
| Speech recognition | Whisper.cpp (offline, on-device) |
| Text-to-speech | Piper TTS (offline, neural voices) |
| Voice recording | Record your own voice for dubbing |
| Subtitle generation | Auto-generate from speech |
| Subtitle editing | Full in-app editor with timing control |
| SRT export | Export subtitles as `.srt` files |
| MP4 export | Dubbed video saved to `Movies/OfflineDubber` |
| Batch processing | Background service for multiple videos |
| Dark mode | Material Design dark/light theme |
| 16 languages | Auto-detection and multilingual TTS |
| Background audio | Keeps background music while replacing speech |
| Audio normalization | EBU R128 loudness normalization |
| Progress indicator | Step-by-step processing feedback |
| History | View and re-share past projects |

---

## Project Structure

```
offline-dubbing-studio/
├── main.py                     # App entry point
├── buildozer.spec              # Buildozer Android configuration
├── requirements.txt            # Python dependencies
│
├── screens/                    # Kivy UI screens
│   ├── splash_screen.py        # Animated startup screen
│   ├── home_screen.py          # Main dashboard
│   ├── video_picker_screen.py  # File browser
│   ├── language_screen.py      # Source/target language selection
│   ├── voice_screen.py         # TTS voice or own-voice recording
│   ├── subtitle_editor_screen.py  # Subtitle editing
│   ├── processing_screen.py    # Pipeline progress
│   ├── export_screen.py        # Output and sharing
│   ├── settings_screen.py      # App configuration
│   ├── history_screen.py       # Past projects
│   └── about_screen.py         # App info
│
├── widgets/                    # Reusable UI components
│   ├── material_button.py      # Styled button
│   ├── progress_card.py        # Processing step card
│   ├── subtitle_item.py        # Editable subtitle row
│   └── video_card.py           # Video / history card
│
├── utils/                      # Business logic utilities
│   ├── background_service.py   # Android foreground service
│   ├── ffmpeg/
│   │   └── ffmpeg_utils.py     # All FFmpeg operations
│   ├── speech/
│   │   └── whisper_engine.py   # Whisper.cpp wrapper
│   ├── tts/
│   │   └── piper_engine.py     # Piper TTS wrapper
│   ├── subtitle/
│   │   └── subtitle_utils.py   # SRT read/write/edit
│   └── video/
│       └── video_utils.py      # Video metadata and scanning
│
├── database/                   # SQLite persistence
│   ├── db_manager.py           # Connection & table creation
│   ├── history/
│   │   └── history_manager.py  # Dubbing job history
│   └── settings/
│       └── settings_manager.py # App settings key-value store
│
└── assets/
    ├── fonts/                  # Custom TTF fonts (optional)
    ├── icons/                  # App icons (add app_icon.png)
    └── models/                 # AI model files (see below)
```

---

## Requirements

### Development Machine (Linux recommended)

| Tool | Version | Notes |
|---|---|---|
| Python | 3.10+ | `pyenv` recommended |
| pip | latest | `pip install --upgrade pip` |
| Buildozer | 1.5+ | `pip install buildozer` |
| Android SDK | API 33 | Downloaded automatically by Buildozer |
| Android NDK | r25b | Downloaded automatically |
| Java JDK | 17 | `sudo apt install openjdk-17-jdk` |
| FFmpeg | 6+ | System FFmpeg for dev testing |

### Ubuntu / Debian quick setup

```bash
sudo apt update
sudo apt install -y \
    python3 python3-pip python3-venv \
    git zip unzip openjdk-17-jdk \
    autoconf libtool pkg-config \
    libffi-dev libssl-dev \
    build-essential cmake ninja-build \
    ffmpeg

pip install buildozer cython==0.29.37 kivy==2.3.0 kivymd pillow
```

---

## AI Model Setup

### Whisper.cpp (Speech Recognition)

1. Build whisper.cpp for Android (cross-compile) or use a pre-built binary:
   ```bash
   git clone https://github.com/ggerganov/whisper.cpp
   cd whisper.cpp
   bash ./models/download-ggml-model.sh tiny.en   # 75MB, included in APK
   bash ./models/download-ggml-model.sh base.en   # 142MB, optional
   ```
2. Copy model files to `assets/models/`:
   ```
   assets/models/ggml-tiny.en.bin
   assets/models/ggml-base.en.bin   (optional)
   ```
3. Build `main` binary for Android ARM64:
   ```bash
   cd whisper.cpp
   cmake -B build-android -DCMAKE_TOOLCHAIN_FILE=$ANDROID_NDK/build/cmake/android.toolchain.cmake \
       -DANDROID_ABI=arm64-v8a -DANDROID_PLATFORM=android-21
   cmake --build build-android
   cp build-android/bin/main ../offline-dubbing-studio/assets/whisper/main
   ```

### Piper TTS (Text-to-Speech)

1. Download voice models from Hugging Face:
   ```
   https://huggingface.co/rhasspy/piper-voices/tree/main
   ```
2. Download for each desired voice:
   - `en_US-amy-medium.onnx`
   - `en_US-amy-medium.onnx.json`
3. Place in `assets/models/piper/`:
   ```
   assets/models/piper/en_US-amy-medium.onnx
   assets/models/piper/en_US-amy-medium.onnx.json
   ```
4. Build `piper` binary for Android (cross-compile):
   ```
   https://github.com/rhasspy/piper — see build instructions for Android
   ```

### Recommended bundled model set (keeps APK under 200MB)

| File | Size | Purpose |
|---|---|---|
| `ggml-tiny.en.bin` | 75 MB | English speech recognition |
| `en_US-amy-medium.onnx` | 63 MB | English TTS voice |
| `en_US-amy-medium.onnx.json` | ~2 KB | Voice config |

Total: ~138 MB — fits in a standard APK.

---

## Building the APK

### 1. Clone / copy the project

```bash
git clone <your-repo> offline-dubbing-studio
cd offline-dubbing-studio
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Add AI models and icons

Follow the **AI Model Setup** section above.
Add `assets/icons/app_icon.png` (512×512 RGBA PNG).

### 4. Build debug APK

```bash
buildozer android debug
```

This will:
- Download the Android SDK and NDK automatically (first run takes ~20 minutes)
- Cross-compile all dependencies for ARM
- Package the app as `.apk`

Output: `bin/offlinedubber-1.0.0-arm64-v8a_armeabi-v7a-debug.apk`

### 5. Build release APK

```bash
# Generate a signing key (first time only)
keytool -genkey -v -keystore dubbing-release.keystore \
    -alias dubbing -keyalg RSA -keysize 2048 -validity 10000

# Build release
buildozer android release

# Sign the APK
jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 \
    -keystore dubbing-release.keystore \
    bin/offlinedubber-*-release-unsigned.apk dubbing

# Align and verify
zipalign -v 4 \
    bin/offlinedubber-*-release-unsigned.apk \
    bin/offlinedubber-release.apk
```

### 6. Install on device

```bash
adb install bin/offlinedubber-1.0.0-*-debug.apk
```

---

## Running on Desktop (for development)

```bash
# Install desktop dependencies
pip install kivy kivymd pillow ffpyplayer

# Run
python main.py
```

On desktop:
- Videos are loaded from your home directory
- Exports go to `~/OfflineDubber_Exports/`
- System `ffmpeg` and `ffprobe` are used if installed

---

## Troubleshooting

### `buildozer android debug` fails with "SDK not found"

```bash
buildozer android clean
buildozer android debug
```

Buildozer downloads the SDK on first run. Ensure you have accepted the license:
```
android.accept_sdk_license = True
```

### `NDK path not set`

```bash
export ANDROID_NDK_HOME=$HOME/.buildozer/android/platform/android-ndk-r25b
```

### `java.lang.UnsatisfiedLinkError` on device

The NDK compiled binary may not match the device ABI. Ensure `buildozer.spec` includes:
```
android.archs = arm64-v8a, armeabi-v7a
```

### App crashes immediately on launch

1. Check `adb logcat | grep python`
2. Ensure all `assets/models/` and `assets/icons/app_icon.png` are present
3. Run on desktop first to validate Python logic

### Whisper transcription returns empty

- Ensure the model file `ggml-*.bin` is in `assets/models/`
- Ensure the `whisper.cpp` binary is at `assets/whisper/main` and is executable
- Check audio extraction: the extracted WAV must be 16kHz mono PCM

### Piper TTS produces no audio

- Ensure the `.onnx` and `.onnx.json` pair are in `assets/models/piper/`
- Test the piper binary: `echo "Hello" | ./assets/piper/piper --model assets/models/piper/en_US-amy-medium.onnx --output_file test.wav`

### APK size too large

- Use only `tiny.en` Whisper model in the APK bundle
- Offer larger models as optional in-app downloads
- Remove unused Piper voice models

---

## Privacy & Offline Guarantee

- **No network calls** are made by the app at runtime
- All AI inference runs on-device using the bundled binary and model files
- Video files never leave the device
- Export history is stored in a local SQLite database

---

## License

MIT License — see `LICENSE` for details.

AI models are governed by their own licenses:
- Whisper: MIT (OpenAI)
- Piper TTS: MIT (Rhasspy)
- FFmpeg: LGPL/GPL (see FFmpeg docs for static vs dynamic linking requirements)
