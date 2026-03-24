from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QScrollArea, QGridLayout, QLabel, QFrame
)
from PySide6.QtCore import Qt, QSize
from ui.components.widgets import FilledButton, VideoCard, get_h3_font
from core.backend import backend

class ExploreView(QWidget):
    """
    Search & Discovery Tab (Arama ve Keşfetme)
    - Search bar + Button
    - Responsive Grid Layout for results
    - Connects to YtDlpBackend
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ExploreView")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        # --- Search Header ---
        search_layout = QHBoxLayout()
        search_layout.setSpacing(8)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search YouTube videos...")
        self.search_input.setMinimumHeight(40)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                padding: 0 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
        """)
        self.search_input.returnPressed.connect(self.perform_search)
        self.search_input.setAccessibleName("Search Videos Input")

        self.search_btn = FilledButton("🔍 Search")
        self.search_btn.clicked.connect(self.perform_search)

        search_layout.addWidget(self.search_input, stretch=1)
        search_layout.addWidget(self.search_btn)

        # Status Label
        self.status_label = QLabel("Enter a keyword to discover videos.")
        self.status_label.setStyleSheet("color: #666666;")

        # --- Results Area (Grid) ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet("background-color: transparent;")

        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(16)
        self.scroll_area.setWidget(self.grid_container)

        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.scroll_area, stretch=1)

        # Backend Connections
        backend.search_started.connect(self._on_search_started)
        backend.search_finished.connect(self._on_search_finished)
        backend.search_error.connect(self._on_search_error)

    def perform_search(self):
        query = self.search_input.text().strip()
        if not query:
            return

        backend.search_videos(query, limit=50)

    def _on_search_started(self):
        self.status_label.setText("Searching... Please wait.")
        self.search_btn.setEnabled(False)
        self._clear_grid()

    def _on_search_finished(self, results):
        self.search_btn.setEnabled(True)
        self.status_label.setText(f"Found {len(results)} results.")

        # Populate grid (Responsive calculation: ~260px per card)
        # For simplicity, we use 4 columns initially. We'll adjust based on window resize later.
        cols = 4
        row = 0
        col = 0

        for video in results:
            card = VideoCard(video)
            card.clicked.connect(self._on_card_clicked)
            self.grid_layout.addWidget(card, row, col)

            col += 1
            if col >= cols:
                col = 0
                row += 1

    def _on_search_error(self, err_msg):
        self.search_btn.setEnabled(True)
        self.status_label.setText(f"Error: {err_msg}")
        self.status_label.setStyleSheet("color: #F44336;") # Red

    def _clear_grid(self):
        # Remove all widgets from grid layout
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _on_card_clicked(self, video_data):
        # Default action: Play
        self.status_label.setText(f"Loading stream for: {video_data['title']}...")
        backend.extract_stream_info(video_data['url'])

        # Log to history
        from core.config import config_manager
        config_manager.add_to_history({
            'id': video_data.get('id'),
            'title': video_data.get('title'),
            'channel': video_data.get('channel'),
            'url': video_data.get('url'),
            'type': 'watch'
        })

    def contextMenuEvent(self, event):
        """Right-click context menu logic for video cards"""
        # We need to find if the right-click was over a video card
        child = self.childAt(event.pos())

        # Walk up to find the VideoCard
        while child:
            from ui.components.widgets import VideoCard
            if isinstance(child, VideoCard):
                self._show_context_menu(child.video_data, event.globalPos())
                return
            child = child.parentWidget()

    def _show_context_menu(self, video_data, pos):
        from PySide6.QtWidgets import QMenu
        from PySide6.QtGui import QAction

        menu = QMenu(self)

        play_action = QAction("▶ Oynat (Play)", self)
        play_action.triggered.connect(lambda: self._on_card_clicked(video_data))

        download_action = QAction("⬇️ İndir (Download)", self)
        download_action.triggered.connect(lambda: self._trigger_download(video_data))

        menu.addAction(play_action)
        menu.addAction(download_action)

        menu.exec_(pos)

    def _trigger_download(self, video_data):
        # Find Downloads view from parent (MainWindow) and trigger download
        parent_window = self.window()
        if hasattr(parent_window, 'pages'):
            downloads_view = parent_window.pages.get('downloads')
            if downloads_view:
                self.status_label.setText(f"Added to downloads: {video_data['title']}")
                downloads_view.add_download(video_data)
