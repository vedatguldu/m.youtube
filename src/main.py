import sys
import logging
from PySide6.QtWidgets import QApplication
from ui.views.main_window import MainWindow
from core.config import logger

def main():
    logger.info("Application starting...")

    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough if hasattr(Qt, 'HighDpiScaleFactorRoundingPolicy') else 1
    )

    app = QApplication(sys.argv)
    app.setApplicationName("YouTube Desktop")

    window = MainWindow()
    window.show()

    logger.info("Main window shown. Entering event loop.")
    sys.exit(app.exec())

if __name__ == "__main__":
    from PySide6.QtCore import Qt
    main()
