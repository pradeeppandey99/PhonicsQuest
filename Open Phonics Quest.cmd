@echo off
REM Opens Phonics Quest in your browser. Keep this window open while you play; close it to stop.
REM Recordings are saved in the "sounds" folder by server.py, so nothing is lost if the browser is cleared.
cd /d "%~dp0"
start "" http://localhost:8766/index.html
python server.py 8766
