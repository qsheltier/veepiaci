import PyInstaller.__main__

PyInstaller.__main__.run([
    "--windowed",
    "--noconfirm",
    "--icon", "icons/veepiaci-icon.ico",
    "--icon", "icons/veepiaci-icon.icns",
    "veepiaci.py"
])
