# YouTube Desktop App PyInstaller Build Script
import PyInstaller.__main__
import os
import platform

print("Starting build process for YouTube Desktop...")

project_root = os.path.dirname(os.path.abspath(__file__))
main_script = os.path.join(project_root, "src", "main.py")
locales_dir = os.path.join(project_root, "src", "locales")

# Handle OS specific path separator for PyInstaller data
separator = ';' if platform.system() == "Windows" else ':'

PyInstaller.__main__.run([
    main_script,
    '--name=YouTubeDesktop',
    '--windowed',         # No console window
    '--onefile',          # Bundle everything into a SINGLE executable! (Solves the missing file issue)
    '--noconfirm',
    '--clean',
    '--log-level=WARN',

    # Include all our custom Python modules
    f'--paths={os.path.join(project_root, "src")}',

    # Include the language dictionary JSON files!
    f'--add-data={locales_dir}{separator}locales',
])

print("\n\n=== BUILD COMPLETED ===")
print(f"You can find the standalone application inside the 'dist/' folder.")
