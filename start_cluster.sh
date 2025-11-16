#!/bin/bash

# GAIC Detector - Cluster Start Script (with Gradio Share)
# For use on GPU clusters like PACE Phoenix
# This enables Gradio's share feature to get a public URL

echo "🚀 Starting GAIC Detector Web GUI (Cluster Mode)..."
echo ""

# Check if we're in the right conda environment
if [ "$CONDA_DEFAULT_ENV" != "gaic-detector" ]; then
    echo "⚠️  Warning: Not in 'gaic-detector' conda environment"
    echo "   Current environment: ${CONDA_DEFAULT_ENV:-none}"
    echo ""
    echo "Please activate the environment first:"
    echo "   conda activate gaic-detector"
    echo "   ./start_cluster.sh"
    exit 1
fi

echo "✅ Using conda environment: $CONDA_DEFAULT_ENV"
echo "✅ Python: $(which python)"
echo "✅ Node: $(hostname)"
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

# Check if ports are already in use
if check_port 8000; then
    echo "⚠️  Port 8000 is already in use"
    read -p "Kill existing process? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        lsof -ti:8000 | xargs kill -9
        sleep 2
    else
        exit 1
    fi
fi

if check_port 7860; then
    echo "⚠️  Port 7860 is already in use"
    read -p "Kill existing process? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        lsof -ti:7860 | xargs kill -9
        sleep 2
    else
        exit 1
    fi
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
    
    if ! kill -0 $API_PID 2>/dev/null; then
        echo "❌ Backend API failed to start"
        echo ""
        echo "📋 Error logs:"
        tail -30 /tmp/gaic_backend.log
        exit 1
    fi
    
    if [ $((i % 5)) -eq 0 ]; then
        echo "   Still waiting... ($i/30 seconds)"
    fi
done

if ! curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "❌ Backend API did not start within 30 seconds"
    kill $API_PID 2>/dev/null || true
    exit 1
fi

echo ""

# Start frontend UI with share enabled
echo "🎨 Starting frontend UI with public URL..."
echo "   (This will create a temporary Gradio share link)"
echo ""

# Enable Gradio sharing
export GRADIO_SHARE=true

python gradio_app.py > /tmp/gaic_frontend.log 2>&1 &
UI_PID=$!
echo "   Frontend PID: $UI_PID"

# Wait and extract the share URL
echo "⏳ Waiting for Gradio to generate share URL..."
echo "   (This may take 10-20 seconds)"
echo ""

for i in {1..60}; do
    sleep 1
    
    # Check if process died
    if ! kill -0 $UI_PID 2>/dev/null; then
        echo "❌ Frontend UI failed to start"
        echo ""
        echo "📋 Error logs:"
        tail -30 /tmp/gaic_frontend.log
        kill $API_PID 2>/dev/null || true
        exit 1
    fi
    
    # Look for Gradio share URL in logs
    if grep -q "Running on public URL:" /tmp/gaic_frontend.log; then
        break
    fi
    
    if [ $((i % 10)) -eq 0 ]; then
        echo "   Still generating... ($i/60 seconds)"
    fi
done

echo ""
echo "=========================================="
echo "✅ GAIC Detector is running!"
echo "=========================================="
echo ""

# Extract and display URLs
if grep -q "Running on local URL:" /tmp/gaic_frontend.log; then
    LOCAL_URL=$(grep "Running on local URL:" /tmp/gaic_frontend.log | tail -1 | awk '{print $NF}')
    echo "🏠 Local URL (on cluster node):"
    echo "   $LOCAL_URL"
    echo ""
fi

if grep -q "Running on public URL:" /tmp/gaic_frontend.log; then
    PUBLIC_URL=$(grep "Running on public URL:" /tmp/gaic_frontend.log | tail -1 | awk '{print $NF}')
    echo "🌐 Public URL (accessible from anywhere):"
    echo "   $PUBLIC_URL"
    echo ""
    echo "   ⭐ Use this URL to access from your local computer!"
    echo ""
else
    echo "⚠️  Public URL not found. Showing alternative access methods..."
    echo ""
fi

echo "📍 Backend API:"
echo "   Health Check: http://localhost:8000/"
echo "   API Docs:     http://localhost:8000/docs"
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

# If no public URL, show SSH tunneling instructions
if ! grep -q "Running on public URL:" /tmp/gaic_frontend.log; then
    echo "💡 Alternative: Use SSH Port Forwarding"
    echo "=========================================="
    echo ""
    echo "On your local computer, run:"
    echo ""
    echo "ssh -L 7860:$(hostname):7860 -L 8000:$(hostname):8000 eliu354@login-phoenix.pace.gatech.edu"
    echo ""
    echo "Then visit: http://localhost:7860"
    echo ""
    echo "=========================================="
    echo ""
fi

# Setup trap for clean shutdown
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    kill $UI_PID 2>/dev/null && echo "   ✓ Stopped frontend (PID: $UI_PID)" || true
    kill $API_PID 2>/dev/null && echo "   ✓ Stopped backend (PID: $API_PID)" || true
    sleep 2
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
        kill $UI_PID 2>/dev/null || true
        exit 1
    fi
    
    if ! kill -0 $UI_PID 2>/dev/null; then
        echo ""
        echo "❌ Frontend UI stopped unexpectedly!"
        kill $API_PID 2>/dev/null || true
        exit 1
    fi
    
    sleep 5
done
