# YouTube Desktop App PyInstaller Build Script
import PyInstaller.__main__
import os

print("Starting build process for YouTube Desktop...")

project_root = os.path.dirname(os.path.abspath(__file__))
main_script = os.path.join(project_root, "src", "main.py")
locales_dir = os.path.join(project_root, "src", "locales")

# Handle OS specific path separator for PyInstaller data correctly using os.pathsep
separator = os.pathsep

# Remove old spec file to prevent hardcoded paths from breaking the build
spec_file = os.path.join(project_root, "YouTubeDesktop.spec")
if os.path.exists(spec_file):
    try:
        os.remove(spec_file)
        print("Removed old .spec file to ensure clean build.")
    except Exception as e:
        print(f"Warning: Could not remove {spec_file}: {e}")

PyInstaller.__main__.run([
    main_script,
    '--name=YouTubeDesktop',
    '--windowed',         # No console window
    '--onefile',          # Bundle everything into a SINGLE executable!
    '--noconfirm',
    '--clean',
    '--log-level=WARN',

    # Include all our custom Python modules
    f'--paths={os.path.join(project_root, "src")}',

    # Include the language dictionary JSON files
    f'--add-data={locales_dir}{separator}locales',
])

print("\n\n=== BUILD COMPLETED ===")
print(f"You can find the standalone application inside the 'dist/' folder.")
