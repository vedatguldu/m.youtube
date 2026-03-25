from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QComboBox, QFileDialog
)
from PySide6.QtCore import Qt
from core.config import config_manager
from core.backend import backend
from core.theme import i18n
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
        gen_title = QLabel(i18n.t('general'))
        gen_title.setFont(get_h3_font())

        down_layout = QHBoxLayout()
        self.down_label = QLabel(f"{i18n.t('download_dir')}: {config_manager.get('download_dir')}")
        self.down_label.setFont(get_body_font())

        btn_change_dir = OutlinedButton("📂")
        btn_change_dir.setFixedWidth(50)
        btn_change_dir.clicked.connect(self.change_directory)

        down_layout.addWidget(self.down_label, stretch=1)
        down_layout.addWidget(btn_change_dir)

        # --- Language ---
        lang_layout = QHBoxLayout()
        lang_label = QLabel(i18n.t('language'))
        lang_label.setFont(get_body_font())

        self.lang_combo = QComboBox()
        self.lang_combo.addItem("English", "en")
        self.lang_combo.addItem("Türkçe", "tr")
        self.lang_combo.addItem("Español", "es")
        self.lang_combo.addItem("العربية", "ar")

        # Set current
        current_lang = config_manager.get('language')
        index = self.lang_combo.findData(current_lang)
        if index >= 0:
            self.lang_combo.setCurrentIndex(index)

        self.lang_combo.currentIndexChanged.connect(self.change_language)

        lang_layout.addWidget(lang_label, stretch=1)
        lang_layout.addWidget(self.lang_combo)

        layout.addWidget(gen_title)
        layout.addLayout(down_layout)
        layout.addLayout(lang_layout)

        # Notification label
        self.restart_lbl = QLabel(i18n.t('restart_required', default="Please restart the app to fully apply language changes."))
        self.restart_lbl.setStyleSheet("color: #FF9800;")
        self.restart_lbl.hide()
        layout.addWidget(self.restart_lbl)

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

    def change_directory(self):
        new_dir = QFileDialog.getExistingDirectory(self, "Select Download Directory")
        if new_dir:
            config_manager.set('download_dir', new_dir)
            self.down_label.setText(f"{i18n.t('download_dir')}: {new_dir}")

    def change_language(self):
        lang_code = self.lang_combo.currentData()
        if lang_code != config_manager.get('language'):
            i18n.load_language(lang_code)
            self.restart_lbl.show()
