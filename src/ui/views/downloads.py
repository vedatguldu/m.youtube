import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QProgressBar, QHBoxLayout, QFrame
)
from PySide6.QtCore import Qt, QSize
from ui.components.widgets import IconButton, get_body_font, get_h3_font
from core.download import download_manager
from core.config import config_manager
import os

class DownloadItem(QFrame):
    """
    Individual Download Progress Item inside the Downloads View
    """
    def __init__(self, video_id, title, parent=None):
        super().__init__(parent)
        self.video_id = video_id

        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #EEEEEE;
                padding: 12px;
                margin-bottom: 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        # Header (Title + Status)
        h_layout = QHBoxLayout()

        self.title_label = QLabel(title)
        self.title_label.setFont(get_body_font())
        self.title_label.setStyleSheet("font-weight: bold;")

        self.status_label = QLabel("Starting...")
        self.status_label.setStyleSheet("color: #666666;")

        h_layout.addWidget(self.title_label, stretch=1)
        h_layout.addWidget(self.status_label)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #E0E0E0;
                height: 8px;
                border-radius: 4px;
                text-align: right;
            }
            QProgressBar::chunk {
                background-color: #FF0000;
                border-radius: 4px;
            }
        """)

        layout.addLayout(h_layout)
        layout.addWidget(self.progress_bar)

    def update_progress(self, percent, text):
        self.progress_bar.setValue(int(percent))
        self.status_label.setText(text)

    def set_finished(self, path):
        self.progress_bar.setValue(100)
        self.status_label.setText("Completed")
        self.status_label.setStyleSheet("color: #4CAF50;") # Green

    def set_error(self, msg):
        self.status_label.setText(f"Error: {msg}")
        self.status_label.setStyleSheet("color: #F44336;") # Red
        self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #F44336; }")

class DownloadsView(QWidget):
    """
    Downloads Tab
    - Active Downloads List
    - Download History
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DownloadsView")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Downloads & History")
        title.setFont(get_h3_font())

        # Active Downloads Section
        self.active_list = QVBoxLayout()
        self.active_list.setAlignment(Qt.AlignTop)
        self.active_items = {} # video_id -> DownloadItem

        active_container = QWidget()
        active_container.setLayout(self.active_list)
        active_container.setMinimumHeight(200)

        # Connect to DownloadManager
        download_manager.progress_updated.connect(self._on_progress)
        download_manager.download_finished.connect(self._on_finished)
        download_manager.download_error.connect(self._on_error)

        # History List
        history_title = QLabel("Recent Downloads")
        history_title.setFont(get_h3_font())
        history_title.setStyleSheet("margin-top: 16px;")

        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                padding: 8px;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #EEEEEE;
            }
            QListWidget::item:hover {
                background-color: #F5F5F5;
            }
        """)

        layout.addWidget(title)
        layout.addWidget(active_container)
        layout.addWidget(history_title)
        layout.addWidget(self.history_list, stretch=1)

        self.refresh_history()

    def add_download(self, video_data):
        """Called from Explore Tab (Context Menu)"""
        video_id = video_data['id']
        title = video_data['title']
        url = video_data['url']

        # UI
        item = DownloadItem(video_id, title)
        self.active_items[video_id] = item
        self.active_list.addWidget(item)

        # Backend
        download_manager.download_video(video_id, url, title)

    def _on_progress(self, video_id, percent, text):
        if video_id in self.active_items:
            self.active_items[video_id].update_progress(percent, text)

    def _on_finished(self, video_id, path):
        if video_id in self.active_items:
            self.active_items[video_id].set_finished(path)
        self.refresh_history()

    def _on_error(self, video_id, msg):
        if video_id in self.active_items:
            self.active_items[video_id].set_error(msg)

    def refresh_history(self):
        self.history_list.clear()
        history = config_manager.get_history()
        # Filter only downloads
        d_history = [h for h in history if h.get('type') == 'download']

        for h in d_history:
            title = h.get('title', 'Unknown')
            path = h.get('local_path', '')

            # Simple format for now
            item = QListWidgetItem(f"✓ {title}\n  Path: {path}")
            self.history_list.addItem(item)
