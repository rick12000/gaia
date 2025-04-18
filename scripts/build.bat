@echo off
echo Cleaning up previous builds...
rmdir /s /q build
rmdir /s /q dist
del /q gaia.spec

echo Running PyInstaller...
pyinstaller --onefile --windowed --noconfirm ^
--add-data "vosk-model-small-en-us-0.15;vosk-model-small-en-us-0.15" ^
--add-data "LICENSE;." ^
--add-data "README.md;." ^
--add-data "C:\Users\ricca\miniconda3\envs\gaia_env\Lib\site-packages\vosk;vosk" ^
src/gaia.py

echo Build process completed.
echo The executable can be found in the 'dist' folder.
pause