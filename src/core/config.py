import os
import json
import logging
import platform

# Constants
APP_NAME = "YouTubeDesktop"
APP_VERSION = "1.0.0"

def get_app_dir():
    """Gets the user-specific application data directory."""
    if platform.system() == "Windows":
        base_dir = os.environ.get("APPDATA", os.path.expanduser("~"))
    elif platform.system() == "Darwin":
        base_dir = os.path.expanduser("~/Library/Application Support")
    else:
        base_dir = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))

    app_dir = os.path.join(base_dir, APP_NAME)
    os.makedirs(app_dir, exist_ok=True)
    return app_dir

def get_downloads_dir():
    """Gets the default downloads directory."""
    if platform.system() == "Windows":
        return os.path.join(os.path.expanduser("~"), "Downloads", APP_NAME)
    else:
        return os.path.join(os.path.expanduser("~/Downloads"), APP_NAME)

# Setup Logging
def setup_logging():
    log_dir = get_app_dir()
    log_file = os.path.join(log_dir, "app.log")

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(APP_NAME)

logger = setup_logging()

class ConfigManager:
    """Manages application configuration, history, and playlists."""

    def __init__(self):
        self.app_dir = get_app_dir()
        self.config_path = os.path.join(self.app_dir, "config.json")
        self.history_path = os.path.join(self.app_dir, "history.json")
        self.playlists_path = os.path.join(self.app_dir, "playlists.json")

        self.config = self._load_json(self.config_path, self._get_default_config())
        self.history = self._load_json(self.history_path, [])
        self.playlists = self._load_json(self.playlists_path, {"Favorites": []})

    def _get_default_config(self):
        return {
            "language": "en",
            "theme": "system",
            "region": "US",
            "download_dir": get_downloads_dir(),
            "max_concurrent_downloads": 3,
            "oauth2_cache": None,
            "volume": 100
        }

    def _load_json(self, path, default):
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {path}: {e}")
        return default

    def _save_json(self, path, data):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving {path}: {e}")

    # --- Config Methods ---
    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config()

    def save_config(self):
        self._save_json(self.config_path, self.config)

    # --- History Methods ---
    def add_to_history(self, video_data):
        # Prevent duplicates, move to top if exists
        video_id = video_data.get('id')
        self.history = [v for v in self.history if v.get('id') != video_id]
        self.history.insert(0, video_data)

        # Keep history bounded (e.g., max 1000 items)
        if len(self.history) > 1000:
            self.history = self.history[:1000]

        self._save_json(self.history_path, self.history)

    def get_history(self):
        return self.history

    def clear_history(self):
        self.history = []
        self._save_json(self.history_path, self.history)

    # --- Playlist Methods ---
    def get_playlists(self):
        return self.playlists

    def create_playlist(self, name):
        if name not in self.playlists:
            self.playlists[name] = []
            self._save_json(self.playlists_path, self.playlists)
            return True
        return False

    def add_to_playlist(self, playlist_name, video_data):
        if playlist_name in self.playlists:
            video_id = video_data.get('id')
            # Check if already exists in this playlist
            if not any(v.get('id') == video_id for v in self.playlists[playlist_name]):
                self.playlists[playlist_name].append(video_data)
                self._save_json(self.playlists_path, self.playlists)
                return True
        return False

    def remove_from_playlist(self, playlist_name, video_id):
        if playlist_name in self.playlists:
            self.playlists[playlist_name] = [v for v in self.playlists[playlist_name] if v.get('id') != video_id]
            self._save_json(self.playlists_path, self.playlists)

config_manager = ConfigManager()
