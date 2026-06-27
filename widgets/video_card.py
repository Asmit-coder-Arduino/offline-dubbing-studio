"""
Reusable video card widgets for lists and history views.
"""

import os
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle


class ProjectHistoryCard(BoxLayout):
    """A card widget showing a past dubbing project in the history list."""

    def __init__(self, entry: dict, **kwargs):
        super().__init__(orientation="vertical", size_hint_y=None, height=100,
                         padding=12, spacing=6, **kwargs)
        self.entry = entry
        self._draw_bg()
        self._build_ui()

    def _draw_bg(self):
        with self.canvas.before:
            Color(0.13, 0.13, 0.20, 1)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
        self.bind(pos=lambda i, v: setattr(self._bg, "pos", v))
        self.bind(size=lambda i, v: setattr(self._bg, "size", v))

    def _build_ui(self):
        name = os.path.basename(self.entry.get("input", "Unknown"))
        langs = f"{self.entry.get('source_lang','?')} → {self.entry.get('target_lang','?')}"
        date = self.entry.get("date", "")
        out = self.entry.get("output", "")
        exists = os.path.exists(out)

        name_lbl = Label(
            text=name, font_size="14sp", bold=True, color=(1, 1, 1, 1),
            halign="left", text_size=(None, None), size_hint_y=None, height=26,
        )
        info_lbl = Label(
            text=f"{langs} | {date}", font_size="12sp", color=(0.5, 0.5, 0.7, 1),
            halign="left", text_size=(None, None), size_hint_y=None, height=22,
        )
        row = BoxLayout(orientation="horizontal", size_hint_y=None, height=34, spacing=8)
        status_lbl = Label(
            text="✓ Available" if exists else "✗ Missing",
            font_size="12sp",
            color=(0.3, 0.9, 0.4, 1) if exists else (0.8, 0.3, 0.3, 1),
        )
        open_btn = Button(
            text="Open",
            size_hint_x=None, width=70,
            background_color=(0.3, 0.5, 0.9, 1) if exists else (0.3, 0.3, 0.4, 1),
            color=(1, 1, 1, 1), font_size="12sp", disabled=not exists,
        )
        open_btn.bind(on_release=lambda b: self._open_entry())
        row.add_widget(status_lbl)
        row.add_widget(open_btn)

        self.add_widget(name_lbl)
        self.add_widget(info_lbl)
        self.add_widget(row)

    def _open_entry(self):
        from kivy.app import App
        app = App.get_running_app()
        app.set_project_data("output_path", self.entry.get("output", ""))
        app.navigate_to("export")


class VideoListCard(BoxLayout):
    """Compact card for a video file in the picker list."""

    def __init__(self, name: str, path: str, size_str: str = "", **kwargs):
        super().__init__(orientation="horizontal", size_hint_y=None, height=64,
                         padding=10, spacing=10, **kwargs)
        self.path = path
        self._draw_bg()
        self._build_ui(name, size_str)

    def _draw_bg(self):
        with self.canvas.before:
            Color(0.13, 0.13, 0.20, 1)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
        self.bind(pos=lambda i, v: setattr(self._bg, "pos", v))
        self.bind(size=lambda i, v: setattr(self._bg, "size", v))

    def _build_ui(self, name, size_str):
        icon_lbl = Label(
            text="[V]", font_size="20sp", color=(0.4, 0.6, 1, 1),
            size_hint_x=None, width=36,
        )
        info_box = BoxLayout(orientation="vertical")
        name_lbl = Label(
            text=name, font_size="14sp", color=(1, 1, 1, 1),
            halign="left", text_size=(None, None),
        )
        size_lbl = Label(
            text=size_str, font_size="11sp", color=(0.5, 0.5, 0.7, 1),
            halign="left", text_size=(None, None),
        )
        info_box.add_widget(name_lbl)
        if size_str:
            info_box.add_widget(size_lbl)
        self.add_widget(icon_lbl)
        self.add_widget(info_box)
