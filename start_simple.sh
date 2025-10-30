#!/bin/bash

# GAIC Detector - Simple Start Script
# Run with: ./start.sh
# Note: Ensure you've activated the conda environment first with:
#   conda activate gaic-detector

echo "🚀 Starting GAIC Detector Web GUI..."
echo ""

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Check if we're in the right conda environment
if [ "$CONDA_DEFAULT_ENV" != "gaic-detector" ]; then
    echo "⚠️  Warning: Not in 'gaic-detector' conda environment"
    echo "   Current environment: ${CONDA_DEFAULT_ENV:-none}"
    echo ""
    echo "Please activate the environment first:"
    echo "   conda activate gaic-detector"
    echo "   ./start.sh"
    exit 1
fi

echo "✅ Using conda environment: $CONDA_DEFAULT_ENV"
echo "✅ Python: $(which python)"
echo "✅ Python version: $(python --version)"
echo ""

# Check if ports are already in use
if check_port 8000; then
    echo "⚠️  Port 8000 is already in use"
    echo "   Stop the existing service or use: lsof -ti:8000 | xargs kill -9"
    exit 1
fi

if check_port 7860; then
    echo "⚠️  Port 7860 is already in use"
    echo "   Stop the existing service or use: lsof -ti:7860 | xargs kill -9"
    exit 1
fi

# Start backend API
echo "📡 Starting backend API on port 8000..."
python -m app.main > /tmp/gaic_backend.log 2>&1 &
API_PID=$!
echo "   Backend PID: $API_PID"

# Wait for API to start
echo "⏳ Waiting for backend API to start..."
for i in {1..30}; do
    sleep 1
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        echo "✅ Backend API is ready!"
        break
    fi
    
    # Check if process died
    if ! kill -0 $API_PID 2>/dev/null; then
        echo "❌ Backend API failed to start"
        echo ""
        echo "📋 Error logs:"
        tail -30 /tmp/gaic_backend.log
        exit 1
    fi
    
    # Show progress
    if [ $((i % 5)) -eq 0 ]; then
        echo "   Still waiting... ($i/30 seconds)"
    fi
done

# Final check
if ! curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "❌ Backend API did not start within 30 seconds"
    echo ""
    echo "📋 Last 30 lines of backend log:"
    tail -30 /tmp/gaic_backend.log
    kill $API_PID 2>/dev/null || true
    exit 1
fi

echo ""

# Start frontend UI
echo "🎨 Starting frontend UI on port 7860..."
python gradio_app.py > /tmp/gaic_frontend.log 2>&1 &
UI_PID=$!
echo "   Frontend PID: $UI_PID"

# Wait a bit for frontend
echo "⏳ Waiting for frontend UI to start..."
sleep 5

# Check if frontend is responsive
for i in {1..10}; do
    if curl -s http://localhost:7860/ > /dev/null 2>&1; then
        echo "✅ Frontend UI is ready!"
        break
    fi
    
    if ! kill -0 $UI_PID 2>/dev/null; then
        echo "❌ Frontend UI failed to start"
        echo ""
        echo "📋 Error logs:"
        tail -30 /tmp/gaic_frontend.log
        kill $API_PID 2>/dev/null || true
        exit 1
    fi
    
    sleep 1
done

echo ""
echo "=========================================="
echo "✅ GAIC Detector is running!"
echo "=========================================="
echo ""
echo "📍 Access points:"
echo "   🎨 Frontend UI:  http://localhost:7860"
echo "   📚 API Docs:     http://localhost:8000/docs"
echo "   ❤️  Health Check: http://localhost:8000/"
echo ""
echo "📋 Logs:"
echo "   Backend:  tail -f /tmp/gaic_backend.log"
echo "   Frontend: tail -f /tmp/gaic_frontend.log"
echo ""
echo "🛑 To stop:"
echo "   Press Ctrl+C in this terminal"
echo "   Or run: kill $API_PID $UI_PID"
echo ""
echo "=========================================="
echo ""

# Setup trap for clean shutdown
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    kill $UI_PID 2>/dev/null && echo "   ✓ Stopped frontend (PID: $UI_PID)" || true
    kill $API_PID 2>/dev/null && echo "   ✓ Stopped backend (PID: $API_PID)" || true
    sleep 2
    
    # Force kill if still running
    kill -9 $UI_PID 2>/dev/null || true
    kill -9 $API_PID 2>/dev/null || true
    
    echo "✅ Services stopped"
    exit 0
}

trap cleanup INT TERM

# Monitor processes
echo "Monitoring services... (Press Ctrl+C to stop)"
while true; do
    if ! kill -0 $API_PID 2>/dev/null; then
        echo ""
        echo "❌ Backend API stopped unexpectedly!"
        echo "📋 Last 20 lines of log:"
        tail -20 /tmp/gaic_backend.log
        kill $UI_PID 2>/dev/null || true
        exit 1
    fi
    
    if ! kill -0 $UI_PID 2>/dev/null; then
        echo ""
        echo "❌ Frontend UI stopped unexpectedly!"
        echo "📋 Last 20 lines of log:"
        tail -20 /tmp/gaic_frontend.log
        kill $API_PID 2>/dev/null || true
        exit 1
    fi
    
    sleep 5
done
