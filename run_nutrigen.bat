@echo off
title NutriGEN-AI Server & Frontend Launcher
color 0A

echo ========================================================
echo           Starting NutriGEN-AI System...
echo ========================================================

:: Navigate to the true repository directory where server.py and Frontend exist
cd /d "C:\Users\abhi\Desktop\NutriGEN-AI\NutriGEN-AI"

:: Check if port 8000 is occupied and free it if necessary
echo Checking port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo Freeing port 8000 (Process ID: %%a)...
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo Launching NutriGEN-AI FastAPI Server with Frontend mounted at http://localhost:8000 ...
echo.
start "" "http://localhost:8000"
python -m uvicorn Backend.server:app --reload --port 8000
pause
