# Accessible Shortcuts Module
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtCore import Qt

def setup_global_shortcuts(main_window):
    """
    Sets up all the Alt+... shortcuts for sidebar navigation
    and standard Ctrl+ shortcuts.
    """

    # Navigation Shortcuts
    shortcut_explore = QShortcut(QKeySequence("Alt+1"), main_window)
    shortcut_explore.activated.connect(lambda: main_window.switch_tab("explore"))

    shortcut_downloads = QShortcut(QKeySequence("Alt+2"), main_window)
    shortcut_downloads.activated.connect(lambda: main_window.switch_tab("downloads"))

    shortcut_playlists = QShortcut(QKeySequence("Alt+3"), main_window)
    shortcut_playlists.activated.connect(lambda: main_window.switch_tab("playlists"))

    shortcut_history = QShortcut(QKeySequence("Alt+4"), main_window)
    shortcut_history.activated.connect(lambda: main_window.switch_tab("history"))

    # Open Downloads Folder (Ctrl+O)
    shortcut_open = QShortcut(QKeySequence("Ctrl+O"), main_window)
    def open_downloads():
        from core.config import config_manager
        import os, subprocess, platform
        path = config_manager.get('download_dir')
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    shortcut_open.activated.connect(open_downloads)

    # Search Focus (Ctrl+F)
    shortcut_search = QShortcut(QKeySequence("Ctrl+F"), main_window)
    def focus_search():
        main_window.switch_tab("explore")
        if "explore" in main_window.pages:
            main_window.pages["explore"].search_input.setFocus()

    shortcut_search.activated.connect(focus_search)

    # Quit (Ctrl+Q)
    shortcut_quit = QShortcut(QKeySequence("Ctrl+Q"), main_window)
    shortcut_quit.activated.connect(main_window.close)
