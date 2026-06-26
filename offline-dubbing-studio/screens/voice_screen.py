"""Voice selection and recording screen."""

import os
import threading
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.app import App
from kivy.clock import Clock

Builder.load_string("""
<VoiceScreen>:
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
                on_release: app.navigate_to('language')

            Label:
                text: 'Voice Selection'
                font_size: '18sp'
                bold: True
                color: 1, 1, 1, 1
                halign: 'left'
                text_size: self.size
                valign: 'center'

        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(16)
                spacing: dp(16)

                # Mode selector
                Label:
                    text: 'Dubbing Mode'
                    font_size: '15sp'
                    bold: True
                    color: 0.8, 0.8, 1, 1
                    size_hint_y: None
                    height: dp(32)
                    halign: 'left'
                    text_size: self.size

                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: dp(48)
                    spacing: dp(8)

                    Button:
                        id: btn_tts
                        text: 'AI Voice (TTS)'
                        background_color: 0.25, 0.47, 0.95, 1
                        color: 1, 1, 1, 1
                        on_release: root.set_mode('tts')

                    Button:
                        id: btn_record
                        text: 'Record My Voice'
                        background_color: 0.18, 0.18, 0.28, 1
                        color: 0.8, 0.8, 1, 1
                        on_release: root.set_mode('record')

                # TTS voice list
                BoxLayout:
                    id: tts_panel
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: dp(8)

                    Label:
                        text: 'Available AI Voices (Piper TTS)'
                        font_size: '14sp'
                        bold: True
                        color: 0.7, 0.7, 0.9, 1
                        size_hint_y: None
                        height: dp(32)
                        halign: 'left'
                        text_size: self.size

                    GridLayout:
                        id: voice_grid
                        cols: 1
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: dp(6)

                # Record panel
                BoxLayout:
                    id: record_panel
                    orientation: 'vertical'
                    size_hint_y: None
                    height: dp(0)
                    opacity: 0
                    spacing: dp(12)

                    Label:
                        text: 'Record Your Voice'
                        font_size: '14sp'
                        bold: True
                        color: 0.7, 0.7, 0.9, 1
                        size_hint_y: None
                        height: dp(32)
                        halign: 'left'
                        text_size: self.size

                    Label:
                        id: record_status
                        text: 'Tap to start recording'
                        font_size: '13sp'
                        color: 0.6, 0.6, 0.8, 1
                        size_hint_y: None
                        height: dp(32)
                        halign: 'center'
                        text_size: self.size

                    Button:
                        id: record_btn
                        text: 'Start Recording'
                        size_hint_y: None
                        height: dp(56)
                        background_color: 0.9, 0.2, 0.2, 1
                        color: 1, 1, 1, 1
                        font_size: '16sp'
                        on_release: root.toggle_recording()

                    ProgressBar:
                        id: audio_level
                        max: 100
                        value: 0
                        size_hint_y: None
                        height: dp(8)

        Button:
            text: 'Continue to Subtitle Editor'
            size_hint_y: None
            height: dp(52)
            background_color: 0.25, 0.47, 0.95, 1
            color: 1, 1, 1, 1
            font_size: '15sp'
            on_release: root.continue_to_subtitles()
""")

PIPER_VOICES = [
    {"name": "Amy (Female, US)", "id": "en_US-amy-medium", "lang": "en"},
    {"name": "Danny (Male, UK)", "id": "en_GB-danny-low", "lang": "en"},
    {"name": "Kathleen (Female, US)", "id": "en_US-kathleen-low", "lang": "en"},
    {"name": "Lessac (Female, US)", "id": "en_US-lessac-high", "lang": "en"},
    {"name": "Ryan (Male, UK)", "id": "en_GB-ryan-high", "lang": "en"},
    {"name": "Kusal (Male, ES)", "id": "es_ES-davefx-medium", "lang": "es"},
    {"name": "Carlfm (Male, ES)", "id": "es_ES-carlfm-x_low", "lang": "es"},
    {"name": "Upmc (Female, FR)", "id": "fr_FR-upmc-medium", "lang": "fr"},
    {"name": "Thorsten (Male, DE)", "id": "de_DE-thorsten-high", "lang": "de"},
    {"name": "Paola (Female, IT)", "id": "it_IT-paola-medium", "lang": "it"},
]


