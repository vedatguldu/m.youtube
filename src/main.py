import sys
from PySide6.QtWidgets import QApplication
from ui.views.main_window import MainWindow
from core.config import logger
from core.theme import theme_manager

def apply_theme(app, theme_name):
    if theme_name == 'dark':
        app.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #FFFFFF;
            }
            QLabel { color: #FFFFFF; }
            QFrame { border-color: #333333; }
            QLineEdit, QListWidget, QScrollArea {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: 1px solid #333333;
            }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.1); }
            /* Explicit text colors for specific labels if needed */
        """)
    else:
        app.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                color: #1F1F1F;
            }
            QLabel { color: #1F1F1F; }
            QFrame { border-color: #EEEEEE; }
            QLineEdit, QListWidget, QScrollArea {
                background-color: #FFFFFF;
                color: #1F1F1F;
                border: 1px solid #CCCCCC;
            }
            QPushButton:hover { background-color: rgba(0, 0, 0, 0.05); }
        """)

def main():
    logger.info("Application starting...")

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough if hasattr(Qt, 'HighDpiScaleFactorRoundingPolicy') else 1
    )

    app = QApplication(sys.argv)
    app.setApplicationName("YouTube Desktop")

    # Theme management
    apply_theme(app, theme_manager.get_theme())
    theme_manager.theme_changed.connect(lambda t: apply_theme(app, t))

    window = MainWindow()
    window.show()

    logger.info("Main window shown. Entering event loop.")
    sys.exit(app.exec())

if __name__ == "__main__":
    from PySide6.QtCore import Qt
    main()
