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

# ── Start backend ──────────────────────────────────────────────
start_backend() {
    info "Starting FastAPI backend (port 8000)..."
    export CUDA_VISIBLE_DEVICES=0

    nohup uvicorn app.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --timeout-keep-alive 120 \
        > backend.log 2>&1 &

    BACKEND_PID=$!
    echo "$BACKEND_PID" > backend.pid
    success "Backend started (PID $BACKEND_PID). Logs: backend.log"

    # Wait for backend to become ready (model loading takes time)
    info "Waiting for backend to become ready (model is ~3.6 GB, may take 30–60 s)..."
    for i in $(seq 1 60); do
        kill -0 "$BACKEND_PID" 2>/dev/null || { err "Backend process died. Check backend.log."; exit 1; }
        curl -sf --max-time 2 http://localhost:8000/ >/dev/null 2>&1 && { success "Backend ready (${i}s)."; break; }
        [ "$i" -eq 60 ] && { err "Backend did not start in 60 s. Check backend.log."; exit 1; }
        printf .
        sleep 1
    done
    echo ""
}

# ── Start frontend ─────────────────────────────────────────────
start_frontend() {
    info "Starting Gradio frontend (port 7860)..."

    # Detect cluster environment → enable Gradio public share link
    if [ -n "$SLURM_JOB_ID" ] || [ -n "$PBS_JOBID" ]; then
        info "Cluster environment detected – enabling Gradio share link."
        export GRADIO_SHARE=true
    else
        export GRADIO_SHARE=false
    fi

    export GRADIO_SERVER_PORT=7860
    nohup python gradio_app.py > frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "$FRONTEND_PID" > frontend.pid
    success "Frontend started (PID $FRONTEND_PID). Logs: frontend.log"

    # Wait for frontend
    for i in $(seq 1 30); do
        kill -0 "$FRONTEND_PID" 2>/dev/null || { err "Frontend process died. Check frontend.log."; exit 1; }
        curl -sf --max-time 2 http://localhost:7860/ >/dev/null 2>&1 && { success "Frontend ready (${i}s)."; break; }
        [ "$i" -eq 30 ] && { err "Frontend did not start in 30 s. Check frontend.log."; exit 1; }
        printf .
        sleep 1
    done
    echo ""
}

# ── Stop services ──────────────────────────────────────────────
stop_services() {
    info "Stopping services..."
    for pidf in backend.pid frontend.pid; do
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
    USERNAME=$(whoami)
    echo ""
    echo "════════════════════════════════════════════════════════════"
    success "GAIC Detector is running!"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    echo "  Compute node : $HOSTNAME"
    echo "  Backend API  : http://localhost:8000  (docs: /docs)"
    echo "  Frontend UI  : http://localhost:7860"
    echo ""
    echo "── SSH Tunnel (run this on your LOCAL machine) ─────────────"
    echo ""
    echo "  ssh -N \\"
    echo "    -L 7860:localhost:7860 \\"
    echo "    -L 8000:localhost:8000 \\"
    echo "    -J ${USERNAME}@login-phoenix.pace.gatech.edu \\"
    echo "    ${USERNAME}@${HOSTNAME}"
    echo ""
    echo "  Then open: http://localhost:7860"
    echo ""
    echo "── Management ────────────────────────────────────────────"
    echo "  Logs        : tail -f backend.log | tail -f frontend.log"
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
            start_backend
            ;;
        frontend)
            start_frontend
            print_access_info
            ;;
        all)
            check_gpu && check_pytorch_cuda || true
            echo ""
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
