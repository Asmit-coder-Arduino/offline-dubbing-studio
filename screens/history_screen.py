"""History screen — view past dubbing projects."""

import os
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

Builder.load_string("""
<HistoryScreen>:
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
                text: 'History'
                font_size: '18sp'
                bold: True
                color: 1, 1, 1, 1
                halign: 'left'
                text_size: self.size
                valign: 'center'

            Button:
                text: 'Clear All'
                size_hint_x: None
                width: dp(80)
                background_color: 0.6, 0.2, 0.2, 1
                color: 1, 1, 1, 1
                font_size: '12sp'
                on_release: root.clear_history()

        ScrollView:
            BoxLayout:
                id: history_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(12)
                spacing: dp(10)
""")


class HistoryScreen(Screen):
    """Shows all past dubbing jobs."""

    def on_enter(self):
        self._load_history()

    def _load_history(self):
        from database.history.history_manager import HistoryManager
        entries = HistoryManager().get_all()
        container = self.ids.history_list
        container.clear_widgets()

        if not entries:
            lbl = Label(
                text="No history yet. Complete your first dubbing project.",
                color=(0.4, 0.4, 0.5, 1),
                font_size="14sp",
                size_hint_y=None,
                height="60dp",
                halign="center",
            )
            container.add_widget(lbl)
            return

        for entry in reversed(entries):
            card = self._build_card(entry)
            container.add_widget(card)

    def _build_card(self, entry):
        card = BoxLayout(orientation="vertical", size_hint_y=None, height=120, padding=12, spacing=6)
        with card.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.13, 0.13, 0.20, 1)
            card._bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[8])
        card.bind(pos=lambda i, v: setattr(i._bg, "pos", v))
        card.bind(size=lambda i, v: setattr(i._bg, "size", v))

        name_lbl = Label(
            text=os.path.basename(entry.get("input", "Unknown")),
            font_size="14sp", bold=True, color=(1, 1, 1, 1),
            halign="left", text_size=(None, None),
            size_hint_y=None, height=28,
        )
        info_lbl = Label(
            text=(f"{entry.get('source_lang','?')} → {entry.get('target_lang','?')} | "
                  f"{entry.get('segments', 0)} segments | {entry.get('date','')}"),
            font_size="12sp", color=(0.5, 0.5, 0.7, 1),
            halign="left", text_size=(None, None),
            size_hint_y=None, height=24,
        )
        out_lbl = Label(
            text=entry.get("output", ""),
            font_size="11sp", color=(0.4, 0.6, 0.4, 1),
            halign="left", text_size=(None, None),
            size_hint_y=None, height=22,
        )

        row = BoxLayout(orientation="horizontal", size_hint_y=None, height=36, spacing=8)
        exists = os.path.exists(entry.get("output", ""))
        share_btn = Button(
            text="Share" if exists else "Missing",
            size_hint_x=None, width=80,
            background_color=(0.3, 0.5, 0.9, 1) if exists else (0.4, 0.4, 0.4, 1),
            color=(1, 1, 1, 1), font_size="12sp", disabled=not exists,
        )
        share_btn.bind(on_release=lambda b, e=entry: self._share(e))

        row.add_widget(share_btn)

        card.add_widget(name_lbl)
        card.add_widget(info_lbl)
        card.add_widget(out_lbl)
        card.add_widget(row)
        return card

    def _share(self, entry):
        App.get_running_app().set_project_data("output_path", entry.get("output", ""))
        App.get_running_app().navigate_to("export")

    def clear_history(self):
        from database.history.history_manager import HistoryManager
        HistoryManager().clear_all()
        self._load_history()
