import sys
from PySide6.QtWidgets import QApplication
from ui.views.main_window import MainWindow

app = QApplication(sys.argv)
win = MainWindow()

# Verify that tabs work
assert "explore" in win.pages
assert "downloads" in win.pages
assert "settings" in win.pages

# Verify Backend
from core.backend import backend
assert backend is not None

# Verify Config
from core.config import config_manager
assert config_manager.get('language') in ['en', 'tr', 'es', 'ar'] # allow any supported language if saved in config

win.close()
app.processEvents()
app.quit()
print("ALL TESTS PASSED")
