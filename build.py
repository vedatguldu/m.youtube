# YouTube Desktop App PyInstaller Build Script
import PyInstaller.__main__
import os

print("Starting build process for YouTube Desktop...")

# Define output path and paths to include
project_root = os.path.dirname(os.path.abspath(__file__))
main_script = os.path.join(project_root, "src", "main.py")

PyInstaller.__main__.run([
    main_script,
    '--name=YouTubeDesktop',
    '--windowed',         # No console window (macOS/Windows)
    '--noconfirm',        # Overwrite existing build
    '--clean',            # Clean PyInstaller cache
    '--log-level=WARN',

    # We include our sources inside the executable to avoid missing paths
    f'--paths={os.path.join(project_root, "src")}',

    # Optionally, include any assets if we had icons
    # '--add-data=src/assets:assets',
])

print("Build completed! Check the 'dist' folder.")
