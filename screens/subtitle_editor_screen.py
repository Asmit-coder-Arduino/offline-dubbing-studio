"""Subtitle editor screen — view, edit, add, and delete subtitle segments."""

import threading
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

Builder.load_string("""
<SubtitleEditorScreen>:
    canvas.before:
        Color:
            rgba: 0.07, 0.07, 0.10, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'

        BoxLayout:
            size_hint_y: None
            height: dp(56)
            padding: dp(8)
            spacing: dp(8)
            canvas.before:
                Color:
                    rgba: 0.10, 0.10, 0.15, 1
                Rectangle:
                    pos: self.pos
                    size: self.size

            Button:
                text: '<'
                size_hint_x: None
                width: dp(40)
                background_color: 0, 0, 0, 0
                color: 1, 1, 1, 1
                font_size: '20sp'
                on_release: app.navigate_to('voice')

            Label:
                text: 'Subtitle Editor'
                font_size: '18sp'
                bold: True
                color: 1, 1, 1, 1
                halign: 'left'
                text_size: self.size
                valign: 'center'

            Button:
                text: 'Export SRT'
                size_hint_x: None
                width: dp(90)
                background_color: 0.2, 0.6, 0.3, 1
                color: 1, 1, 1, 1
                font_size: '12sp'
                on_release: root.export_srt()

        BoxLayout:
            size_hint_y: None
            height: dp(44)
            padding: dp(8), dp(4)
            spacing: dp(8)
            canvas.before:
                Color:
                    rgba: 0.10, 0.10, 0.18, 1
                Rectangle:
                    pos: self.pos
                    size: self.size

            Button:
                text: 'Transcribe Audio'
                size_hint_x: 0.5
                background_color: 0.3, 0.5, 0.9, 1
                color: 1, 1, 1, 1
                font_size: '12sp'
                on_release: root.transcribe_audio()

            Button:
                text: '+ Add Segment'
                size_hint_x: 0.3
                background_color: 0.2, 0.5, 0.3, 1
                color: 1, 1, 1, 1
                font_size: '12sp'
                on_release: root.add_segment()

            Button:
                text: 'Clear All'
                size_hint_x: 0.2
                background_color: 0.6, 0.2, 0.2, 1
                color: 1, 1, 1, 1
                font_size: '12sp'
                on_release: root.clear_subtitles()

        Label:
            id: status_label
            text: 'No subtitles yet. Tap Transcribe Audio to generate automatically.'
            font_size: '12sp'
            color: 0.5, 0.5, 0.7, 1
            size_hint_y: None
            height: dp(36)
            halign: 'center'
            text_size: self.size

        ScrollView:
            BoxLayout:
                id: subtitle_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(8)
                spacing: dp(6)

        Button:
            text: 'Start Processing'
            size_hint_y: None
            height: dp(52)
            background_color: 0.25, 0.47, 0.95, 1
            color: 1, 1, 1, 1
            font_size: '16sp'
            bold: True
            on_release: root.start_processing()
""")


class SubtitleSegment:
    def __init__(self, index, start, end, text):
        self.index = index
        self.start = start  # seconds (float)
        self.end = end
        self.text = text


