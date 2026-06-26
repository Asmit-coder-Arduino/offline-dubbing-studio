"""Video picker screen — browse and select a video file."""

import os
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.utils import platform

Builder.load_string("""
<VideoPickerScreen>:
    canvas.before:
        Color:
            rgba: 0.07, 0.07, 0.10, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'

        # App bar
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
                text: 'Select Video'
                font_size: '18sp'
                bold: True
                color: 1, 1, 1, 1
                halign: 'left'
                text_size: self.size
                valign: 'center'

        # Current path breadcrumb
        BoxLayout:
            size_hint_y: None
            height: dp(40)
            padding: dp(12), dp(4)
            canvas.before:
                Color:
                    rgba: 0.10, 0.10, 0.18, 1
                Rectangle:
                    pos: self.pos
                    size: self.size

            Label:
                id: path_label
                text: 'Storage'
                font_size: '12sp'
                color: 0.6, 0.6, 0.8, 1
                halign: 'left'
                text_size: self.size
                valign: 'center'

        # Filter bar
        BoxLayout:
            size_hint_y: None
            height: dp(44)
            padding: dp(8), dp(4)
            spacing: dp(8)
            canvas.before:
                Color:
                    rgba: 0.07, 0.07, 0.10, 1
                Rectangle:
                    pos: self.pos
                    size: self.size

            Button:
                id: btn_all
                text: 'All Videos'
                size_hint_x: None
                width: dp(90)
                background_color: 0.25, 0.47, 0.95, 1
                color: 1, 1, 1, 1
                font_size: '12sp'
                on_release: root.filter_files('all')

            Button:
                text: 'MP4'
                size_hint_x: None
                width: dp(60)
                background_color: 0.18, 0.18, 0.28, 1
                color: 0.8, 0.8, 1, 1
                font_size: '12sp'
                on_release: root.filter_files('mp4')

            Button:
                text: 'MKV'
                size_hint_x: None
                width: dp(60)
                background_color: 0.18, 0.18, 0.28, 1
                color: 0.8, 0.8, 1, 1
                font_size: '12sp'
                on_release: root.filter_files('mkv')

            Button:
                text: 'Other'
                size_hint_x: None
                width: dp(60)
                background_color: 0.18, 0.18, 0.28, 1
                color: 0.8, 0.8, 1, 1
                font_size: '12sp'
                on_release: root.filter_files('other')

        # File list
        ScrollView:
            GridLayout:
                id: file_list
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                padding: dp(8)
                spacing: dp(6)

        # Selected video preview bar
        BoxLayout:
            id: selection_bar
            size_hint_y: None
            height: dp(64)
            padding: dp(12), dp(8)
            spacing: dp(12)
            opacity: 0
            canvas.before:
                Color:
                    rgba: 0.10, 0.15, 0.25, 1
                Rectangle:
                    pos: self.pos
                    size: self.size

            Label:
                id: selected_label
                text: 'No file selected'
                font_size: '13sp'
                color: 0.8, 0.9, 1, 1
                halign: 'left'
                text_size: self.size
                valign: 'center'

            Button:
                text: 'Continue'
                size_hint_x: None
                width: dp(100)
                background_color: 0.25, 0.47, 0.95, 1
                color: 1, 1, 1, 1
                on_release: root.continue_to_language()
""")

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".3gp", ".flv"}


