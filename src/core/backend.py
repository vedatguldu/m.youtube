import yt_dlp
import logging
import os
import threading
from PySide6.QtCore import QObject, QThread, Signal
from core.config import config_manager

logger = logging.getLogger("YouTubeDesktop")

class YtDlpBackend(QObject):
    """
    Core backend for yt-dlp operations.
    Handles searching, extracting stream URLs, and authentication.
    Runs entirely on QThreads to prevent blocking the UI.
    """

    # Signals for search
    search_started = Signal()
    search_finished = Signal(list)
    search_error = Signal(str)

    # Signals for stream extraction
    extraction_started = Signal()
    extraction_finished = Signal(dict)
    extraction_error = Signal(str)

    # Signals for auth
    auth_step = Signal(str) # e.g. "Please open https://... and enter code XYZ"
    auth_success = Signal()
    auth_failed = Signal(str)

    def __init__(self):
        super().__init__()
        self._search_thread = None
        self._extract_thread = None
        self._auth_thread = None

    def _get_base_ydl_opts(self):
        opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,  # Don't download actual videos during search
            'ignoreerrors': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        }

        # Check if we have oauth2 cache
        oauth_cache = config_manager.get('oauth2_cache')
        if oauth_cache:
            # We don't directly pass the string cache, we just tell yt-dlp to use oauth2
            # yt-dlp manages its own internal cache for oauth2 based on the cache directory
            opts['username'] = 'oauth2'

        return opts

    # --- Search ---
    def search_videos(self, query, region="US", language="en", limit=50):
        if self._search_thread and self._search_thread.is_alive():
            logger.warning("Search already in progress, ignoring.")
            return

        self.search_started.emit()
        self._search_thread = threading.Thread(target=self._search_worker, args=(query, region, language, limit))
        self._search_thread.start()

    def _search_worker(self, query, region, language, limit):
        opts = self._get_base_ydl_opts()
        # Ensure youtube results align with the chosen region and language
        opts['extractor_args'] = {'youtube': {'gl': [region], 'hl': [language]}}
        # Ensure we only fetch max limit results using ytsearch format
        search_query = f"ytsearch{limit}:{query}"

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(search_query, download=False)

                results = []
                if 'entries' in info:
                    for entry in info['entries']:
                        if not entry or entry.get('id') is None:
                            continue

                        # Sanitize and prepare data for UI
                        video_data = {
                            'id': entry.get('id'),
                            'title': entry.get('title', 'Unknown Title'),
                            'channel': entry.get('uploader', entry.get('channel', 'Unknown Channel')),
                            'duration': entry.get('duration', 0),
                            'view_count': entry.get('view_count', 0),
                            'thumbnails': entry.get('thumbnails', []),
                            'url': f"https://www.youtube.com/watch?v={entry.get('id')}"
                        }

                        # Get best thumbnail
                        if video_data['thumbnails']:
                            video_data['best_thumbnail'] = video_data['thumbnails'][-1]['url']
                        else:
                            video_data['best_thumbnail'] = None

                        results.append(video_data)

                self.search_finished.emit(results)

        except Exception as e:
            logger.error(f"Search failed: {e}")
            self.search_error.emit(str(e))

    # --- Stream Extraction (for playback) ---
    def extract_stream_info(self, video_url):
        if self._extract_thread and self._extract_thread.is_alive():
            logger.warning("Extraction already in progress.")
            return

        self.extraction_started.emit()
        self._extract_thread = threading.Thread(target=self._extract_worker, args=(video_url,))
        self._extract_thread.start()

    def _extract_worker(self, video_url):
        # We need actual formats now, not flat
        opts = self._get_base_ydl_opts()
        opts['extract_flat'] = False

        # Priority: Best pre-merged (audio+video) up to 720p, fallback to worst, then best audio
        # QMediaPlayer handles standard mp4/webm with both streams perfectly.
        # It struggles with DASH (separate audio/video streams).
        opts['format'] = 'best[height<=720]/best[ext=mp4]/best'

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(video_url, download=False)

                if not info:
                    self.extraction_error.emit("Video information could not be retrieved.")
                    return

                stream_url = info.get('url')
                if not stream_url:
                    # Sometimes the direct URL is in requested_formats
                    if 'requested_formats' in info and len(info['requested_formats']) > 0:
                        stream_url = info['requested_formats'][0].get('url')

                if not stream_url:
                    self.extraction_error.emit("Stream URL not found.")
                    return

                result = {
                    'id': info.get('id'),
                    'title': info.get('title'),
                    'channel': info.get('uploader'),
                    'stream_url': stream_url,
                    'duration': info.get('duration'),
                    'original_url': video_url
                }

                self.extraction_finished.emit(result)

        except Exception as e:
            logger.error(f"Stream extraction failed: {e}")
            self.extraction_error.emit(str(e))

    # --- OAuth2 Device Flow Authentication ---
    def authenticate_oauth2(self):
        """
        Starts the OAuth2 Device Flow.
        Note: yt-dlp handles this internally by printing to stdout.
        We intercept the logger to pass the message to our UI.
        """
        self._auth_thread = threading.Thread(target=self._auth_worker)
        self._auth_thread.start()

    def _auth_worker(self):
        class YtLogger:
            def __init__(self, backend_ref):
                self.backend = backend_ref

            def debug(self, msg): pass

            def warning(self, msg):
                # Intercept the device code message
                if "Go to" in msg and "enter code" in msg:
                    self.backend.auth_step.emit(msg)
                logger.warning(f"ydl: {msg}")

            def error(self, msg):
                logger.error(f"ydl: {msg}")

        opts = {
            'username': 'oauth2',
            'extract_flat': True,
            'logger': YtLogger(self),
            # Fetch a known fast endpoint just to trigger auth
            'quiet': False
        }

        try:
            # We try to extract info from a harmless URL to trigger the auth flow
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.extract_info("https://www.youtube.com/watch?v=BaW_jenozKc", download=False)

            # If it succeeds without throwing, auth is complete
            config_manager.set('oauth2_cache', True) # Mark that we have cached credentials
            self.auth_success.emit()

        except Exception as e:
            logger.error(f"OAuth2 failed: {e}")
            self.auth_failed.emit(str(e))

backend = YtDlpBackend()
