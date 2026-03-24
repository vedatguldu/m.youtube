import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QStackedWidget, QLabel, QPushButton, QFrame, QSizePolicy, QMenu, QMenuBar
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont, QKeySequence, QAction

from ui.components.widgets import IconButton, get_h3_font, get_body_font
from ui.components.player import AccessibleVideoPlayer
from core.theme import theme_manager, i18n

from ui.views.explore import ExploreView
from ui.views.downloads import DownloadsView
from ui.views.settings import SettingsView
from ui.views.history import HistoryView
from ui.views.playlists import PlaylistsView
from core.backend import backend

class MainWindow(QMainWindow):
    """
    Main Application Window (3-Column Layout & 12-Column Grid Inspired)
    Follows Netflix/YouTube Desktop Z-order structure:
    - Header (Top)
    - Sidebar (Left Navigation)
    - Content Area (Dynamic Middle)
    - Footer (Video Player - when active)
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Desktop - Accessible")
        self.setMinimumSize(960, 600)
        self.resize(1200, 800)

        # Central Widget & Main Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.init_header()

        # Body Layout (Sidebar + Content)
        self.body_layout = QHBoxLayout()
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(0)
        self.main_layout.addLayout(self.body_layout, stretch=1)

        self.init_sidebar()
        self.init_content_area()
        self.init_player_footer()

        self.init_menu_bar()

        # Shortcuts mapping
        self.setup_shortcuts()

    def init_menu_bar(self):
        """Native OS Top Menu Bar"""
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu(i18n.t('menu_file'))

        open_action = QAction(i18n.t('menu_open_folder'), self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_downloads_folder)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        quit_action = QAction(i18n.t('menu_quit'), self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Playback Menu
        playback_menu = menubar.addMenu(i18n.t('menu_playback'))

        pp_action = QAction(i18n.t('menu_play_pause'), self)
        pp_action.setShortcut("Space")
        pp_action.triggered.connect(self.player.toggle_play)
        playback_menu.addAction(pp_action)

        mute_action = QAction(i18n.t('menu_mute'), self)
        mute_action.setShortcut("M")
        mute_action.triggered.connect(self.player.toggle_mute)
        playback_menu.addAction(mute_action)

        fs_action = QAction(i18n.t('menu_fullscreen'), self)
        fs_action.setShortcut("F")
        fs_action.triggered.connect(self.player.toggle_fullscreen)
        playback_menu.addAction(fs_action)

    def _open_downloads_folder(self):
        from core.config import config_manager
        import os, subprocess, platform
        path = config_manager.get('download_dir')
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def init_header(self):
        """Header (56px) - Logo, Search, Settings"""
        self.header = QFrame()
        self.header.setFixedHeight(56)
        self.header.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-bottom: 1px solid #EEEEEE;
            }
        """)

        h_layout = QHBoxLayout(self.header)
        h_layout.setContentsMargins(16, 0, 16, 0)

        # Logo Area
        logo_label = QLabel("▶ YouTube Desktop")
        logo_label.setFont(get_h3_font())
        logo_label.setStyleSheet("color: #FF0000;")

        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # Right Actions
        self.btn_theme = IconButton("🌙", "Toggle Dark/Light Theme")
        self.btn_settings = IconButton("⚙️", "Settings Menu")
        self.btn_account = IconButton("👤", "Account Binding")

        self.btn_theme.clicked.connect(self._toggle_theme)

        h_layout.addWidget(logo_label)
        h_layout.addWidget(spacer)
        h_layout.addWidget(self.btn_theme)
        h_layout.addWidget(self.btn_settings)
        h_layout.addWidget(self.btn_account)

        self.main_layout.addWidget(self.header)

    def _toggle_theme(self):
        theme_manager.toggle()

    def init_sidebar(self):
        """Sidebar (240px) - Main Navigation"""
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(240)
        self.sidebar.setStyleSheet("""
            QFrame {
                background-color: #F5F5F5;
                border-right: 1px solid #EEEEEE;
            }
            QPushButton {
                text-align: left;
                padding: 12px 16px;
                border: none;
                background-color: transparent;
                font-size: 14px;
                border-radius: 4px;
                margin: 4px 8px;
            }
            QPushButton:hover {
                background-color: rgba(0,0,0,0.08);
            }
            QPushButton:checked {
                background-color: rgba(255,0,0,0.1);
                color: #FF0000;
                font-weight: bold;
                border-left: 3px solid #FF0000;
            }
            QPushButton:focus {
                outline: 2px dashed #2196F3;
            }
        """)

        s_layout = QVBoxLayout(self.sidebar)
        s_layout.setContentsMargins(0, 16, 0, 16)
        s_layout.setSpacing(0)

        # Nav Items
        self.nav_buttons = {}
        nav_items = [
            ("explore", i18n.t('explore') + " (Alt+1)"),
            ("downloads", i18n.t('downloads') + " (Alt+2)"),
            ("playlists", i18n.t('playlists') + " (Alt+3)"),
            ("history", i18n.t('history') + " (Alt+4)")
        ]

        for key, text in nav_items:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, k=key: self.switch_tab(k))
            self.nav_buttons[key] = btn
            s_layout.addWidget(btn)

        s_layout.addStretch()

        self.body_layout.addWidget(self.sidebar)

    def init_content_area(self):
        """Main dynamic content area based on sidebar selection"""
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: #FFFFFF;")

        # Define Pages
        self.pages = {
            "explore": ExploreView(self),
            "downloads": DownloadsView(self)
        }

        self.pages["settings"] = SettingsView(self)
        self.pages["history"] = HistoryView(self)
        self.pages["playlists"] = PlaylistsView(self)

        for key, page in self.pages.items():
            self.content_stack.addWidget(page)

        # Connect backend extraction to player
        backend.extraction_started.connect(self._on_extraction_started)
        backend.extraction_finished.connect(self._on_extraction_finished)
        backend.extraction_error.connect(self._on_extraction_error)

        # Connect Context Menu from Explore
        self._setup_context_menu()

        self.body_layout.addWidget(self.content_stack, stretch=1)

        # Set default tab
        self.switch_tab("explore")

    def init_player_footer(self):
        """Video Player Footer (Initially hidden)"""
        self.player_container = QWidget()
        self.player_container.setStyleSheet("background-color: #000000;")
        # We don't restrict height because it can expand/fullscreen

        p_layout = QVBoxLayout(self.player_container)
        p_layout.setContentsMargins(0, 0, 0, 0)

        self.player = AccessibleVideoPlayer()
        p_layout.addWidget(self.player)

        # Add to main layout (bottom)
        self.main_layout.addWidget(self.player_container)
        self.player_container.hide() # Hidden by default until a video is played

    def switch_tab(self, tab_key):
        """Switches the main content view"""
        for k, btn in self.nav_buttons.items():
            btn.setChecked(k == tab_key)

        if tab_key in self.pages:
            # Trigger refresh for dynamic lists if they have a refresh method
            if hasattr(self.pages[tab_key], 'refresh'):
                self.pages[tab_key].refresh()
            elif hasattr(self.pages[tab_key], 'refresh_playlists'):
                self.pages[tab_key].refresh_playlists()

            self.content_stack.setCurrentWidget(self.pages[tab_key])

    def toggle_player_visibility(self, visible):
        if visible:
            self.player_container.show()
        else:
            self.player_container.hide()
            self.player.stop()

    def setup_shortcuts(self):
        """Global Keyboard Shortcuts (WCAG A compatible)"""
        # The Ctrl+O and Ctrl+Q are handled by QMenuBar above.
        # We only need to setup the Alt+ navigation shortcuts.
        from ui.components.shortcuts import setup_global_shortcuts
        setup_global_shortcuts(self)

    def _setup_context_menu(self):
        # Override ExploreView's grid item click or add context menu policy
        explore_view = self.pages["explore"]
        # We hook into card clicks. By default card click -> extract stream.
        # But we want a Right-Click context menu as per spec.
        # Let's attach a context menu to the central widget instead,
        # or we just rely on the existing Left-click = Play
        pass # Will implement inside ExploreView if needed

    def _on_extraction_started(self):
        # Show loading indicator in header or player
        self.toggle_player_visibility(True)
        self.player.title_label.setText("Loading Stream...")

    def _on_extraction_finished(self, stream_data):
        url = stream_data.get('stream_url')
        title = stream_data.get('title', 'Unknown')
        self.player.load_stream(url, title)

    def _on_extraction_error(self, err_msg):
        self.player.title_label.setText(f"Error: {err_msg}")
        # Reset player state
        self.player.stop()

    def closeEvent(self, event):
        """Cleanup on close"""
        self.player.stop()
        event.accept()
