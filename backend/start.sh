#!/bin/bash
echo "🔍 Checking for running backend..."
OLD_PID=$(lsof -ti :8000 2>/dev/null)
if [ ! -z "$OLD_PID" ]; then
    echo "🛑 Killing old process: $OLD_PID"
    kill $OLD_PID
    sleep 1
fi

# Check if port is free
if lsof -i :8000 >/dev/null 2>&1; then
    echo "❌ Port 8000 still in use!"
    exit 1
fi

# Activate venv and start
echo "🚀 Starting backend..."
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

