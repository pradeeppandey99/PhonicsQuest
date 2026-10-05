@echo off
REM Opens Phonics Quest in your browser. Keep this window open while you play; close it to stop.
cd /d "%~dp0"
start "" http://localhost:8765/index.html
python -m http.server 8765
