from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QMenu
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from ui.components.widgets import get_h3_font, FilledButton, OutlinedButton
from core.theme import i18n
from core.config import config_manager
from core.backend import backend

class HistoryView(QWidget):
    """
    Watch History Tab (İzleme Geçmişi)
    Displays list of watched videos and allows re-playing or clearing them.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("HistoryView")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        # Header
        h_layout = QHBoxLayout()
        title = QLabel(i18n.t('history_title'))
        title.setFont(get_h3_font())

        self.btn_clear = OutlinedButton(i18n.t('history_clear'))
        self.btn_clear.clicked.connect(self.clear_history)

        h_layout.addWidget(title, stretch=1)
        h_layout.addWidget(self.btn_clear)

        # List
        self.history_list = QListWidget()
        self.history_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.history_list.customContextMenuRequested.connect(self.show_context_menu)

        layout.addLayout(h_layout)
        layout.addWidget(self.history_list, stretch=1)

        self.refresh()

    def refresh(self):
        self.history_list.clear()
        history = config_manager.get_history()
        # Filter for watched videos
        watched = [h for h in history if h.get('type') == 'watch']

        for v in watched:
            item = QListWidgetItem(f"▶ {v.get('title', 'Unknown')} - {v.get('channel', '')}")
            item.setData(Qt.UserRole, v) # Store video data
            self.history_list.addItem(item)

    def clear_history(self):
        config_manager.clear_history()
        self.refresh()

    def show_context_menu(self, pos):
        item = self.history_list.itemAt(pos)
        if not item:
            return

        video_data = item.data(Qt.UserRole)
        menu = QMenu(self)

        play_action = QAction(i18n.t('play_video'), self)
        play_action.triggered.connect(lambda: self._play_video(video_data))

        menu.addAction(play_action)
        menu.exec_(self.history_list.mapToGlobal(pos))

    def _play_video(self, video_data):
        backend.extract_stream_info(video_data.get('url'))
