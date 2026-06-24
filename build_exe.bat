@echo off
chcp 65001 >nul
echo Установка зависимостей...
pip install -r requirements.txt
pip install pyinstaller

echo Сборка .exe...
pyinstaller --onefile --name "ViewerTracker" --distpath "." src\main.py

echo Очистка временных файлов сборки...
if exist "build" rmdir /s /q "build"
if exist "*.spec" del /q "*.spec"

echo Готово! .exe в папке проекта: ViewerTracker.exe
pause
