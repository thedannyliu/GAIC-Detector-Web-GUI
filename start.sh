#!/bin/bash
# GAIC Detector – Service Launcher
# Launches the FastAPI backend and Gradio frontend.
# Run this on a GPU compute node (not the login node).
#
# Usage:
#   ./start.sh           # Start all services (default)
#   ./start.sh backend   # Start backend only
#   ./start.sh frontend  # Start frontend only
#   ./start.sh stop      # Stop all running services

set -e

# Ensure logs directory exists
mkdir -p logs

# ── Colour helpers ─────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC}   $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()     { echo -e "${RED}[ERR]${NC}  $1"; }

# ── Detect GPU ─────────────────────────────────────────────────
check_gpu() {
    info "Checking GPU availability..."
    if command -v nvidia-smi &>/dev/null; then
        nvidia-smi --query-gpu=index,name,memory.total,memory.free --format=csv,noheader
        success "GPU detected."
        return 0
    else
        warn "nvidia-smi not found – will run in CPU mode."
        return 1
    fi
}

# ── Check PyTorch CUDA ─────────────────────────────────────────
check_pytorch_cuda() {
    info "Checking PyTorch CUDA support..."
    python - <<'EOF'
import torch
print(f"  PyTorch : {torch.__version__}")
print(f"  CUDA    : {torch.cuda.is_available()} ({torch.version.cuda if torch.cuda.is_available() else 'N/A'})")
print(f"  Devices : {torch.cuda.device_count()}")
for i in range(torch.cuda.device_count()):
    print(f"    GPU {i}: {torch.cuda.get_device_name(i)}")
EOF
    [ $? -eq 0 ] && success "PyTorch check passed." || { err "PyTorch check failed. See https://pytorch.org for installation."; exit 1; }
}

# ── Auto-cleanup old processes ─────────────────────────────────
auto_cleanup() {
    # Kill any leftover backend/frontend processes from previous runs
    if pgrep -f "uvicorn app.main:app" > /dev/null 2>&1; then
        warn "Found stale backend process – killing it."
        pkill -f "uvicorn app.main:app" 2>/dev/null || true
        sleep 1
    fi
    if pgrep -f "gradio_app.py" > /dev/null 2>&1; then
        warn "Found stale frontend process – killing it."
        pkill -f "gradio_app.py" 2>/dev/null || true
        sleep 1
    fi
    # Clean up stale PID files
    rm -f logs/backend.pid logs/frontend.pid
}

# ── Start backend ──────────────────────────────────────────────
start_backend() {
    info "Starting FastAPI backend (port 8000)..."
    export CUDA_VISIBLE_DEVICES=0

    nohup uvicorn app.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --timeout-keep-alive 120 \
        > logs/backend.log 2>&1 &

    BACKEND_PID=$!
    echo "$BACKEND_PID" > logs/backend.pid
    success "Backend started (PID $BACKEND_PID). Logs: logs/backend.log"

    # Wait for backend to become ready (model loading takes time)
    info "Waiting for backend to become ready (model is ~3.6 GB, may take 30–60 s)..."
    for i in $(seq 1 60); do
        kill -0 "$BACKEND_PID" 2>/dev/null || { err "Backend process died. Check logs/backend.log."; exit 1; }
        curl -sf --max-time 2 http://localhost:8000/ >/dev/null 2>&1 && { success "Backend ready (${i}s)."; break; }
        [ "$i" -eq 60 ] && { err "Backend did not start in 60 s. Check logs/backend.log."; exit 1; }
        printf .
        sleep 1
    done
    echo ""
}

# ── Start frontend ─────────────────────────────────────────────
start_frontend() {
    info "Starting Gradio frontend (port 7860)..."

    # Enable Gradio public share link unconditionally
    info "Enabling Gradio share link for direct web access."
    export GRADIO_SHARE=true

    nohup python -u gradio_app.py > logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "$FRONTEND_PID" > logs/frontend.pid
    success "Frontend started (PID $FRONTEND_PID). Logs: logs/frontend.log"

    # Wait for frontend by checking logs for the start message
    for i in $(seq 1 30); do
        kill -0 "$FRONTEND_PID" 2>/dev/null || { err "Frontend process died. Check logs/frontend.log."; exit 1; }
        grep -q "Running on" logs/frontend.log && { success "Frontend ready (${i}s)."; break; }
        [ "$i" -eq 30 ] && { err "Frontend did not start in 30 s. Check logs/frontend.log."; exit 1; }
        printf .
        sleep 1
    done
    echo ""
}

# ── Stop services ──────────────────────────────────────────────
stop_services() {
    info "Stopping services..."
    for pidf in logs/backend.pid logs/frontend.pid; do
        if [ -f "$pidf" ]; then
            pid=$(cat "$pidf")
            kill "$pid" 2>/dev/null && success "Stopped PID $pid." || true
            rm -f "$pidf"
        fi
    done
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    pkill -f "gradio_app.py"        2>/dev/null || true
    success "All services stopped."
}

# ── Print access instructions ──────────────────────────────────
print_access_info() {
    HOSTNAME=$(hostname)
    echo ""
    echo "════════════════════════════════════════════════════════════"
    success "GAIC Detector is running!"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    echo "  Compute node : $HOSTNAME"
    echo "  Backend API  : http://localhost:8000  (docs: /docs)"
    echo "  Frontend UI  : Check logs for dynamic port (typically http://localhost:7860+)"
    echo ""
    echo "── Public Web Access ───────────────────────────────────────"
    echo ""
    echo "  A public Gradio link is being generated. Look for the "
    echo "  'Running on public URL' line in your logs."
    echo ""
    echo "  To see the generated URL, run:"
    echo "    cat logs/frontend.log | grep -i 'public URL'"
    echo ""
    echo "── Management ────────────────────────────────────────────"
    echo "  Logs        : tail -f logs/backend.log | tail -f logs/frontend.log"
    echo "  Stop        : ./start.sh stop"
    echo "════════════════════════════════════════════════════════════"
}

# ── Main ───────────────────────────────────────────────────────
main() {
    echo "════════════════════════════════════════════════════════════"
    echo "  GAIC Detector – Service Launcher"
    echo "════════════════════════════════════════════════════════════"
    echo ""

    MODE=${1:-all}

    case "$MODE" in
        backend)
            check_gpu && check_pytorch_cuda || true
            auto_cleanup
            start_backend
            ;;
        frontend)
            auto_cleanup
            start_frontend
            print_access_info
            ;;
        all)
            check_gpu && check_pytorch_cuda || true
            echo ""
            auto_cleanup
            start_backend
            start_frontend
            print_access_info
            ;;
        stop)
            stop_services
            ;;
        *)
            echo "Usage: $0 [backend|frontend|all|stop]"
            exit 1
            ;;
    esac
}

main "$@"
