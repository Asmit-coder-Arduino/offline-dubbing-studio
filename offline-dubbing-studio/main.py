"""
Offline Video Dubbing Studio
Entry point for the Kivy Android application.
"""

import os
import sys

os.environ.setdefault("KIVY_NO_ENV_CONFIG", "1")

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.utils import platform
from kivy.clock import Clock

from screens.splash_screen import SplashScreen
from screens.home_screen import HomeScreen
from screens.video_picker_screen import VideoPickerScreen
from screens.language_screen import LanguageScreen
from screens.voice_screen import VoiceScreen
from screens.subtitle_editor_screen import SubtitleEditorScreen
from screens.processing_screen import ProcessingScreen
from screens.export_screen import ExportScreen
from screens.settings_screen import SettingsScreen
from screens.history_screen import HistoryScreen
from screens.about_screen import AboutScreen

from database.settings.settings_manager import SettingsManager
from database.db_manager import DatabaseManager


class DubbingApp(App):
    """Main application class for Offline Video Dubbing Studio."""

    title = "Offline Video Dubbing Studio"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings_manager = SettingsManager()
        self.db_manager = DatabaseManager()
        self.current_project = {}
        self.theme = "dark"

    def build(self):
        self.db_manager.initialize()
        settings = self.settings_manager.load()
        self.theme = settings.get("theme", "dark")
        self._apply_theme()

        self.sm = ScreenManager(transition=FadeTransition(duration=0.3))
        self.sm.add_widget(SplashScreen(name="splash"))
        self.sm.add_widget(HomeScreen(name="home"))
        self.sm.add_widget(VideoPickerScreen(name="video_picker"))
        self.sm.add_widget(LanguageScreen(name="language"))
        self.sm.add_widget(VoiceScreen(name="voice"))
        self.sm.add_widget(SubtitleEditorScreen(name="subtitle_editor"))
        self.sm.add_widget(ProcessingScreen(name="processing"))
        self.sm.add_widget(ExportScreen(name="export"))
        self.sm.add_widget(SettingsScreen(name="settings"))
        self.sm.add_widget(HistoryScreen(name="history"))
        self.sm.add_widget(AboutScreen(name="about"))

        if platform == "android":
            self._request_android_permissions()

        return self.sm

    def _apply_theme(self):
        if self.theme == "dark":
            Window.clearcolor = (0.07, 0.07, 0.10, 1)
        else:
            Window.clearcolor = (0.96, 0.96, 0.98, 1)

    def _request_android_permissions(self):
        try:
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.RECORD_AUDIO,
                Permission.CAMERA,
            ])
        except ImportError:
            pass

    def navigate_to(self, screen_name):
        self.sm.current = screen_name

    def set_project_data(self, key, value):
        self.current_project[key] = value

    def get_project_data(self, key, default=None):
        return self.current_project.get(key, default)

    def clear_project(self):
        self.current_project = {}

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self._apply_theme()
        self.settings_manager.save({"theme": self.theme})

    def on_pause(self):
        return True

    def on_resume(self):
        pass

    def get_app_dir(self):
        if platform == "android":
            try:
                from android.storage import app_storage_path
                return app_storage_path()
            except ImportError:
                pass
        return os.path.dirname(os.path.abspath(__file__))

    def get_export_dir(self):
        if platform == "android":
            try:
                from android.storage import primary_external_storage_path
                path = os.path.join(primary_external_storage_path(), "Movies", "OfflineDubber")
            except ImportError:
                path = os.path.join(os.path.expanduser("~"), "Movies", "OfflineDubber")
        else:
            path = os.path.join(os.path.expanduser("~"), "OfflineDubber_Exports")
        os.makedirs(path, exist_ok=True)
        return path


if __name__ == "__main__":
    DubbingApp().run()
