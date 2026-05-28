#!/bin/bash

echo "========================================"
echo "  Cloud Scheduler Simulator - Start"
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
    echo "Stopping services..."
    if [ -n "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        wait $BACKEND_PID 2>/dev/null
    fi
    if [ -n "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        wait $FRONTEND_PID 2>/dev/null
    fi
    echo "Services stopped."
    exit 0
}

trap cleanup SIGINT SIGTERM

echo "[1/4] Checking backend dependencies..."
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "Error: Cannot create virtual environment. Please ensure Python3 is installed."
        exit 1
    fi
fi

if [ ! -f "$BACKEND_MARKER" ]; then
    echo "Installing backend dependencies..."
    "$VENV_DIR/bin/pip" install -r "$BACKEND_DIR/requirements.txt"
    if [ $? -ne 0 ]; then
        echo "Error: Backend dependencies installation failed."
        exit 1
    fi
    touch "$BACKEND_MARKER"
fi
echo "Backend dependencies ready."

echo
echo "[2/4] Checking frontend dependencies..."
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd "$FRONTEND_DIR"
    npm install
    if [ $? -ne 0 ]; then
        echo "Error: Frontend dependencies installation failed."
        exit 1
    fi
    touch "$FRONTEND_MARKER"
fi
echo "Frontend dependencies ready."

echo
echo "[3/4] Starting backend service..."
cd "$BACKEND_DIR"
"$VENV_DIR/bin/uvicorn" app.main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

echo "[4/4] Starting frontend service..."
echo
echo "========================================"
echo "  Services starting..."
echo "========================================"
echo
echo "  Backend: http://127.0.0.1:8000"
echo "  Frontend: http://127.0.0.1:5173"
echo
echo "  Press Ctrl+C to stop all services"
echo "========================================"
echo

cd "$FRONTEND_DIR"
npm run dev &
FRONTEND_PID=$!

wait $FRONTEND_PID
