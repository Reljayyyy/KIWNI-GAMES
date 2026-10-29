@echo off
REM Builds KwinsGreatAdventure.exe (Windows). Run from inside this folder:  build.bat
echo Installing build tools...
python -m pip install --upgrade pygame pyinstaller
if errorlevel 1 goto fail
echo.
echo Building the app (this takes a minute or two)...
python -m PyInstaller --noconfirm --clean --onefile --windowed --name KwinsGreatAdventure --icon assets\icon.ico --add-data "assets;assets" main.py
if errorlevel 1 goto fail
echo.
echo ================================================================
echo  Done!  Your app is:  dist\KwinsGreatAdventure.exe
echo  Share that one file (zip it first if you send it by email).
echo ================================================================
pause
exit /b 0
:fail
echo.
echo Something went wrong - scroll up to read the error.
pause
exit /b 1
