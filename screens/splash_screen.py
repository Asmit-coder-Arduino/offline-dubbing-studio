"""Splash screen shown at application startup."""

from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.lang import Builder

Builder.load_string("""
<SplashScreen>:
    canvas.before:
        Color:
            rgba: 0.07, 0.07, 0.10, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'
        padding: dp(40)
        spacing: dp(20)

        Widget:
            size_hint_y: 0.3

        Image:
            id: logo
            source: 'assets/icons/app_icon.png'
            size_hint: None, None
            size: dp(120), dp(120)
            pos_hint: {'center_x': 0.5}
            opacity: 0

        Label:
            id: title_label
            text: 'Offline Video Dubbing Studio'
            font_size: '24sp'
            bold: True
            color: 1, 1, 1, 1
            opacity: 0
            halign: 'center'

        Label:
            id: subtitle_label
            text: 'AI-Powered • Fully Offline • Professional'
            font_size: '14sp'
            color: 0.6, 0.6, 0.8, 1
            opacity: 0
            halign: 'center'

        Widget:
            size_hint_y: 0.1

        ProgressBar:
            id: progress_bar
            max: 100
            value: 0
            size_hint_x: 0.7
            pos_hint: {'center_x': 0.5}
            height: dp(4)
            size_hint_y: None

        Label:
            id: status_label
            text: 'Initializing...'
            font_size: '12sp'
            color: 0.5, 0.5, 0.7, 1
            halign: 'center'

        Widget:
            size_hint_y: 0.2
""")


class SplashScreen(Screen):
    """Animated splash screen with progress indicator."""

    def on_enter(self):
        self._animate_logo()
        Clock.schedule_once(self._start_loading, 0.5)

    def _animate_logo(self):
        logo = self.ids.logo
        title = self.ids.title_label
        subtitle = self.ids.subtitle_label

        anim_logo = Animation(opacity=1, duration=0.8)
        anim_logo.start(logo)

        Clock.schedule_once(lambda dt: Animation(opacity=1, duration=0.6).start(title), 0.3)
        Clock.schedule_once(lambda dt: Animation(opacity=1, duration=0.6).start(subtitle), 0.6)

    def _start_loading(self, dt):
        self._run_initialization()

    def _run_initialization(self):
        steps = [
            (10, "Initializing database..."),
            (25, "Loading AI models..."),
            (45, "Setting up FFmpeg..."),
            (65, "Configuring speech engine..."),
            (80, "Loading TTS engine..."),
            (95, "Almost ready..."),
            (100, "Ready!"),
        ]
        for i, (progress, status) in enumerate(steps):
            delay = 0.3 * i
            Clock.schedule_once(
                lambda dt, p=progress, s=status: self._update_progress(p, s),
                delay,
            )
        Clock.schedule_once(self._go_to_home, 0.3 * len(steps) + 0.5)

    def _update_progress(self, progress, status):
        self.ids.progress_bar.value = progress
        self.ids.status_label.text = status

    def _go_to_home(self, dt):
        self.manager.current = "home"
