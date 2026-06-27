AI Models Directory
===================

This directory holds the offline AI model files.

Structure
---------

assets/models/
├── ggml-tiny.en.bin          — Whisper tiny.en (75 MB, English only, fastest)
├── ggml-base.en.bin          — Whisper base.en (142 MB, English only, fast)
├── ggml-small.en.bin         — Whisper small.en (466 MB, English only, balanced)
├── ggml-tiny.bin             — Whisper tiny multilingual (75 MB)
├── ggml-base.bin             — Whisper base multilingual (142 MB)
└── piper/
    ├── en_US-amy-medium.onnx       — Piper TTS Amy (US English, 63 MB)
    ├── en_US-amy-medium.onnx.json  — Voice config
    ├── en_US-lessac-high.onnx      — Piper TTS Lessac (US English, 63 MB)
    ├── en_US-lessac-high.onnx.json
    ├── en_GB-ryan-high.onnx        — Piper TTS Ryan (UK English, 63 MB)
    ├── en_GB-ryan-high.onnx.json
    └── ... (other language models)

Downloading Models
------------------

Whisper GGML models (for whisper.cpp):
    https://huggingface.co/ggerganov/whisper.cpp/tree/main

Piper TTS voice models:
    https://huggingface.co/rhasspy/piper-voices/tree/main

Bundle the small models (tiny.en + one Piper voice) with the APK.
Larger models can be downloaded by the user from within the app.

For Android builds, place models in:
    /data/data/org.offlinedubber/files/models/      (internal storage)

Bundled via Buildozer:
    source.include_exts must include 'bin,onnx,json' in buildozer.spec.
    Keep bundled models under 150 MB total for APK size constraints.
