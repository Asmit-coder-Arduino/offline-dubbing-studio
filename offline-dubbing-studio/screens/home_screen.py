"""Home screen — main dashboard of the application."""

from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.app import App

Builder.load_string("""
<HomeScreen>:
    canvas.before:
        Color:
            rgba: 0.07, 0.07, 0.10, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'
        spacing: 0

        # Top App Bar
        BoxLayout:
            size_hint_y: None
            height: dp(56)
            padding: dp(16), dp(8)
            spacing: dp(8)
            canvas.before:
                Color:
                    rgba: 0.10, 0.10, 0.15, 1
                Rectangle:
                    pos: self.pos
                    size: self.size

            Label:
                text: 'Dubbing Studio'
                font_size: '20sp'
                bold: True
                color: 1, 1, 1, 1
                halign: 'left'
                text_size: self.size
                valign: 'center'

            Button:
                text: '[Settings]'
                size_hint_x: None
                width: dp(90)
                background_color: 0, 0, 0, 0
                color: 0.6, 0.8, 1, 1
                on_release: app.navigate_to('settings')

        # Scrollable main content
        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(16)
                spacing: dp(16)

                # Welcome card
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: dp(100)
                    padding: dp(16)
                    spacing: dp(8)
                    canvas.before:
                        Color:
                            rgba: 0.13, 0.13, 0.20, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(12)]

                    Label:
                        text: 'Welcome to Offline Dubbing Studio'
                        font_size: '18sp'
                        bold: True
                        color: 1, 1, 1, 1
                        halign: 'left'
                        text_size: self.size

                    Label:
                        text: 'Dub videos with AI — 100% offline'
                        font_size: '13sp'
                        color: 0.6, 0.6, 0.8, 1
                        halign: 'left'
                        text_size: self.size

                # New Project button
                Button:
                    text: '+ New Dubbing Project'
                    size_hint_y: None
                    height: dp(56)
                    font_size: '16sp'
                    bold: True
                    background_color: 0.25, 0.47, 0.95, 1
                    color: 1, 1, 1, 1
                    on_release: root.new_project()

                # Quick actions grid
                GridLayout:
                    cols: 2
                    size_hint_y: None
                    height: dp(160)
                    spacing: dp(12)

                    ActionCard:
                        title: 'Import Video'
                        subtitle: 'Add from storage'
                        icon_text: 'V'
                        on_release: root.import_video()

                    ActionCard:
                        title: 'History'
                        subtitle: 'Recent projects'
                        icon_text: 'H'
                        on_release: app.navigate_to('history')

                    ActionCard:
                        title: 'Settings'
                        subtitle: 'Models & quality'
                        icon_text: 'S'
                        on_release: app.navigate_to('settings')

                    ActionCard:
                        title: 'About'
                        subtitle: 'Version & info'
                        icon_text: 'A'
                        on_release: app.navigate_to('about')

                # Recent projects
                Label:
                    text: 'Recent Projects'
                    font_size: '16sp'
                    bold: True
                    color: 1, 1, 1, 1
                    size_hint_y: None
                    height: dp(40)
                    halign: 'left'
                    text_size: self.size

                RecentProjectsList:
                    id: recent_list
                    size_hint_y: None
                    height: self.minimum_height

<ActionCard@Button>:
    title: ''
    subtitle: ''
    icon_text: ''
    size_hint_y: None
    height: dp(72)
    background_color: 0, 0, 0, 0

    canvas.before:
        Color:
            rgba: 0.13, 0.13, 0.20, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(12)]

    BoxLayout:
        orientation: 'horizontal'
        padding: dp(12)
        spacing: dp(12)

        Label:
            text: root.icon_text
            font_size: '22sp'
            size_hint_x: None
            width: dp(36)
            color: 0.4, 0.6, 1, 1

        BoxLayout:
            orientation: 'vertical'

            Label:
                text: root.title
                font_size: '14sp'
                bold: True
                color: 1, 1, 1, 1
                halign: 'left'
                text_size: self.size

            Label:
                text: root.subtitle
                font_size: '12sp'
                color: 0.5, 0.5, 0.7, 1
                halign: 'left'
                text_size: self.size

<RecentProjectsList@BoxLayout>:
    orientation: 'vertical'
    spacing: dp(8)
""")


class HomeScreen(Screen):
    """Main home screen."""

    def on_enter(self):
        self._load_recent_projects()

    def _load_recent_projects(self):
        from database.history.history_manager import HistoryManager
        hm = HistoryManager()
        recent = hm.get_recent(limit=5)
        container = self.ids.recent_list
        container.clear_widgets()

        if not recent:
            from kivy.uix.label import Label
            lbl = Label(
                text="No projects yet. Start by importing a video.",
                color=(0.5, 0.5, 0.6, 1),
                font_size="13sp",
                size_hint_y=None,
                height="40dp",
                halign="center",
            )
            container.add_widget(lbl)
        else:
            for entry in recent:
                from widgets.video_card import ProjectHistoryCard
                card = ProjectHistoryCard(entry=entry)
                container.add_widget(card)

    def new_project(self):
        App.get_running_app().clear_project()
        App.get_running_app().navigate_to("video_picker")

    def import_video(self):
        App.get_running_app().navigate_to("video_picker")
