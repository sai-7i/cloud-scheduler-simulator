@echo off
setlocal enabledelayedexpansion

echo ========================================
echo   云数据中心资源调度模拟器 - 启动脚本
echo ========================================
echo.

set "ROOT_DIR=%~dp0"
set "BACKEND_DIR=%ROOT_DIR%backend"
set "FRONTEND_DIR=%ROOT_DIR%frontend"
set "VENV_DIR=%BACKEND_DIR%\.venv"
set "BACKEND_MARKER=%BACKEND_DIR%\.deps_installed"
set "FRONTEND_MARKER=%FRONTEND_DIR%\.deps_installed"

echo [1/4] 检查后端依赖...
if not exist "%VENV_DIR%" (
    echo 创建Python虚拟环境...
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo 错误: 无法创建虚拟环境，请确保Python已安装
        pause
        exit /b 1
    )
)

if not exist "%BACKEND_MARKER%" (
    echo 安装后端依赖...
    "%VENV_DIR%\Scripts\pip.exe" install -r "%BACKEND_DIR%\requirements.txt"
    if errorlevel 1 (
        echo 错误: 后端依赖安装失败
        pause
        exit /b 1
    )
    echo. > "%BACKEND_MARKER%"
)
echo 后端依赖已就绪

echo.
echo [2/4] 检查前端依赖...
if not exist "%FRONTEND_DIR%\node_modules" (
    echo 安装前端依赖...
    cd /d "%FRONTEND_DIR%"
    call npm install
    if errorlevel 1 (
        echo 错误: 前端依赖安装失败
        pause
        exit /b 1
    )
    echo. > "%FRONTEND_MARKER%"
)
echo 前端依赖已就绪

echo.
echo [3/4] 启动后端服务...
start "CloudScheduler-Backend" /min cmd /c "cd /d "%BACKEND_DIR%" && "%VENV_DIR%\Scripts\uvicorn.exe" app.main:app --reload --host 127.0.0.1 --port 8000"

echo [4/4] 启动前端服务...
echo.
echo ========================================
echo   服务启动中...
echo ========================================
echo.
echo   后端: http://127.0.0.1:8000
echo   前端: http://127.0.0.1:5173
echo.
echo   按 Ctrl+C 停止所有服务
echo ========================================
echo.

cd /d "%FRONTEND_DIR%"
call npm run dev

echo.
echo 正在停止服务...
taskkill /f /fi "WindowTitle eq CloudScheduler-Backend*" >nul 2>&1
echo 服务已停止
pause