import PyInstaller.__main__
import os

project_root = os.path.dirname(os.path.abspath(__file__))
main_script = os.path.join(project_root, "src", "main.py")
locales_dir = os.path.join(project_root, "src", "locales")

PyInstaller.__main__.run([
    main_script,
    '--name=YouTubeDesktop',
    '--noconfirm',
    '--clean',
    '--log-level=ERROR',
    f'--paths={os.path.join(project_root, "src")}',
    f'--add-data={locales_dir}:locales',  # Include translation files in the build!
])
print("Build test complete.")
