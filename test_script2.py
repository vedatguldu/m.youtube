import sys
from PySide6.QtWidgets import QApplication
from ui.views.main_window import MainWindow

app = QApplication(sys.argv)
win = MainWindow()

# Verify new pages are added
assert "history" in win.pages
assert "playlists" in win.pages

# Verify translation dictionary works
from core.theme import i18n
i18n.load_language('en')
assert i18n.t('explore') == '🔍 Explore'
i18n.load_language('tr')
assert i18n.t('explore') == '🔍 Keşfet'

print("ALL NEW TESTS PASSED")
