#!/bin/sh
# Builds the app for the computer you run it on (macOS / Linux).  Run:  sh build.sh
python3 -m pip install --upgrade pygame pyinstaller || exit 1
python3 -m PyInstaller --noconfirm --clean --onefile --windowed --name KwinsGreatAdventure --add-data "assets:assets" main.py || exit 1
echo "Done! Your app is in the dist/ folder."
