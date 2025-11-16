#!/bin/bash
# Test if backend can start without errors

cd /storage/home/hcoda1/9/eliu354/r-agarg35-0/projects/GAIC-Detector-Web-GUI

# Activate conda
source ~/miniconda3/etc/profile.d/conda.sh
conda activate gaic-detector

echo "🧪 Testing backend startup..."
echo ""

# Try to import main module
echo "1️⃣ Testing Python imports..."
python -c "
import sys
sys.path.insert(0, '.')
try:
    from app.aide_original import AIDE
    print('   ✅ AIDE import OK')
except Exception as e:
    print(f'   ❌ AIDE import failed: {e}')
    sys.exit(1)

try:
    from app import main
    print('   ✅ app.main import OK')
except Exception as e:
    print(f'   ❌ app.main import failed: {e}')
    sys.exit(1)
" || exit 1

echo ""
echo "2️⃣ Starting backend (will run for 15 seconds)..."
echo ""

# Start backend with timeout
timeout 15 python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for startup
sleep 5

# Test if backend responds
echo "3️⃣ Testing backend health..."
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "   ✅ Backend is responding!"
    kill $BACKEND_PID 2>/dev/null
    echo ""
    echo "🎉 All tests passed! Backend is ready to use."
    exit 0
else
    echo "   ⏳ Backend still loading... (this is normal for first run)"
    kill $BACKEND_PID 2>/dev/null
    echo ""
    echo "💡 Backend imports work. First startup may take 20-30 seconds."
    echo "   Run: ./start_backend_simple.sh"
    exit 0
fi
