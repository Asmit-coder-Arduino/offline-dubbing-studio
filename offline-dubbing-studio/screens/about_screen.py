"""About screen — app version, credits, and model info."""

from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.app import App

Builder.load_string("""
<AboutScreen>:
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
                text: 'About'
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
                padding: dp(20)
                spacing: dp(20)

                Image:
                    source: 'assets/icons/app_icon.png'
                    size_hint: None, None
                    size: dp(80), dp(80)
                    pos_hint: {'center_x': 0.5}

                Label:
                    text: 'Offline Video Dubbing Studio'
                    font_size: '20sp'
                    bold: True
                    color: 1, 1, 1, 1
                    halign: 'center'
                    size_hint_y: None
                    height: dp(36)

                Label:
                    text: 'Version 1.0.0'
                    font_size: '14sp'
                    color: 0.5, 0.5, 0.7, 1
                    halign: 'center'
                    size_hint_y: None
                    height: dp(28)

                Label:
                    text: 'A fully offline AI-powered video dubbing app.\\nDub any video in any language without an internet connection.'
                    font_size: '13sp'
                    color: 0.7, 0.7, 0.9, 1
                    halign: 'center'
                    text_size: self.width, None
                    size_hint_y: None
                    height: self.texture_size[1]

                # Tech stack
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                    padding: dp(16)
                    spacing: dp(10)
                    canvas.before:
                        Color:
                            rgba: 0.12, 0.12, 0.20, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(12)]

                    Label:
                        text: 'Technology Stack'
                        font_size: '15sp'
                        bold: True
                        color: 0.4, 0.6, 1, 1
                        halign: 'left'
                        text_size: self.size
                        size_hint_y: None
                        height: dp(28)

                    Label:
                        text: '[b]Speech Recognition:[/b] OpenAI Whisper.cpp (offline)'
                        markup: True
                        font_size: '13sp'
                        color: 0.8, 0.8, 1, 1
                        halign: 'left'
                        text_size: self.size
                        size_hint_y: None
                        height: dp(26)

                    Label:
                        text: '[b]Text-to-Speech:[/b] Piper TTS (offline, neural)'
                        markup: True
                        font_size: '13sp'
                        color: 0.8, 0.8, 1, 1
                        halign: 'left'
                        text_size: self.size
                        size_hint_y: None
                        height: dp(26)

                    Label:
                        text: '[b]Video Processing:[/b] FFmpeg'
                        markup: True
                        font_size: '13sp'
                        color: 0.8, 0.8, 1, 1
                        halign: 'left'
                        text_size: self.size
                        size_hint_y: None
                        height: dp(26)

                    Label:
                        text: '[b]UI Framework:[/b] Kivy 2.3'
                        markup: True
                        font_size: '13sp'
                        color: 0.8, 0.8, 1, 1
                        halign: 'left'
                        text_size: self.size
                        size_hint_y: None
                        height: dp(26)

                    Label:
                        text: '[b]Language:[/b] Python 3.10+'
                        markup: True
                        font_size: '13sp'
                        color: 0.8, 0.8, 1, 1
                        halign: 'left'
                        text_size: self.size
                        size_hint_y: None
                        height: dp(26)

                Label:
                    text: 'No internet connection required after installation.\\nAll AI models run locally on your device.'
                    font_size: '13sp'
                    color: 0.4, 0.8, 0.4, 1
                    halign: 'center'
                    text_size: self.width, None
                    size_hint_y: None
                    height: self.texture_size[1]

                Label:
                    text: '© 2024 Offline Dubbing Studio'
                    font_size: '12sp'
                    color: 0.4, 0.4, 0.5, 1
                    halign: 'center'
                    size_hint_y: None
                    height: dp(36)
""")


class AboutScreen(Screen):
    """About / credits screen."""
    pass
