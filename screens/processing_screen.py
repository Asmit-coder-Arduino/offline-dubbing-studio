"""Processing screen — runs the full dubbing pipeline in the background."""

import os
import threading
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.app import App
from kivy.clock import Clock

Builder.load_string("""
<ProcessingScreen>:
    canvas.before:
        Color:
            rgba: 0.07, 0.07, 0.10, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(20)

        Label:
            text: 'Processing Video'
            font_size: '22sp'
            bold: True
            color: 1, 1, 1, 1
            size_hint_y: None
            height: dp(50)
            halign: 'center'

        Widget:
            size_hint_y: 0.1

        # Overall progress
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: dp(80)
            spacing: dp(8)

            Label:
                id: overall_label
                text: 'Preparing...'
                font_size: '14sp'
                color: 0.8, 0.8, 1, 1
                halign: 'center'

            ProgressBar:
                id: overall_bar
                max: 100
                value: 0
                size_hint_y: None
                height: dp(8)

            Label:
                id: overall_pct
                text: '0%'
                font_size: '13sp'
                color: 0.5, 0.5, 0.7, 1
                halign: 'center'

        # Step list
        BoxLayout:
            id: step_list
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            spacing: dp(10)

        Widget:

        # Cancel / retry
        BoxLayout:
            size_hint_y: None
            height: dp(52)
            spacing: dp(12)

            Button:
                id: cancel_btn
                text: 'Cancel'
                background_color: 0.6, 0.2, 0.2, 1
                color: 1, 1, 1, 1
                on_release: root.cancel_processing()

            Button:
                id: continue_btn
                text: 'Continue to Export'
                background_color: 0.2, 0.6, 0.3, 1
                color: 1, 1, 1, 1
                opacity: 0
                disabled: True
                on_release: root.go_to_export()
""")

STEPS = [
    ("extract_audio", "Extracting original audio"),
    ("transcribe", "Transcribing speech"),
    ("synthesize_tts", "Synthesizing dubbed speech"),
    ("align_audio", "Aligning audio timing"),
    ("merge_audio", "Merging dubbed audio into video"),
    ("generate_subtitles", "Embedding subtitles"),
    ("export_mp4", "Exporting final MP4"),
]


