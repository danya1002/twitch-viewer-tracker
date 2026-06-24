@echo off
chcp 65001 >nul
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --onefile --name "ViewerTracker" --distpath "." src\main.py
if exist "build" rmdir /s /q "build"
if exist "*.spec" del /q "*.spec"
echo Done. ViewerTracker.exe created.
pause
