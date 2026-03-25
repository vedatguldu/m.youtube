import logging
import os
import threading
from PySide6.QtCore import QObject, Signal, QTimer
from core.config import config_manager
from core.backend import backend

logger = logging.getLogger("YouTubeDesktop")

class DownloadManager(QObject):
    """
    Manages concurrent video downloads using yt-dlp.
    Reports progress back to the UI asynchronously.
    """

    # Emits (video_id, progress_percent, status_text)
    progress_updated = Signal(str, float, str)
    download_finished = Signal(str, str) # video_id, file_path
    download_error = Signal(str, str)    # video_id, error_message

    def __init__(self):
        super().__init__()
        self._active_downloads = {} # video_id -> thread
        self._queue = []
        self._max_concurrent = config_manager.get('max_concurrent_downloads', 3)
        self._lock = threading.Lock() # Protect shared structures

        # Timer to check queue
        self._queue_timer = QTimer(self)
        self._queue_timer.timeout.connect(self._process_queue)
        self._queue_timer.start(1000)

    def download_video(self, video_id, video_url, title):
        with self._lock:
            if video_id in self._active_downloads:
                logger.warning(f"Download for {video_id} already in progress.")
                return

            # Add to queue
            self._queue.append((video_id, video_url, title))

        self._process_queue()

    def _process_queue(self):
        with self._lock:
            if len(self._active_downloads) >= self._max_concurrent:
                return

            if not self._queue:
                return

            video_id, video_url, title = self._queue.pop(0)

            thread = threading.Thread(
                target=self._download_worker,
                args=(video_id, video_url, title)
            )
            self._active_downloads[video_id] = thread
            thread.start()

    def _download_worker(self, video_id, video_url, title):
        download_dir = config_manager.get('download_dir')
        os.makedirs(download_dir, exist_ok=True)

        # Clean title for filename to avoid OS errors
        safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        output_template = os.path.join(download_dir, f"{safe_title} - {video_id}.%(ext)s")

        # Custom progress hook for yt-dlp
        def progress_hook(d):
            if d['status'] == 'downloading':
                # Attempt to get percentage
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded_bytes = d.get('downloaded_bytes', 0)

                percent = 0.0
                if total_bytes > 0:
                    percent = (downloaded_bytes / total_bytes) * 100

                speed = d.get('speed', 0)
                speed_str = f"{speed / 1024 / 1024:.2f} MiB/s" if speed else "Unknown speed"

                status_text = f"Downloading: {speed_str}"

                # We emit this carefully to avoid flooding the UI thread
                self.progress_updated.emit(video_id, percent, status_text)

            elif d['status'] == 'finished':
                self.progress_updated.emit(video_id, 100.0, "Processing complete")

            elif d['status'] == 'error':
                self.progress_updated.emit(video_id, 0.0, "Error during download")

        # Base yt-dlp options
        # We use a single combined format (like mp4) to avoid requiring external 'ffmpeg'
        # If the user has ffmpeg installed, they could use 'bestvideo+bestaudio/best'.
        # Since we are making a standalone app, we aim for maximum compatibility.
        opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': output_template,
            'progress_hooks': [progress_hook],
            'quiet': True,
            'no_warnings': True
        }

        # Auth check
        if config_manager.get('oauth2_cache'):
            opts['username'] = 'oauth2'

        try:
            import yt_dlp
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(video_url, download=True)

                if info:
                    # The actual final path
                    ext = info.get('ext', 'mkv')
                    final_path = os.path.join(download_dir, f"{safe_title} - {video_id}.{ext}")

                    # Notify UI
                    self.download_finished.emit(video_id, final_path)

                    # Log download
                    config_manager.add_to_history({
                        'id': video_id,
                        'title': title,
                        'url': video_url,
                        'local_path': final_path,
                        'type': 'download'
                    })
                else:
                    self.download_error.emit(video_id, "Could not retrieve video info.")

        except Exception as e:
            logger.error(f"Download failed for {video_id}: {e}")
            self.download_error.emit(video_id, str(e))

        finally:
            with self._lock:
                if video_id in self._active_downloads:
                    del self._active_downloads[video_id]
            # Try to start next on main thread (via signal or direct if safe)
            # Since QTimer runs it, we can also just wait for the next tick,
            # but we can safely call it directly too.
            self._process_queue()

download_manager = DownloadManager()