class VideoPickerScreen(Screen):
    """File browser for selecting video files from device storage."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._current_path = "/"
        self._all_entries = []
        self._selected_file = None
        self._filter = "all"

    def on_enter(self):
        self._selected_file = None
        self.ids.selection_bar.opacity = 0
        Clock.schedule_once(lambda dt: self._load_storage_root(), 0.1)

    def _load_storage_root(self):
        if platform == "android":
            try:
                from android.storage import primary_external_storage_path
                root = primary_external_storage_path()
            except Exception:
                root = "/sdcard"
        else:
            root = os.path.expanduser("~")
        self._navigate_to(root)

    def _navigate_to(self, path):
        self._current_path = path
        self.ids.path_label.text = path
        try:
            entries = sorted(os.listdir(path))
        except PermissionError:
            entries = []

        self._all_entries = []
        for name in entries:
            full = os.path.join(path, name)
            if os.path.isdir(full):
                self._all_entries.append({"name": name, "path": full, "type": "dir"})
            else:
                ext = os.path.splitext(name)[1].lower()
                if ext in VIDEO_EXTENSIONS:
                    size = self._human_size(os.path.getsize(full))
                    self._all_entries.append({
                        "name": name, "path": full, "type": "file", "size": size, "ext": ext,
                    })

        self._render_entries()

    def _render_entries(self):
        container = self.ids.file_list
        container.clear_widgets()

        ext_filter = self._filter
        entries = []
        if self._current_path != "/":
            entries.append({"name": ".. (Go Up)", "path": os.path.dirname(self._current_path), "type": "up"})

        for e in self._all_entries:
            if e["type"] == "dir":
                entries.append(e)
            elif ext_filter == "all":
                entries.append(e)
            elif ext_filter == "other":
                if e["ext"] not in {".mp4", ".mkv"}:
                    entries.append(e)
            elif e["ext"] == "." + ext_filter:
                entries.append(e)

        for entry in entries:
            btn = self._make_entry_button(entry)
            container.add_widget(btn)

        if not entries:
            lbl = Label(
                text="No video files found in this folder.",
                color=(0.5, 0.5, 0.6, 1),
                font_size="13sp",
                size_hint_y=None,
                height="48dp",
            )
            container.add_widget(lbl)

    def _make_entry_button(self, entry):
        is_dir = entry["type"] in ("dir", "up")
        icon = "[D]" if is_dir else "[V]"
        subtitle = "" if is_dir else entry.get("size", "")

        layout = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height="64dp",
            padding="8dp",
            spacing="2dp",
        )
        with layout.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.13, 0.13, 0.20, 1)
            layout._bg = RoundedRectangle(pos=layout.pos, size=layout.size, radius=[8])
        layout.bind(pos=lambda i, v: setattr(i._bg, "pos", v))
        layout.bind(size=lambda i, v: setattr(i._bg, "size", v))

        row = BoxLayout(orientation="horizontal", spacing="12dp")
        icon_lbl = Label(text=icon, font_size="18sp", color=(0.4, 0.6, 1, 1),
                         size_hint_x=None, width="36dp")
        name_box = BoxLayout(orientation="vertical")
        name_lbl = Label(text=entry["name"], font_size="14sp", color=(1, 1, 1, 1),
                         halign="left", text_size=(None, None))
        name_box.add_widget(name_lbl)
        if subtitle:
            sub_lbl = Label(text=subtitle, font_size="11sp", color=(0.5, 0.5, 0.7, 1),
                            halign="left", text_size=(None, None))
            name_box.add_widget(sub_lbl)
        row.add_widget(icon_lbl)
        row.add_widget(name_box)
        layout.add_widget(row)

        btn = Button(
            size_hint=(1, None),
            height="64dp",
            background_color=(0, 0, 0, 0),
            opacity=0,
        )
        btn.bind(on_release=lambda b, e=entry: self._on_entry_tap(e))

        stack = BoxLayout(size_hint_y=None, height="64dp")
        stack.add_widget(layout)
        stack.add_widget(btn)
        return stack

    def _on_entry_tap(self, entry):
        if entry["type"] in ("dir", "up"):
            self._navigate_to(entry["path"])
        else:
            self._selected_file = entry["path"]
            self.ids.selected_label.text = entry["name"]
            self.ids.selection_bar.opacity = 1

    def filter_files(self, f):
        self._filter = f
        self._render_entries()

    def continue_to_language(self):
        if not self._selected_file:
            return
        app = App.get_running_app()
        app.set_project_data("video_path", self._selected_file)
        app.navigate_to("language")

    @staticmethod
    def _human_size(n):
        for unit in ("B", "KB", "MB", "GB"):
            if n < 1024:
                return f"{n:.1f} {unit}"
            n /= 1024
        return f"{n:.1f} TB"
