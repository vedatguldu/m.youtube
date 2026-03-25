from PySide6.QtWidgets import QPushButton, QSlider, QFrame, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtCore import Qt, QSize, Signal, QByteArray
from PySide6.QtGui import QCursor, QFont, QAccessible, QPixmap
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

# Brand Colors (Material 3)
BRAND_RED = "#FF0000"
BRAND_RED_HOVER = "#E60000"
BRAND_RED_PRESSED = "#CC0000"

LIGHT_BG = "#FFFFFF"
LIGHT_SURFACE = "#F5F5F5"
LIGHT_TEXT = "#1F1F1F"

DARK_BG = "#121212"
DARK_SURFACE = "#1E1E1E"
DARK_TEXT = "#FFFFFF"

# Common Fonts
def get_h3_font():
    f = QFont("Roboto", 14)
    f.setBold(True)
    return f

def get_body_font():
    return QFont("Roboto", 12)

class FilledButton(QPushButton):
    """Material 3 Filled Button (Primary Action)"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setMinimumHeight(40)
        self.setFont(get_body_font())

        # Accessibility
        self.setAccessibleName(text)
        self.setAccessibleDescription("Primary action button")

        self.setStyleSheet(f"""
            FilledButton {{
                background-color: {BRAND_RED};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0 24px;
                font-weight: bold;
            }}
            FilledButton:hover {{
                background-color: {BRAND_RED_HOVER};
            }}
            FilledButton:pressed {{
                background-color: {BRAND_RED_PRESSED};
            }}
            FilledButton:disabled {{
                background-color: #CCCCCC;
                color: #999999;
            }}
            FilledButton:focus {{
                outline: 2px solid #2196F3;
                outline-offset: 2px;
            }}
        """)

class OutlinedButton(QPushButton):
    """Material 3 Outlined Button (Secondary Action)"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setMinimumHeight(40)
        self.setFont(get_body_font())

        self.setAccessibleName(text)

        self.setStyleSheet(f"""
            OutlinedButton {{
                background-color: transparent;
                color: {BRAND_RED};
                border: 2px solid {BRAND_RED};
                border-radius: 8px;
                padding: 0 22px;
                font-weight: bold;
            }}
            OutlinedButton:hover {{
                background-color: rgba(255, 0, 0, 0.08);
            }}
            OutlinedButton:pressed {{
                background-color: rgba(255, 0, 0, 0.12);
            }}
            OutlinedButton:focus {{
                outline: 2px dashed #2196F3;
                outline-offset: 2px;
            }}
        """)

class IconButton(QPushButton):
    """Icon Button (40x40px minimum target)"""
    def __init__(self, icon_text, acc_name, parent=None):
        super().__init__(icon_text, parent)
        self.setFixedSize(40, 40)
        self.setCursor(QCursor(Qt.PointingHandCursor))

        self.setAccessibleName(acc_name)

        self.setStyleSheet(f"""
            IconButton {{
                background-color: transparent;
                border: none;
                border-radius: 20px;
                font-size: 18px;
            }}
            IconButton:hover {{
                background-color: rgba(0, 0, 0, 0.08);
            }}
            IconButton:pressed {{
                background-color: rgba(0, 0, 0, 0.12);
            }}
            IconButton:focus {{
                outline: 2px solid #2196F3;
            }}
        """)

class TimelineSlider(QSlider):
    """Custom Video Timeline Slider"""
    def __init__(self, parent=None):
        super().__init__(Qt.Horizontal, parent)
        self.setCursor(QCursor(Qt.PointingHandCursor))

        self.setAccessibleName("Video Timeline")
        self.setAccessibleDescription("Use left and right arrows to seek")

        self.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid #bbb;
                background: #CCCCCC;
                height: 4px;
                border-radius: 2px;
            }}
            QSlider::sub-page:horizontal {{
                background: {BRAND_RED};
                border: 1px solid #777;
                height: 4px;
                border-radius: 2px;
            }}
            QSlider::add-page:horizontal {{
                background: #CCCCCC;
                border: 1px solid #777;
                height: 4px;
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: white;
                border: 1px solid #777;
                width: 12px;
                margin-top: -4px;
                margin-bottom: -4px;
                border-radius: 6px;
            }}
            QSlider::handle:horizontal:hover {{
                background: #f0f0f0;
                border: 1px solid #444;
            }}
        """)

class VideoCard(QFrame):
    """A card displaying a video thumbnail, title, and channel."""

    clicked = Signal(dict)
    right_clicked = Signal(dict, object) # dict: video_data, object: global_pos

    def __init__(self, video_data, parent=None):
        super().__init__(parent)
        self.video_data = video_data

        self.setFrameShape(QFrame.StyledPanel)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setFocusPolicy(Qt.StrongFocus)

        # Accessibility
        title = video_data.get('title', 'Unknown')
        channel = video_data.get('channel', 'Unknown')
        self.setAccessibleName(f"Video: {title} by {channel}")
        self.setAccessibleRole(QAccessible.Button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        # Thumbnail placeholder
        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(240, 135)
        self.thumb_label.setStyleSheet("background-color: #E0E0E0; border-radius: 8px;")
        self.thumb_label.setAlignment(Qt.AlignCenter)
        self.thumb_label.setText("Loading...")
        self.thumb_label.setScaledContents(True)

        # Async image load
        self._nam = QNetworkAccessManager(self)
        self._nam.finished.connect(self._on_thumbnail_loaded)
        self._load_thumbnail()

        # Title
        self.title_label = QLabel(title)
        self.title_label.setFixedWidth(240)
        self.title_label.setFont(get_h3_font())
        self.title_label.setWordWrap(True)

        # Channel
        self.channel_label = QLabel(channel)
        self.channel_label.setFont(get_body_font())
        self.channel_label.setStyleSheet("color: #666;")

        layout.addWidget(self.thumb_label)
        layout.addWidget(self.title_label)
        layout.addWidget(self.channel_label)

        self.setStyleSheet("""
            VideoCard {
                background-color: white;
                border-radius: 8px;
            }
            VideoCard:hover {
                background-color: #F9F9F9;
                border: 1px solid #CCCCCC;
            }
            VideoCard:focus {
                border: 2px dashed #2196F3;
            }
        """)

    def _load_thumbnail(self):
        thumb_url = self.video_data.get('best_thumbnail')
        if thumb_url:
            from PySide6.QtCore import QUrl
            req = QNetworkRequest(QUrl(thumb_url))
            self._nam.get(req)
        else:
            self.thumb_label.setText("No Image")

    def _on_thumbnail_loaded(self, reply: QNetworkReply):
        if reply.error() == QNetworkReply.NoError:
            data = reply.readAll()
            pixmap = QPixmap()
            if pixmap.loadFromData(data):
                self.thumb_label.setPixmap(pixmap)
                self.thumb_label.setText("") # Clear text
        else:
            self.thumb_label.setText("Failed")
        reply.deleteLater()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.video_data)
        elif event.button() == Qt.RightButton:
            self.right_clicked.emit(self.video_data, event.globalPos())

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Space):
            self.clicked.emit(self.video_data)
