#!/bin/bash

echo "========================================"
echo "  云数据中心资源调度模拟器 - 启动脚本"
echo "========================================"
echo

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
VENV_DIR="$BACKEND_DIR/.venv"
BACKEND_MARKER="$BACKEND_DIR/.deps_installed"
FRONTEND_MARKER="$FRONTEND_DIR/.deps_installed"

BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
    echo
    echo "正在停止服务..."
    if [ -n "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        wait $BACKEND_PID 2>/dev/null
    fi
    if [ -n "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        wait $FRONTEND_PID 2>/dev/null
    fi
    echo "服务已停止"
    exit 0
}

trap cleanup SIGINT SIGTERM

echo "[1/4] 检查后端依赖..."
if [ ! -d "$VENV_DIR" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "错误: 无法创建虚拟环境，请确保Python3已安装"
        exit 1
    fi
fi

if [ ! -f "$BACKEND_MARKER" ]; then
    echo "安装后端依赖..."
    "$VENV_DIR/bin/pip" install -r "$BACKEND_DIR/requirements.txt"
    if [ $? -ne 0 ]; then
        echo "错误: 后端依赖安装失败"
        exit 1
    fi
    touch "$BACKEND_MARKER"
fi
echo "后端依赖已就绪"

echo
echo "[2/4] 检查前端依赖..."
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo "安装前端依赖..."
    cd "$FRONTEND_DIR"
    npm install
    if [ $? -ne 0 ]; then
        echo "错误: 前端依赖安装失败"
        exit 1
    fi
    touch "$FRONTEND_MARKER"
fi
echo "前端依赖已就绪"

echo
echo "[3/4] 启动后端服务..."
cd "$BACKEND_DIR"
"$VENV_DIR/bin/uvicorn" app.main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

echo "[4/4] 启动前端服务..."
echo
echo "========================================"
echo "  服务启动中..."
echo "========================================"
echo
echo "  后端: http://127.0.0.1:8000"
echo "  前端: http://127.0.0.1:5173"
echo
echo "  按 Ctrl+C 停止所有服务"
echo "========================================"
echo

cd "$FRONTEND_DIR"
npm run dev &
FRONTEND_PID=$!

wait $FRONTEND_PID