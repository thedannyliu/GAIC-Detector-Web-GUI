#!/bin/bash

# GAIC Detector - Start Script
# Starts both backend API and frontend UI

set -e

echo "🚀 Starting GAIC Detector Web GUI..."

# Check for conda
if ! command -v conda &> /dev/null; then
    echo "❌ Conda not found. Please install Conda or run setup.sh first."
    exit 1
fi

# Activate conda environment
ENV_NAME="gaic-detector"
eval "$(conda shell.bash hook)"
conda activate $ENV_NAME

# Start backend API in background
echo "📡 Starting backend API on port 8000..."
python -m app.main &
API_PID=$!

# Wait for API to be ready
echo "⏳ Waiting for API to start..."
sleep 5

# Check if API is running
if ! curl -s http://localhost:8000/ > /dev/null; then
    echo "❌ Failed to start backend API"
    kill $API_PID 2>/dev/null || true
    exit 1
fi

echo "✅ Backend API is running (PID: $API_PID)"

# Start frontend UI
echo "🎨 Starting frontend UI on port 7860..."
python gradio_app.py &
UI_PID=$!

echo ""
echo "✅ GAIC Detector is running!"
echo ""
echo "📍 Access the application at:"
echo "   Frontend UI:  http://localhost:7860"
echo "   API Docs:     http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both services..."
echo ""

# Wait for user interrupt
trap "echo ''; echo '🛑 Stopping services...'; kill $API_PID $UI_PID 2>/dev/null || true; echo '✅ Services stopped'; exit 0" INT

# Keep script running
wait
