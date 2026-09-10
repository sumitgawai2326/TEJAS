@echo off
setlocal enabledelayedexpansion

title TEJAS - Demo Launcher
cls

echo ======================================================================
echo    TEJAS - Technology Enabled Judicious Agriculture And soil sensor
echo                 Smart India Hackathon 2026 Prototype
echo ======================================================================
echo.
echo  [1/4] Checking Python Virtual Environment...
if exist "backend\.venv\Scripts\python.exe" (
    echo       Found: backend\.venv\Scripts\python.exe
) else (
    echo       [WARNING] backend\.venv not found! Checking fallback python...
)

echo.
echo  [2/4] Checking Frontend Dependencies...
if exist "frontend\node_modules" (
    echo       Found: frontend\node_modules
) else (
    echo       [INFO] Running npm install in frontend...
    cd frontend && call npm install && cd ..
)

echo.
echo  [3/4] Launching TEJAS Backend (FastAPI + YOLO11n AI + SQLite)...
start "TEJAS Backend Server (FastAPI on Port 8000)" cmd /k "cd backend && .venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

echo.
echo  [4/4] Launching TEJAS Frontend (Vite on Port 5173)...
start "TEJAS Frontend Web Shell (Vite on Port 5173)" cmd /k "cd frontend && npm run dev"

echo.
echo ======================================================================
echo    TEJAS Demo Environment is starting!
echo.
echo    Backend API:     http://127.0.0.1:8000
echo    API Docs:        http://127.0.0.1:8000/docs
echo    Frontend Shell:  http://localhost:5173
echo.
echo    Opening http://localhost:5173 in default browser...
echo ======================================================================
echo.

timeout /t 4 /nobreak >nul
start http://localhost:5173

echo Close the individual server command windows when you wish to stop TEJAS.
echo.
pause
