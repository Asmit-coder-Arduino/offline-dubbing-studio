"""Subtitle segment item widget for the editor list."""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle


class SubtitleItem(BoxLayout):
    """
    An editable subtitle segment row consisting of:
    - Index label
    - Start / end time inputs
    - Text input
    - Delete button
    """

    def __init__(self, segment, on_delete=None, on_change=None, **kwargs):
        super().__init__(orientation="vertical", size_hint_y=None, height=120,
                         padding=8, spacing=4, **kwargs)
        self.segment = segment
        self.on_delete = on_delete
        self.on_change = on_change
        self._draw_bg()
        self._build_ui()

    def _draw_bg(self):
        with self.canvas.before:
            Color(0.13, 0.13, 0.20, 1)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
        self.bind(pos=lambda i, v: setattr(self._bg, "pos", v))
        self.bind(size=lambda i, v: setattr(self._bg, "size", v))

    def _build_ui(self):
        # Time row
        time_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=36, spacing=6)

        index_lbl = Label(
            text=f"#{self.segment.index}",
            font_size="11sp", color=(0.4, 0.6, 1, 1),
            size_hint_x=None, width=30,
        )
        self._start_in = TextInput(
            text=f"{self.segment.start:.2f}", multiline=False, font_size="12sp",
            background_color=(0.18, 0.18, 0.28, 1), foreground_color=(1, 1, 1, 1),
            size_hint_x=None, width=72,
        )
        arrow_lbl = Label(
            text="→", font_size="14sp", color=(0.5, 0.5, 0.7, 1),
            size_hint_x=None, width=22,
        )
        self._end_in = TextInput(
            text=f"{self.segment.end:.2f}", multiline=False, font_size="12sp",
            background_color=(0.18, 0.18, 0.28, 1), foreground_color=(1, 1, 1, 1),
            size_hint_x=None, width=72,
        )
        del_btn = Button(
            text="✕", size_hint_x=None, width=32,
            background_color=(0.7, 0.2, 0.2, 1), color=(1, 1, 1, 1), font_size="14sp",
        )
        del_btn.bind(on_release=lambda b: self._on_delete())

        self._start_in.bind(text=self._on_start_change)
        self._end_in.bind(text=self._on_end_change)

        time_row.add_widget(index_lbl)
        time_row.add_widget(self._start_in)
        time_row.add_widget(arrow_lbl)
        time_row.add_widget(self._end_in)
        time_row.add_widget(del_btn)

        # Text input
        self._text_in = TextInput(
            text=self.segment.text, multiline=True, font_size="13sp",
            background_color=(0.10, 0.12, 0.20, 1), foreground_color=(1, 1, 1, 1),
        )
        self._text_in.bind(text=self._on_text_change)

        self.add_widget(time_row)
        self.add_widget(self._text_in)

    def _on_start_change(self, widget, value):
        try:
            self.segment.start = float(value)
            if self.on_change:
                self.on_change(self.segment)
        except ValueError:
            pass

    def _on_end_change(self, widget, value):
        try:
            self.segment.end = float(value)
            if self.on_change:
                self.on_change(self.segment)
        except ValueError:
            pass

    def _on_text_change(self, widget, value):
        self.segment.text = value
        if self.on_change:
            self.on_change(self.segment)

    def _on_delete(self):
        if self.on_delete:
            self.on_delete(self.segment)

    def refresh(self):
        """Sync widget display from the underlying segment data."""
        self._start_in.text = f"{self.segment.start:.2f}"
        self._end_in.text = f"{self.segment.end:.2f}"
        self._text_in.text = self.segment.text