class ProcessingScreen(Screen):
    """Background processing pipeline for the dubbing job."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._thread = None
        self._cancelled = False
        self._output_path = None

    def on_enter(self):
        self._cancelled = False
        self._output_path = None
        self.ids.continue_btn.opacity = 0
        self.ids.continue_btn.disabled = True
        self._build_step_ui()
        Clock.schedule_once(lambda dt: self._start(), 0.3)

    def _build_step_ui(self):
        container = self.ids.step_list
        container.clear_widgets()
        self._step_labels = {}
        for step_id, step_name in STEPS:
            row = self._make_step_row(step_id, step_name)
            container.add_widget(row)

    def _make_step_row(self, step_id, step_name):
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        row = BoxLayout(orientation="horizontal", size_hint_y=None, height="36dp", spacing="12dp")
        status_lbl = Label(text="○", font_size="16sp", color=(0.4, 0.4, 0.6, 1),
                           size_hint_x=None, width="24dp")
        name_lbl = Label(text=step_name, font_size="13sp", color=(0.7, 0.7, 0.9, 1),
                         halign="left", text_size=(None, None))
        row.add_widget(status_lbl)
        row.add_widget(name_lbl)
        self._step_labels[step_id] = {"status": status_lbl, "name": name_lbl}
        return row

    def _start(self):
        self._thread = threading.Thread(target=self._run_pipeline, daemon=True)
        self._thread.start()

    def _update_step(self, step_id, state):
        if step_id not in self._step_labels:
            return
        icons = {"pending": "○", "running": "◉", "done": "●", "error": "✗"}
        colors = {
            "pending": (0.4, 0.4, 0.6, 1),
            "running": (0.9, 0.8, 0.2, 1),
            "done": (0.3, 0.9, 0.4, 1),
            "error": (1, 0.3, 0.3, 1),
        }
        lbl = self._step_labels[step_id]
        lbl["status"].text = icons.get(state, "○")
        lbl["status"].color = colors.get(state, (0.4, 0.4, 0.6, 1))

    def _set_overall(self, progress, text):
        self.ids.overall_bar.value = progress
        self.ids.overall_label.text = text
        self.ids.overall_pct.text = f"{int(progress)}%"

    def _run_pipeline(self):
        try:
            app = App.get_running_app()
            video_path = app.get_project_data("video_path")
            subtitles = app.get_project_data("subtitles", [])
            dubbing_mode = app.get_project_data("dubbing_mode", "tts")
            tts_voice = app.get_project_data("tts_voice")
            target_lang = app.get_project_data("target_lang", "en")
            source_lang = app.get_project_data("source_lang", "en")
            export_dir = app.get_export_dir()

            from utils.ffmpeg.ffmpeg_utils import FFmpegUtils
            from utils.tts.piper_engine import PiperEngine
            from utils.subtitle.subtitle_utils import SubtitleUtils

            base = os.path.splitext(os.path.basename(video_path))[0]
            tmp_dir = os.path.join(export_dir, f".tmp_{base}")
            os.makedirs(tmp_dir, exist_ok=True)

            def step(step_id, fn, progress_start, progress_end, label):
                if self._cancelled:
                    return
                Clock.schedule_once(
                    lambda dt: (self._update_step(step_id, "running"),
                                self._set_overall(progress_start, label)), 0
                )
                fn()
                Clock.schedule_once(
                    lambda dt: (self._update_step(step_id, "done"),
                                self._set_overall(progress_end, label + " done")), 0
                )

            # Step 1: Extract audio
            extracted_audio = os.path.join(tmp_dir, "original_audio.wav")
            step("extract_audio",
                 lambda: FFmpegUtils.extract_audio(video_path, extracted_audio),
                 0, 14, "Extracting original audio")

            # Step 2: Transcribe (may already have subtitles)
            if not subtitles:
                from utils.speech.whisper_engine import WhisperEngine
                engine = WhisperEngine()
                raw_segs = engine.transcribe(extracted_audio, language=source_lang)
                from screens.subtitle_editor_screen import SubtitleSegment
                subtitles = [SubtitleSegment(i + 1, s["start"], s["end"], s["text"])
                             for i, s in enumerate(raw_segs)]
            Clock.schedule_once(lambda dt: (self._update_step("transcribe", "done"),
                                             self._set_overall(28, "Transcription complete")), 0)

            # Step 3: Synthesize dubbed audio
            dubbed_segments = []
            if dubbing_mode == "tts":
                tts = PiperEngine()
                voice_id = tts_voice["id"] if tts_voice else "en_US-amy-medium"
                for i, seg in enumerate(subtitles):
                    if self._cancelled:
                        return
                    out_wav = os.path.join(tmp_dir, f"seg_{i:04d}.wav")
                    tts.synthesize(seg.text, voice_id, out_wav)
                    dubbed_segments.append({"path": out_wav, "start": seg.start, "end": seg.end})
                    Clock.schedule_once(
                        lambda dt, p=28 + (i + 1) / max(len(subtitles), 1) * 20:
                        (self._update_step("synthesize_tts", "running"),
                         self._set_overall(p, "Synthesizing speech...")), 0
                    )
            else:
                recorded = app.get_project_data("recorded_audio")
                if recorded:
                    dubbed_segments.append({"path": recorded, "start": 0, "end": 9999})
            Clock.schedule_once(lambda dt: (self._update_step("synthesize_tts", "done"),
                                             self._set_overall(48, "Speech synthesis done")), 0)

            # Step 4: Align audio
            aligned_audio = os.path.join(tmp_dir, "aligned_dubbed.wav")
            FFmpegUtils.build_silence_padded_audio(dubbed_segments, aligned_audio,
                                                    FFmpegUtils.get_duration(video_path))
            Clock.schedule_once(lambda dt: (self._update_step("align_audio", "done"),
                                             self._set_overall(62, "Audio aligned")), 0)

            # Step 5: Merge audio
            merged_video = os.path.join(tmp_dir, "merged_video.mp4")
            FFmpegUtils.replace_audio(video_path, aligned_audio, merged_video)
            Clock.schedule_once(lambda dt: (self._update_step("merge_audio", "done"),
                                             self._set_overall(76, "Audio merged")), 0)

            # Step 6: Embed subtitles
            srt_path = os.path.join(tmp_dir, "subtitles.srt")
            SubtitleUtils.write_srt(subtitles, srt_path)
            subtitled_video = os.path.join(tmp_dir, "subtitled_video.mp4")
            FFmpegUtils.add_subtitles(merged_video, srt_path, subtitled_video)
            Clock.schedule_once(lambda dt: (self._update_step("generate_subtitles", "done"),
                                             self._set_overall(88, "Subtitles embedded")), 0)

            # Step 7: Final export
            output_path = os.path.join(export_dir, f"{base}_dubbed.mp4")
            FFmpegUtils.compress_output(subtitled_video, output_path)
            self._output_path = output_path
            app.set_project_data("output_path", output_path)
            Clock.schedule_once(lambda dt: (self._update_step("export_mp4", "done"),
                                             self._set_overall(100, "Export complete!")), 0)

            # Save to history
            from database.history.history_manager import HistoryManager
            HistoryManager().add_entry({
                "input": video_path,
                "output": output_path,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "segments": len(subtitles),
            })

            Clock.schedule_once(lambda dt: self._on_done(), 0.5)
        except Exception as e:
            Clock.schedule_once(
                lambda dt, err=str(e): self._on_error(err), 0
            )

    def _on_done(self):
        self.ids.continue_btn.opacity = 1
        self.ids.continue_btn.disabled = False

    def _on_error(self, err):
        self.ids.overall_label.text = f"Error: {err}"

    def cancel_processing(self):
        self._cancelled = True
        App.get_running_app().navigate_to("home")

    def go_to_export(self):
        App.get_running_app().navigate_to("export")
