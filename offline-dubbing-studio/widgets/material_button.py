"""Material Design-inspired button widget for Kivy."""

from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Ellipse
from kivy.animation import Animation
from kivy.metrics import dp


class MaterialButton(Button):
    """
    A styled button with:
    - Rounded corners
    - Ripple-like press animation
    - Configurable primary / secondary / danger variants
    """

    VARIANTS = {
        "primary":   {"bg": (0.25, 0.47, 0.95, 1), "text": (1, 1, 1, 1)},
        "secondary": {"bg": (0.18, 0.18, 0.28, 1), "text": (0.8, 0.8, 1, 1)},
        "danger":    {"bg": (0.75, 0.18, 0.18, 1), "text": (1, 1, 1, 1)},
        "success":   {"bg": (0.18, 0.58, 0.28, 1), "text": (1, 1, 1, 1)},
    }

    def __init__(self, variant: str = "primary", radius: float = 8, **kwargs):
        super().__init__(**kwargs)
        self._variant = variant
        self._radius = radius
        colors = self.VARIANTS.get(variant, self.VARIANTS["primary"])
        self._bg_color = colors["bg"]
        self.color = colors["text"]
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ""
        self.background_down = ""
        self._draw_bg()

    def _draw_bg(self):
        with self.canvas.before:
            self._color_instr = Color(*self._bg_color)
            self._rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(self._radius)]
            )
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size

    def on_press(self):
        """Darken briefly on press."""
        r, g, b, a = self._bg_color
        darkened = (max(0, r - 0.08), max(0, g - 0.08), max(0, b - 0.08), a)
        self._color_instr.rgba = darkened

    def on_release(self):
        """Restore original color on release."""
        anim = Animation(rgba=self._bg_color, duration=0.15)
        anim.start(self._color_instr)
