"""Progress card widget for showing processing step status."""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.graphics import Color, RoundedRectangle
from kivy.animation import Animation


class ProgressCard(BoxLayout):
    """
    A styled card that shows a processing step with:
    - Step name
    - Status icon (pending / running / done / error)
    - Optional progress bar
    """

    STATUS_ICONS = {
        "pending": "○",
        "running": "◉",
        "done":    "●",
        "error":   "✗",
    }
    STATUS_COLORS = {
        "pending": (0.4, 0.4, 0.6, 1),
        "running": (0.9, 0.8, 0.2, 1),
        "done":    (0.3, 0.9, 0.4, 1),
        "error":   (1, 0.3, 0.3, 1),
    }

    def __init__(self, step_name: str, show_progress: bool = False, **kwargs):
        super().__init__(orientation="vertical", size_hint_y=None, height=72,
                         padding=12, spacing=4, **kwargs)
        self._status = "pending"
        self._draw_bg()

        self._icon_lbl = Label(
            text=self.STATUS_ICONS["pending"],
            font_size="18sp",
            color=self.STATUS_COLORS["pending"],
            size_hint_x=None, width=28,
        )
        self._name_lbl = Label(
            text=step_name, font_size="13sp", color=(0.8, 0.8, 1, 1),
            halign="left", text_size=(None, None),
        )
        top_row = BoxLayout(orientation="horizontal", spacing=10,
                            size_hint_y=None, height=32)
        top_row.add_widget(self._icon_lbl)
        top_row.add_widget(self._name_lbl)
        self.add_widget(top_row)

        if show_progress:
            self._progress_bar = ProgressBar(max=100, value=0, size_hint_y=None, height=6)
            self.add_widget(self._progress_bar)
        else:
            self._progress_bar = None

    def _draw_bg(self):
        with self.canvas.before:
            Color(0.12, 0.12, 0.20, 1)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
        self.bind(pos=lambda i, v: setattr(self._bg, "pos", v))
        self.bind(size=lambda i, v: setattr(self._bg, "size", v))

    def set_status(self, status: str):
        """Update the status icon and color."""
        self._status = status
        self._icon_lbl.text = self.STATUS_ICONS.get(status, "○")
        self._icon_lbl.color = self.STATUS_COLORS.get(status, (0.4, 0.4, 0.6, 1))

        if status == "done":
            anim = Animation(opacity=0.7, duration=0.3) + Animation(opacity=1, duration=0.3)
            anim.start(self._name_lbl)

    def set_progress(self, value: float):
        """Update the progress bar (0–100)."""
        if self._progress_bar:
            self._progress_bar.value = value

    @property
    def status(self) -> str:
        return self._status