class VoiceScreen(Screen):
    """Select AI voice or record own voice."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._mode = "tts"
        self._selected_voice = None
        self._is_recording = False
        self._recording_thread = None

    def on_enter(self):
        self._populate_voices()
        self.set_mode("tts")

    def _populate_voices(self):
        app = App.get_running_app()
        target_lang = app.get_project_data("target_lang", "en")
        grid = self.ids.voice_grid
        grid.clear_widgets()

        voices = [v for v in PIPER_VOICES if v["lang"] == target_lang]
        if not voices:
            voices = PIPER_VOICES[:5]

        for voice in voices:
            selected = self._selected_voice and self._selected_voice["id"] == voice["id"]
            bg = (0.25, 0.47, 0.95, 1) if selected else (0.18, 0.18, 0.28, 1)
            from kivy.uix.button import Button
            btn = Button(
                text=voice["name"],
                size_hint_y=None,
                height="48dp",
                background_color=bg,
                color=(1, 1, 1, 1),
                font_size="14sp",
            )
            btn.bind(on_release=lambda b, v=voice: self._select_voice(v))
            grid.add_widget(btn)

    def _select_voice(self, voice):
        self._selected_voice = voice
        self._populate_voices()

    def set_mode(self, mode):
        self._mode = mode
        if mode == "tts":
            self.ids.tts_panel.height = self.ids.tts_panel.minimum_height
            self.ids.tts_panel.opacity = 1
            self.ids.record_panel.height = 0
            self.ids.record_panel.opacity = 0
            self.ids.btn_tts.background_color = (0.25, 0.47, 0.95, 1)
            self.ids.btn_record.background_color = (0.18, 0.18, 0.28, 1)
        else:
            self.ids.tts_panel.height = 0
            self.ids.tts_panel.opacity = 0
            self.ids.record_panel.height = self.ids.record_panel.minimum_height
            self.ids.record_panel.opacity = 1
            self.ids.btn_record.background_color = (0.25, 0.47, 0.95, 1)
            self.ids.btn_tts.background_color = (0.18, 0.18, 0.28, 1)

    def toggle_recording(self):
        if self._is_recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self):
        self._is_recording = True
        self.ids.record_btn.text = "Stop Recording"
        self.ids.record_btn.background_color = (0.3, 0.8, 0.3, 1)
        self.ids.record_status.text = "Recording..."
        self._recording_thread = threading.Thread(target=self._do_record, daemon=True)
        self._recording_thread.start()

    def _do_record(self):
        import wave
        import struct
        import math
        app = App.get_running_app()
        out_path = os.path.join(app.get_app_dir(), "recorded_voice.wav")

        try:
            import pyaudio
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 44100
            p = pyaudio.PyAudio()
            stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
            frames = []
            while self._is_recording:
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
                rms = math.sqrt(sum(struct.unpack_from(f"{CHUNK}h", data.ljust(CHUNK * 2, b"\x00"))[-1] ** 2
                                    for _ in range(1)) / 1)
                Clock.schedule_once(
                    lambda dt, r=min(rms / 32768 * 100, 100): setattr(self.ids.audio_level, "value", r), 0
                )
            stream.stop_stream()
            stream.close()
            p.terminate()
            with wave.open(out_path, "wb") as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b"".join(frames))
            Clock.schedule_once(
                lambda dt: setattr(self.ids.record_status, "text", f"Saved: {out_path}"), 0
            )
            app.set_project_data("recorded_audio", out_path)
        except Exception as e:
            Clock.schedule_once(
                lambda dt, err=str(e): setattr(self.ids.record_status, "text", f"Error: {err}"), 0
            )

    def _stop_recording(self):
        self._is_recording = False
        self.ids.record_btn.text = "Start Recording"
        self.ids.record_btn.background_color = (0.9, 0.2, 0.2, 1)
        self.ids.audio_level.value = 0

    def continue_to_subtitles(self):
        app = App.get_running_app()
        app.set_project_data("dubbing_mode", self._mode)
        if self._mode == "tts" and self._selected_voice:
            app.set_project_data("tts_voice", self._selected_voice)
        app.navigate_to("subtitle_editor")
