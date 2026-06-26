"""Settings screen — app configuration, model selection, theme, quality."""

from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.app import App

Builder.load_string("""
<SettingsScreen>:
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
                on_release: app.navigate_to('home')

            Label:
                text: 'Settings'
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

                # Theme
                SettingSection:
                    title: 'Appearance'

                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: dp(48)
                    spacing: dp(12)

                    Label:
                        text: 'Theme'
                        font_size: '14sp'
                        color: 0.8, 0.8, 1, 1

                    Button:
                        id: theme_btn
                        text: 'Dark'
                        size_hint_x: None
                        width: dp(100)
                        background_color: 0.25, 0.47, 0.95, 1
                        color: 1, 1, 1, 1
                        on_release: root.toggle_theme()

                # Whisper model
                SettingSection:
                    title: 'Speech Recognition Model (Whisper)'

                GridLayout:
                    cols: 1
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: dp(6)
                    id: whisper_model_grid

                # Piper TTS
                SettingSection:
                    title: 'Text-to-Speech Model (Piper)'

                GridLayout:
                    cols: 1
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: dp(6)
                    id: piper_model_grid

                # Export quality
                SettingSection:
                    title: 'Export Quality'

                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: dp(48)
                    spacing: dp(12)

                    Label:
                        text: 'Video Bitrate'
                        font_size: '14sp'
                        color: 0.8, 0.8, 1, 1

                    Spinner:
                        id: bitrate_spinner
                        text: '4000k'
                        values: ['1000k', '2000k', '4000k', '6000k', '8000k', '10000k']
                        size_hint_x: None
                        width: dp(110)
                        background_color: 0.18, 0.18, 0.28, 1
                        color: 1, 1, 1, 1
                        on_text: root.save_bitrate(self.text)

                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: dp(48)
                    spacing: dp(12)

                    Label:
                        text: 'Audio Quality'
                        font_size: '14sp'
                        color: 0.8, 0.8, 1, 1

                    Spinner:
                        id: audio_quality_spinner
                        text: '192k'
                        values: ['96k', '128k', '192k', '256k', '320k']
                        size_hint_x: None
                        width: dp(110)
                        background_color: 0.18, 0.18, 0.28, 1
                        color: 1, 1, 1, 1
                        on_text: root.save_audio_quality(self.text)

                # Performance
                SettingSection:
                    title: 'Performance'

                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: dp(48)
                    spacing: dp(12)

                    Label:
                        text: 'CPU Threads'
                        font_size: '14sp'
                        color: 0.8, 0.8, 1, 1

                    Spinner:
                        id: threads_spinner
                        text: '4'
                        values: ['1', '2', '4', '6', '8']
                        size_hint_x: None
                        width: dp(80)
                        background_color: 0.18, 0.18, 0.28, 1
                        color: 1, 1, 1, 1
                        on_text: root.save_threads(self.text)

                # Save button
                Button:
                    text: 'Save Settings'
                    size_hint_y: None
                    height: dp(52)
                    background_color: 0.25, 0.47, 0.95, 1
                    color: 1, 1, 1, 1
                    font_size: '15sp'
                    on_release: root.save_all()

<SettingSection@BoxLayout>:
    title: ''
    orientation: 'vertical'
    size_hint_y: None
    height: dp(36)

    Label:
        text: root.title
        font_size: '13sp'
        bold: True
        color: 0.4, 0.6, 1, 1
        halign: 'left'
        text_size: self.size
        valign: 'bottom'

    canvas.after:
        Color:
            rgba: 0.2, 0.2, 0.4, 1
        Line:
            points: self.x, self.y, self.right, self.y
            width: 1
""")

WHISPER_MODELS = [
    ("tiny.en (75MB, fastest)", "tiny.en"),
    ("base.en (142MB, fast)", "base.en"),
    ("small.en (466MB, balanced)", "small.en"),
    ("medium.en (1.5GB, accurate)", "medium.en"),
    ("tiny (multilingual, 75MB)", "tiny"),
    ("base (multilingual, 142MB)", "base"),
    ("small (multilingual, 466MB)", "small"),
]

PIPER_MODELS = [
    ("amy-medium (en-US, 63MB)", "en_US-amy-medium"),
    ("lessac-high (en-US, 63MB)", "en_US-lessac-high"),
    ("ryan-high (en-GB, 63MB)", "en_GB-ryan-high"),
    ("davefx-medium (es-ES, 63MB)", "es_ES-davefx-medium"),
    ("upmc-medium (fr-FR, 63MB)", "fr_FR-upmc-medium"),
    ("thorsten-high (de-DE, 63MB)", "de_DE-thorsten-high"),
]


class SettingsScreen(Screen):
    """App settings screen."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._pending_settings = {}

    def on_enter(self):
        from database.settings.settings_manager import SettingsManager
        settings = SettingsManager().load()

        app = App.get_running_app()
        self.ids.theme_btn.text = app.theme.capitalize()

        self.ids.bitrate_spinner.text = settings.get("video_bitrate", "4000k")
        self.ids.audio_quality_spinner.text = settings.get("audio_quality", "192k")
        self.ids.threads_spinner.text = str(settings.get("cpu_threads", 4))

        self._populate_whisper_models(settings.get("whisper_model", "base.en"))
        self._populate_piper_models(settings.get("piper_model", "en_US-amy-medium"))

    def _populate_whisper_models(self, current):
        grid = self.ids.whisper_model_grid
        grid.clear_widgets()
        from kivy.uix.button import Button
        for name, mid in WHISPER_MODELS:
            selected = current == mid
            btn = Button(
                text=name, size_hint_y=None, height="44dp",
                background_color=(0.25, 0.47, 0.95, 1) if selected else (0.18, 0.18, 0.28, 1),
                color=(1, 1, 1, 1), font_size="13sp",
            )
            btn.bind(on_release=lambda b, m=mid: self._select_whisper_model(m))
            grid.add_widget(btn)

    def _populate_piper_models(self, current):
        grid = self.ids.piper_model_grid
        grid.clear_widgets()
        from kivy.uix.button import Button
        for name, mid in PIPER_MODELS:
            selected = current == mid
            btn = Button(
                text=name, size_hint_y=None, height="44dp",
                background_color=(0.25, 0.47, 0.95, 1) if selected else (0.18, 0.18, 0.28, 1),
                color=(1, 1, 1, 1), font_size="13sp",
            )
            btn.bind(on_release=lambda b, m=mid: self._select_piper_model(m))
            grid.add_widget(btn)

    def _select_whisper_model(self, model_id):
        self._pending_settings["whisper_model"] = model_id
        self._populate_whisper_models(model_id)

    def _select_piper_model(self, model_id):
        self._pending_settings["piper_model"] = model_id
        self._populate_piper_models(model_id)

    def toggle_theme(self):
        App.get_running_app().toggle_theme()
        self.ids.theme_btn.text = App.get_running_app().theme.capitalize()

    def save_bitrate(self, val):
        self._pending_settings["video_bitrate"] = val

    def save_audio_quality(self, val):
        self._pending_settings["audio_quality"] = val

    def save_threads(self, val):
        self._pending_settings["cpu_threads"] = int(val)

    def save_all(self):
        from database.settings.settings_manager import SettingsManager
        mgr = SettingsManager()
        current = mgr.load()
        current.update(self._pending_settings)
        mgr.save(current)
        self._pending_settings = {}
        App.get_running_app().navigate_to("home")
