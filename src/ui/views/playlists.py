from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QMenu, QLineEdit, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from ui.components.widgets import get_h3_font, FilledButton, OutlinedButton
from core.theme import i18n
from core.config import config_manager
from core.backend import backend

class PlaylistsView(QWidget):
    """
    Playlists Tab (Çalma Listeleri)
    Allows creating, viewing, and managing playlists.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PlaylistsView")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        # --- Header ---
        h_layout = QHBoxLayout()
        title = QLabel(i18n.t('playlists_title'))
        title.setFont(get_h3_font())

        h_layout.addWidget(title, stretch=1)

        # --- Create Playlist ---
        create_layout = QHBoxLayout()
        self.new_name_input = QLineEdit()
        self.new_name_input.setPlaceholderText(i18n.t('playlists_name'))

        self.btn_create = FilledButton(i18n.t('playlists_create'))
        self.btn_create.clicked.connect(self.create_playlist)

        create_layout.addWidget(self.new_name_input, stretch=1)
        create_layout.addWidget(self.btn_create)

        # --- Split View (Playlists & Videos) ---
        split_layout = QHBoxLayout()

        self.playlists_list = QListWidget()
        self.playlists_list.itemClicked.connect(self.on_playlist_selected)

        self.videos_list = QListWidget()
        self.videos_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.videos_list.customContextMenuRequested.connect(self.show_video_menu)

        split_layout.addWidget(self.playlists_list, 1)
        split_layout.addWidget(self.videos_list, 2)

        layout.addLayout(h_layout)
        layout.addLayout(create_layout)
        layout.addLayout(split_layout, stretch=1)

        self.current_playlist = None
        self.refresh_playlists()

    def refresh_playlists(self):
        self.playlists_list.clear()
        playlists = config_manager.get_playlists()

        for name in playlists.keys():
            item = QListWidgetItem(f"📁 {name} ({len(playlists[name])})")
            item.setData(Qt.UserRole, name)
            self.playlists_list.addItem(item)

    def create_playlist(self):
        name = self.new_name_input.text().strip()
        if name:
            config_manager.create_playlist(name)
            self.new_name_input.clear()
            self.refresh_playlists()

    def on_playlist_selected(self, item):
        self.current_playlist = item.data(Qt.UserRole)
        self.refresh_videos()

    def refresh_videos(self):
        self.videos_list.clear()
        if not self.current_playlist:
            return

        playlists = config_manager.get_playlists()
        videos = playlists.get(self.current_playlist, [])

        if not videos:
            self.videos_list.addItem(QListWidgetItem(i18n.t('playlists_empty')))
            return

        for v in videos:
            title = v.get('title', 'Unknown')
            item = QListWidgetItem(f"▶ {title}")
            item.setData(Qt.UserRole, v)
            self.videos_list.addItem(item)

    def show_video_menu(self, pos):
        item = self.videos_list.itemAt(pos)
        if not item:
            return

        video_data = item.data(Qt.UserRole)
        if not video_data:
            return # Probably the 'empty' message

        menu = QMenu(self)

        play_action = QAction(i18n.t('play_video'), self)
        play_action.triggered.connect(lambda: self._play_video(video_data))

        remove_action = QAction(i18n.t('video_remove'), self)
        remove_action.triggered.connect(lambda: self._remove_video(video_data))

        menu.addAction(play_action)
        menu.addAction(remove_action)

        menu.exec_(self.videos_list.mapToGlobal(pos))

    def _play_video(self, video_data):
        backend.extract_stream_info(video_data.get('url'))

    def _remove_video(self, video_data):
        if self.current_playlist:
            config_manager.remove_from_playlist(self.current_playlist, video_data.get('id'))
            self.refresh_videos()
            self.refresh_playlists()
