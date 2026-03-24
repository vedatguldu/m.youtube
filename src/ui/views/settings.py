from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
)
from PySide6.QtCore import Qt
from core.config import config_manager
from core.backend import backend
from ui.components.widgets import get_h3_font, get_body_font, FilledButton, OutlinedButton

class SettingsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsView")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        title = QLabel("Settings")
        title.setFont(get_h3_font())
        layout.addWidget(title)

        # --- Authentication Status ---
        auth_title = QLabel("Google / YouTube Account")
        auth_title.setFont(get_h3_font())

        self.auth_status = QLabel("Not logged in. You won't be able to access Members-only or Premium videos.")
        self.auth_status.setFont(get_body_font())
        self.auth_status.setWordWrap(True)

        self.btn_login = FilledButton("Login with Google (OAuth2)")
        self.btn_login.clicked.connect(self.trigger_login)

        if config_manager.get('oauth2_cache'):
            self.auth_status.setText("Logged in successfully. Premium/Members-only videos are accessible.")
            self.btn_login.setText("Re-authenticate")
            self.auth_status.setStyleSheet("color: #4CAF50;")

        layout.addWidget(auth_title)
        layout.addWidget(self.auth_status)
        layout.addWidget(self.btn_login)

        # --- Paths & General ---
        gen_title = QLabel("General")
        gen_title.setFont(get_h3_font())

        down_dir = config_manager.get('download_dir')
        down_label = QLabel(f"Download Directory: {down_dir}")
        down_label.setFont(get_body_font())

        layout.addWidget(gen_title)
        layout.addWidget(down_label)

        layout.addStretch()

        # Connect backend signals
        backend.auth_step.connect(self._on_auth_step)
        backend.auth_success.connect(self._on_auth_success)
        backend.auth_failed.connect(self._on_auth_error)

    def trigger_login(self):
        self.btn_login.setEnabled(False)
        self.auth_status.setText("Initializing authentication...")
        self.auth_status.setStyleSheet("color: #FF9800;")
        backend.authenticate_oauth2()

    def _on_auth_step(self, step_msg):
        # The user needs to open a browser and enter a code
        self.auth_status.setText(f"ACTION REQUIRED:\n\n{step_msg}")
        self.auth_status.setStyleSheet("color: #FF0000; font-weight: bold;")

    def _on_auth_success(self):
        self.btn_login.setEnabled(True)
        self.btn_login.setText("Re-authenticate")
        self.auth_status.setText("Logged in successfully. Premium/Members-only videos are accessible.")
        self.auth_status.setStyleSheet("color: #4CAF50;")

    def _on_auth_error(self, err_msg):
        self.btn_login.setEnabled(True)
        self.auth_status.setText(f"Authentication failed: {err_msg}")
        self.auth_status.setStyleSheet("color: #F44336;")
