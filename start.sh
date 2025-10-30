#!/bin/bash

# GAIC Detector - Start Script
# Starts both backend API and frontend UI

echo "🚀 Starting GAIC Detector Web GUI..."

# Check for conda
if ! command -v conda &> /dev/null; then
    echo "❌ Conda not found. Please install Conda or run setup.sh first."
    exit 1
fi

# Activate conda environment
ENV_NAME="gaic-detector"
eval "$(conda shell.bash hook)"

# Check if environment exists
if ! conda env list | grep -q "^${ENV_NAME} "; then
    echo "❌ Conda environment '${ENV_NAME}' not found. Please run ./setup.sh first."
    exit 1
fi

conda activate $ENV_NAME

# Verify activation
if [ "$CONDA_DEFAULT_ENV" != "$ENV_NAME" ]; then
    echo "❌ Failed to activate conda environment"
    exit 1
fi

echo "✅ Using conda environment: $CONDA_DEFAULT_ENV"
echo "✅ Python: $(which python)"

# Start backend API in background
echo "📡 Starting backend API on port 8000..."
python -m app.main > /tmp/gaic_backend.log 2>&1 &
API_PID=$!

# Wait for API to be ready with retry
echo "⏳ Waiting for API to start..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    sleep 1
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    
    # Check if process is still running
    if ! kill -0 $API_PID 2>/dev/null; then
        echo "❌ Backend API process died. Check logs:"
        tail -20 /tmp/gaic_backend.log
        exit 1
    fi
done

# Final check
if ! curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "❌ Failed to start backend API after ${MAX_RETRIES} seconds"
    echo "📋 Last 20 lines of backend log:"
    tail -20 /tmp/gaic_backend.log
    kill $API_PID 2>/dev/null || true
    exit 1
fi

echo "✅ Backend API is running (PID: $API_PID)"
echo "📋 Backend logs: /tmp/gaic_backend.log"

# Start frontend UI
echo "🎨 Starting frontend UI on port 7860..."
python gradio_app.py > /tmp/gaic_frontend.log 2>&1 &
UI_PID=$!

# Wait a moment for frontend to start
sleep 3

echo ""
echo "✅ GAIC Detector is running!"
echo ""
echo "📍 Access the application at:"
echo "   Frontend UI:  http://localhost:7860"
echo "   API Docs:     http://localhost:8000/docs"
echo ""
echo "📋 Logs:"
echo "   Backend:  tail -f /tmp/gaic_backend.log"
echo "   Frontend: tail -f /tmp/gaic_frontend.log"
echo ""
echo "Press Ctrl+C to stop both services..."
echo ""

# Wait for user interrupt
trap "echo ''; echo '🛑 Stopping services...'; kill $API_PID $UI_PID 2>/dev/null || true; sleep 2; echo '✅ Services stopped'; exit 0" INT

# Keep script running and show that we're alive
while true; do
    # Check if processes are still running
    if ! kill -0 $API_PID 2>/dev/null; then
        echo "❌ Backend API stopped unexpectedly"
        kill $UI_PID 2>/dev/null || true
        exit 1
    fi
    if ! kill -0 $UI_PID 2>/dev/null; then
        echo "❌ Frontend UI stopped unexpectedly"
        kill $API_PID 2>/dev/null || true
        exit 1
    fi
    sleep 5
done
