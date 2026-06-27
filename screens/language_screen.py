"""Language selection screen."""

from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.app import App

Builder.load_string("""
<LanguageScreen>:
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
                on_release: app.navigate_to('video_picker')

            Label:
                text: 'Select Language'
                font_size: '18sp'
                bold: True
                color: 1, 1, 1, 1
                halign: 'left'
                text_size: self.size
                valign: 'center'

        Label:
            text: 'Source Language (video audio)'
            font_size: '14sp'
            bold: True
            color: 0.7, 0.7, 0.9, 1
            size_hint_y: None
            height: dp(44)
            halign: 'left'
            padding: dp(16), 0
            text_size: self.size

        ScrollView:
            size_hint_y: 0.4
            GridLayout:
                id: source_lang_grid
                cols: 2
                size_hint_y: None
                height: self.minimum_height
                padding: dp(12)
                spacing: dp(8)

        Label:
            text: 'Target Dubbing Language'
            font_size: '14sp'
            bold: True
            color: 0.7, 0.7, 0.9, 1
            size_hint_y: None
            height: dp(44)
            halign: 'left'
            padding: dp(16), 0
            text_size: self.size

        ScrollView:
            size_hint_y: 0.4
            GridLayout:
                id: target_lang_grid
                cols: 2
                size_hint_y: None
                height: self.minimum_height
                padding: dp(12)
                spacing: dp(8)

        Button:
            text: 'Continue to Voice Selection'
            size_hint_y: None
            height: dp(52)
            background_color: 0.25, 0.47, 0.95, 1
            color: 1, 1, 1, 1
            font_size: '15sp'
            on_release: root.continue_to_voice()
""")

LANGUAGES = [
    ("English", "en"),
    ("Spanish", "es"),
    ("French", "fr"),
    ("German", "de"),
    ("Italian", "it"),
    ("Portuguese", "pt"),
    ("Russian", "ru"),
    ("Japanese", "ja"),
    ("Chinese", "zh"),
    ("Korean", "ko"),
    ("Arabic", "ar"),
    ("Hindi", "hi"),
    ("Dutch", "nl"),
    ("Polish", "pl"),
    ("Turkish", "tr"),
    ("Vietnamese", "vi"),
]


class LanguageScreen(Screen):
    """Select source and target dubbing language."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._source_lang = "en"
        self._target_lang = "en"

    def on_enter(self):
        self._populate_grids()

    def _populate_grids(self):
        for grid_id, attr in [("source_lang_grid", "_source_lang"), ("target_lang_grid", "_target_lang")]:
            grid = self.ids[grid_id]
            grid.clear_widgets()
            for name, code in LANGUAGES:
                selected = getattr(self, attr) == code
                btn = self._lang_button(name, code, selected, attr)
                grid.add_widget(btn)

    def _lang_button(self, name, code, selected, attr):
        from kivy.uix.button import Button
        color = (0.25, 0.47, 0.95, 1) if selected else (0.18, 0.18, 0.28, 1)
        btn = Button(
            text=name,
            size_hint_y=None,
            height="44dp",
            background_color=color,
            color=(1, 1, 1, 1),
            font_size="13sp",
        )
        btn.bind(on_release=lambda b, c=code, a=attr: self._select_lang(c, a))
        return btn

    def _select_lang(self, code, attr):
        setattr(self, attr, code)
        self._populate_grids()

    def continue_to_voice(self):
        app = App.get_running_app()
        app.set_project_data("source_lang", self._source_lang)
        app.set_project_data("target_lang", self._target_lang)
        app.navigate_to("voice")
