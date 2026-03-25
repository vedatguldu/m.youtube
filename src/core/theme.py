import os
import sys
import json
import logging
from core.config import config_manager
from PySide6.QtCore import QObject, Signal

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Normal execution
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

logger = logging.getLogger("YouTubeDesktop")

class ThemeManager(QObject):
    theme_changed = Signal(str) # Emits 'dark' or 'light'

    def __init__(self):
        super().__init__()
        # Load from config or default to 'light'
        self.current_theme = config_manager.get('theme', 'light')
        if self.current_theme not in ['light', 'dark']:
            self.current_theme = 'light'

    def get_theme(self):
        return self.current_theme

    def set_theme(self, theme_name):
        if theme_name in ['light', 'dark']:
            self.current_theme = theme_name
            config_manager.set('theme', theme_name)
            self.theme_changed.emit(theme_name)

    def toggle(self):
        new_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.set_theme(new_theme)
        return new_theme

class LocaleManager(QObject):
    language_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.current_lang = config_manager.get('language', 'en')
        self.dict = {}
        self.load_language(self.current_lang)

    def load_language(self, lang_code):
        # Use our helper for robust path finding
        locales_dir = get_resource_path("locales")
        lang_path = os.path.join(locales_dir, f"{lang_code}.json")

        if not os.path.exists(lang_path):
            logger.warning(f"Language file not found: {lang_path}, falling back to English.")
            lang_path = os.path.join(locales_dir, "en.json")
            lang_code = "en"

        try:
            with open(lang_path, 'r', encoding='utf-8') as f:
                self.dict = json.load(f)
            self.current_lang = lang_code
            config_manager.set('language', lang_code)
            self.language_changed.emit(lang_code)
        except Exception as e:
            logger.error(f"Failed to load language file: {e}")
            self.dict = {}

    def t(self, key, default=None, **kwargs):
        text = self.dict.get(key, default if default is not None else key)
        if kwargs:
            try:
                return text.format(**kwargs)
            except KeyError:
                return text
        return text

theme_manager = ThemeManager()
i18n = LocaleManager()
