@echo off
setlocal enabledelayedexpansion

echo ========================================
echo   Cloud Scheduler Simulator - Start
echo ========================================
echo.

set "ROOT_DIR=%~dp0"
set "BACKEND_DIR=%ROOT_DIR%backend"
set "FRONTEND_DIR=%ROOT_DIR%frontend"
set "VENV_DIR=%BACKEND_DIR%\.venv"

echo [1/4] Checking backend dependencies...
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo Creating Python virtual environment...
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo Error: Cannot create virtual environment. Please ensure Python is installed.
        pause
        exit /b 1
    )
)

if not exist "%VENV_DIR%\Lib\site-packages\fastapi" (
    echo Installing backend dependencies...
    "%VENV_DIR%\Scripts\pip.exe" install -r "%BACKEND_DIR%\requirements.txt"
    if errorlevel 1 (
        echo Error: Backend dependencies installation failed.
        pause
        exit /b 1
    )
)
echo Backend dependencies ready.

echo.
echo [2/4] Checking frontend dependencies...
if not exist "%FRONTEND_DIR%\node_modules" (
    echo Installing frontend dependencies...
    cd /d "%FRONTEND_DIR%"
    call npm install
    if errorlevel 1 (
        echo Error: Frontend dependencies installation failed.
        pause
        exit /b 1
    )
)
echo Frontend dependencies ready.

echo.
echo [3/4] Starting backend service...
cd /d "%BACKEND_DIR%"
start "CloudScheduler-Backend" /min "%VENV_DIR%\Scripts\uvicorn.exe" app.main:app --reload --host 127.0.0.1 --port 8000

echo [4/4] Starting frontend service...
echo.
echo ========================================
echo   Services starting...
echo ========================================
echo.
echo   Backend: http://127.0.0.1:8000
echo   Frontend: http://127.0.0.1:5173
echo.
echo   Press Ctrl+C to stop all services
echo ========================================
echo.

cd /d "%FRONTEND_DIR%"
call npm run dev

echo.
echo Stopping services...
taskkill /f /fi "WindowTitle eq CloudScheduler-Backend*" >nul 2>&1
echo Services stopped.
pause
