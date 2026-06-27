"""Export screen — show final output and sharing options."""

import os
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.app import App

Builder.load_string("""
<ExportScreen>:
    canvas.before:
        Color:
            rgba: 0.07, 0.07, 0.10, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(20)

        Label:
            text: 'Export Complete!'
            font_size: '24sp'
            bold: True
            color: 0.3, 0.9, 0.5, 1
            size_hint_y: None
            height: dp(50)
            halign: 'center'

        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: dp(180)
            padding: dp(16)
            spacing: dp(12)
            canvas.before:
                Color:
                    rgba: 0.10, 0.18, 0.12, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(12)]

            Label:
                text: 'Output File'
                font_size: '13sp'
                color: 0.5, 0.8, 0.6, 1
                halign: 'left'
                text_size: self.size

            Label:
                id: output_path_label
                text: 'Loading...'
                font_size: '14sp'
                bold: True
                color: 0.9, 1, 0.9, 1
                halign: 'left'
                text_size: self.size

            Label:
                id: file_size_label
                text: ''
                font_size: '12sp'
                color: 0.5, 0.7, 0.5, 1
                halign: 'left'
                text_size: self.size

            Label:
                id: video_info_label
                text: ''
                font_size: '12sp'
                color: 0.5, 0.7, 0.5, 1
                halign: 'left'
                text_size: self.size

        Label:
            text: 'Actions'
            font_size: '16sp'
            bold: True
            color: 0.8, 0.8, 1, 1
            size_hint_y: None
            height: dp(36)
            halign: 'left'
            text_size: self.size

        GridLayout:
            cols: 2
            size_hint_y: None
            height: dp(160)
            spacing: dp(12)

            Button:
                text: 'Share Video'
                background_color: 0.3, 0.5, 0.9, 1
                color: 1, 1, 1, 1
                on_release: root.share_video()

            Button:
                text: 'Open Folder'
                background_color: 0.25, 0.35, 0.55, 1
                color: 1, 1, 1, 1
                on_release: root.open_folder()

            Button:
                text: 'New Project'
                background_color: 0.2, 0.5, 0.3, 1
                color: 1, 1, 1, 1
                on_release: root.new_project()

            Button:
                text: 'View History'
                background_color: 0.35, 0.25, 0.55, 1
                color: 1, 1, 1, 1
                on_release: app.navigate_to('history')

        Widget:

        Button:
            text: 'Back to Home'
            size_hint_y: None
            height: dp(52)
            background_color: 0.18, 0.18, 0.28, 1
            color: 0.8, 0.8, 1, 1
            font_size: '15sp'
            on_release: app.navigate_to('home')
""")


class ExportScreen(Screen):
    """Shows the finished export with sharing options."""

    def on_enter(self):
        app = App.get_running_app()
        output_path = app.get_project_data("output_path", "")
        self.ids.output_path_label.text = output_path or "No output file found."

        if output_path and os.path.exists(output_path):
            size = os.path.getsize(output_path)
            self.ids.file_size_label.text = f"File size: {self._human_size(size)}"
            try:
                from utils.ffmpeg.ffmpeg_utils import FFmpegUtils
                duration = FFmpegUtils.get_duration(output_path)
                self.ids.video_info_label.text = f"Duration: {int(duration)}s"
            except Exception:
                self.ids.video_info_label.text = ""
        else:
            self.ids.file_size_label.text = ""
            self.ids.video_info_label.text = ""

    def share_video(self):
        app = App.get_running_app()
        output_path = app.get_project_data("output_path", "")
        if not output_path or not os.path.exists(output_path):
            return
        try:
            from kivy.utils import platform
            if platform == "android":
                from jnius import autoclass
                Intent = autoclass("android.content.Intent")
                Uri = autoclass("android.net.Uri")
                File = autoclass("java.io.File")
                intent = Intent(Intent.ACTION_SEND)
                intent.setType("video/mp4")
                uri = Uri.fromFile(File(output_path))
                intent.putExtra(Intent.EXTRA_STREAM, uri)
                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                PythonActivity.mActivity.startActivity(Intent.createChooser(intent, "Share Video"))
        except Exception as e:
            print(f"Share error: {e}")

    def open_folder(self):
        app = App.get_running_app()
        folder = app.get_export_dir()
        try:
            from kivy.utils import platform
            if platform == "android":
                from jnius import autoclass
                Intent = autoclass("android.content.Intent")
                Uri = autoclass("android.net.Uri")
                intent = Intent(Intent.ACTION_VIEW)
                intent.setDataAndType(Uri.parse(f"file://{folder}"), "resource/folder")
                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                PythonActivity.mActivity.startActivity(intent)
        except Exception as e:
            print(f"Open folder error: {e}")

    def new_project(self):
        App.get_running_app().clear_project()
        App.get_running_app().navigate_to("video_picker")

    @staticmethod
    def _human_size(n):
        for unit in ("B", "KB", "MB", "GB"):
            if n < 1024:
                return f"{n:.1f} {unit}"
            n /= 1024
        return f"{n:.1f} TB"
