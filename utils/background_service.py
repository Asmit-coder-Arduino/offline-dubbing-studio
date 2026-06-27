"""
Android foreground service for background dubbing processing.
This file is loaded by Buildozer as an Android service.
It receives job parameters via a shared file and updates progress.
"""

import os
import json
import time
import sys


SERVICE_COMM_FILE = "/sdcard/Movies/OfflineDubber/.service_comm.json"
SERVICE_PROGRESS_FILE = "/sdcard/Movies/OfflineDubber/.service_progress.json"


def read_job():
    """Read the pending job from the communication file."""
    if not os.path.isfile(SERVICE_COMM_FILE):
        return None
    with open(SERVICE_COMM_FILE) as f:
        return json.load(f)


def write_progress(progress: float, status: str, step: str = ""):
    """Write the current progress so the UI can read it."""
    data = {"progress": progress, "status": status, "step": step, "ts": time.time()}
    os.makedirs(os.path.dirname(SERVICE_PROGRESS_FILE), exist_ok=True)
    with open(SERVICE_PROGRESS_FILE, "w") as f:
        json.dump(data, f)


def run_job(job: dict):
    """Execute the dubbing pipeline for a single job."""
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from utils.ffmpeg.ffmpeg_utils import FFmpegUtils
    from utils.speech.whisper_engine import WhisperEngine
    from utils.tts.piper_engine import PiperEngine
    from utils.subtitle.subtitle_utils import SubtitleUtils, SubtitleSegment

    video_path = job["video_path"]
    source_lang = job.get("source_lang", "en")
    target_lang = job.get("target_lang", "en")
    voice_id = job.get("voice_id", "en_US-amy-medium")
    export_dir = job.get("export_dir", "/sdcard/Movies/OfflineDubber")
    os.makedirs(export_dir, exist_ok=True)

    base = os.path.splitext(os.path.basename(video_path))[0]
    tmp_dir = os.path.join(export_dir, f".tmp_{base}")
    os.makedirs(tmp_dir, exist_ok=True)

    write_progress(5, "Extracting audio...", "extract_audio")
    extracted_audio = os.path.join(tmp_dir, "original.wav")
    FFmpegUtils.extract_audio(video_path, extracted_audio)

    write_progress(20, "Transcribing...", "transcribe")
    whisper = WhisperEngine()
    raw_segs = whisper.transcribe(extracted_audio, language=source_lang)
    subtitles = [SubtitleSegment(i + 1, s["start"], s["end"], s["text"])
                 for i, s in enumerate(raw_segs)]

    write_progress(40, "Synthesizing dubbed speech...", "synthesize")
    piper = PiperEngine()
    dubbed_segments = []
    for i, seg in enumerate(subtitles):
        out_wav = os.path.join(tmp_dir, f"seg_{i:04d}.wav")
        piper.synthesize(seg.text, voice_id, out_wav)
        dubbed_segments.append({"path": out_wav, "start": seg.start, "end": seg.end})
        write_progress(40 + (i + 1) / max(len(subtitles), 1) * 20,
                       f"TTS {i+1}/{len(subtitles)}", "synthesize")

    write_progress(62, "Aligning audio...", "align")
    aligned = os.path.join(tmp_dir, "aligned.wav")
    duration = FFmpegUtils.get_duration(video_path)
    FFmpegUtils.build_silence_padded_audio(dubbed_segments, aligned, duration)

    write_progress(72, "Merging audio...", "merge")
    merged = os.path.join(tmp_dir, "merged.mp4")
    FFmpegUtils.replace_audio(video_path, aligned, merged)

    write_progress(82, "Embedding subtitles...", "subtitles")
    srt_path = os.path.join(tmp_dir, "subtitles.srt")
    SubtitleUtils.write_srt(subtitles, srt_path)
    subtitled = os.path.join(tmp_dir, "subtitled.mp4")
    FFmpegUtils.add_subtitles(merged, srt_path, subtitled)

    write_progress(90, "Exporting final video...", "export")
    output_path = os.path.join(export_dir, f"{base}_dubbed.mp4")
    FFmpegUtils.compress_output(subtitled, output_path)

    write_progress(100, "Done!", "done")

    result_file = SERVICE_COMM_FILE.replace("_comm", "_result")
    with open(result_file, "w") as f:
        json.dump({"status": "done", "output": output_path}, f)

    os.remove(SERVICE_COMM_FILE)


def main():
    """Main service loop — wait for jobs and process them."""
    from android.broadcast import BroadcastReceiver  # noqa: F401 — available at runtime

    write_progress(0, "Service started", "idle")
    while True:
        job = read_job()
        if job:
            try:
                run_job(job)
            except Exception as e:
                write_progress(0, f"Error: {e}", "error")
                if os.path.exists(SERVICE_COMM_FILE):
                    os.remove(SERVICE_COMM_FILE)
        time.sleep(2)


if __name__ == "__main__":
    main()