def seconds_to_srt_time(s):
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = int(s % 60)
    ms = int((s - int(s)) * 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"


class SubtitleEditorScreen(Screen):
    """Edit subtitle segments before processing."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._segments = []
        self._transcribing = False

    def on_enter(self):
        if not self._segments:
            self._render_segments()

    def transcribe_audio(self):
        if self._transcribing:
            return
        self._transcribing = True
        self.ids.status_label.text = "Extracting audio and transcribing (this may take a moment)..."
        threading.Thread(target=self._do_transcribe, daemon=True).start()

    def _do_transcribe(self):
        try:
            app = App.get_running_app()
            video_path = app.get_project_data("video_path")
            source_lang = app.get_project_data("source_lang", "en")

            from utils.ffmpeg.ffmpeg_utils import FFmpegUtils
            from utils.speech.whisper_engine import WhisperEngine

            tmp_audio = video_path + "_extracted.wav"
            FFmpegUtils.extract_audio(video_path, tmp_audio)

            engine = WhisperEngine()
            segments = engine.transcribe(tmp_audio, language=source_lang)

            self._segments = [
                SubtitleSegment(i + 1, seg["start"], seg["end"], seg["text"])
                for i, seg in enumerate(segments)
            ]
            app.set_project_data("subtitles", self._segments)
            Clock.schedule_once(lambda dt: self._on_transcribe_done(), 0)
        except Exception as e:
            Clock.schedule_once(
                lambda dt, err=str(e): setattr(
                    self.ids.status_label, "text", f"Transcription error: {err}"
                ),
                0,
            )
            self._transcribing = False

    def _on_transcribe_done(self):
        self._transcribing = False
        self.ids.status_label.text = f"{len(self._segments)} segments transcribed."
        self._render_segments()

    def add_segment(self):
        last_end = self._segments[-1].end if self._segments else 0.0
        seg = SubtitleSegment(len(self._segments) + 1, last_end, last_end + 3.0, "New subtitle text")
        self._segments.append(seg)
        self._render_segments()

    def clear_subtitles(self):
        self._segments = []
        self._render_segments()
        self.ids.status_label.text = "All subtitles cleared."

    def _render_segments(self):
        container = self.ids.subtitle_list
        container.clear_widgets()
        for seg in self._segments:
            row = self._build_segment_row(seg)
            container.add_widget(row)
        if not self._segments:
            lbl = Label(
                text="No subtitle segments.",
                color=(0.4, 0.4, 0.5, 1),
                font_size="13sp",
                size_hint_y=None,
                height="48dp",
            )
            container.add_widget(lbl)

    def _build_segment_row(self, seg):
        row = BoxLayout(orientation="vertical", size_hint_y=None, height=120, padding=8, spacing=4)
        with row.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.13, 0.13, 0.20, 1)
            row._bg = RoundedRectangle(pos=row.pos, size=row.size, radius=[8])
        row.bind(pos=lambda i, v: setattr(i._bg, "pos", v))
        row.bind(size=lambda i, v: setattr(i._bg, "size", v))

        # Timecode row
        time_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=32, spacing=6)
        index_lbl = Label(text=f"#{seg.index}", font_size="11sp", color=(0.4, 0.6, 1, 1),
                          size_hint_x=None, width=28)
        start_in = TextInput(
            text=f"{seg.start:.2f}", multiline=False, font_size="12sp",
            background_color=(0.18, 0.18, 0.28, 1), foreground_color=(1, 1, 1, 1),
            size_hint_x=None, width=70,
        )
        sep_lbl = Label(text="→", font_size="14sp", color=(0.6, 0.6, 0.8, 1), size_hint_x=None, width=24)
        end_in = TextInput(
            text=f"{seg.end:.2f}", multiline=False, font_size="12sp",
            background_color=(0.18, 0.18, 0.28, 1), foreground_color=(1, 1, 1, 1),
            size_hint_x=None, width=70,
        )
        del_btn = Button(text="X", size_hint_x=None, width=32, background_color=(0.7, 0.2, 0.2, 1),
                         color=(1, 1, 1, 1), font_size="12sp")
        del_btn.bind(on_release=lambda b, s=seg: self._delete_segment(s))
        start_in.bind(text=lambda w, v, s=seg: self._update_time(s, "start", v))
        end_in.bind(text=lambda w, v, s=seg: self._update_time(s, "end", v))

        time_row.add_widget(index_lbl)
        time_row.add_widget(start_in)
        time_row.add_widget(sep_lbl)
        time_row.add_widget(end_in)
        time_row.add_widget(del_btn)

        # Text input
        text_in = TextInput(
            text=seg.text, multiline=True, font_size="13sp",
            background_color=(0.10, 0.12, 0.20, 1), foreground_color=(1, 1, 1, 1),
        )
        text_in.bind(text=lambda w, v, s=seg: setattr(s, "text", v))

        row.add_widget(time_row)
        row.add_widget(text_in)
        return row

    def _update_time(self, seg, attr, value):
        try:
            setattr(seg, attr, float(value))
        except ValueError:
            pass

    def _delete_segment(self, seg):
        self._segments = [s for s in self._segments if s.index != seg.index]
        for i, s in enumerate(self._segments):
            s.index = i + 1
        self._render_segments()

    def export_srt(self):
        if not self._segments:
            self.ids.status_label.text = "No subtitles to export."
            return
        try:
            app = App.get_running_app()
            out_dir = app.get_export_dir()
            import os
            srt_path = os.path.join(out_dir, "subtitles.srt")
            from utils.subtitle.subtitle_utils import SubtitleUtils
            SubtitleUtils.write_srt(self._segments, srt_path)
            self.ids.status_label.text = f"Exported: {srt_path}"
        except Exception as e:
            self.ids.status_label.text = f"Export error: {e}"

    def start_processing(self):
        app = App.get_running_app()
        app.set_project_data("subtitles", self._segments)
        app.navigate_to("processing")
