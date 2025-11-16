#!/bin/bash
# GAIC Detector - GPU启动脚本
# Usage: ./start_gpu.sh [backend|frontend|all]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印信息函数
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 检查 GPU 可用性
check_gpu() {
    info "检查 GPU 可用性..."
    
    if command -v nvidia-smi &> /dev/null; then
        echo ""
        nvidia-smi --query-gpu=index,name,driver_version,memory.total,memory.free --format=csv,noheader
        echo ""
        success "GPU 检测成功！"
        return 0
    else
        warning "未检测到 nvidia-smi，将使用 CPU 模式"
        return 1
    fi
}

# 检查 PyTorch CUDA 支持
check_pytorch_cuda() {
    info "检查 PyTorch CUDA 支持..."
    
    python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda if torch.cuda.is_available() else \"N/A\"}'); print(f'GPU count: {torch.cuda.device_count()}'); [print(f'GPU {i}: {torch.cuda.get_device_name(i)}') for i in range(torch.cuda.device_count())]" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        success "PyTorch CUDA 检查完成"
    else
        error "PyTorch CUDA 检查失败，请确保安装了正确的 PyTorch 版本"
        echo ""
        echo "请访问 https://pytorch.org 安装支持 CUDA 的 PyTorch："
        echo "例如: pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu121"
        exit 1
    fi
}

# 启动后端
start_backend() {
    info "启动后端服务 (GPU 模式)..."
    
    # 设置环境变量强制使用 GPU
    export CUDA_VISIBLE_DEVICES=0  # 使用第一个 GPU，如果有多个可以改成 0,1
    export USE_GPU=1
    
    # 启动 FastAPI
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
}

# 启动前端
start_frontend() {
    info "启动前端服务..."
    
    # 检查是否在集群环境（启用 Gradio Share 获取公共 URL）
    if [ ! -z "$SLURM_JOB_ID" ] || [ ! -z "$PBS_JOBID" ]; then
        info "检测到集群环境，启用 Gradio Share（公共 URL）..."
        export GRADIO_SHARE=true
    fi
    
    # 前端不需要 GPU
    python gradio_app.py
}

# 启动全部（使用后台模式）
start_all() {
    info "启动全部服务 (后端 GPU 模式 + 前端)..."
    
    # 启动后端
    export CUDA_VISIBLE_DEVICES=0
    export USE_GPU=1
    
    info "启动后端（后台运行）..."
    nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > backend.pid
    success "后端已启动 (PID: $BACKEND_PID), 日志: backend.log"
    
    # 等待后端启动
    info "等待后端启动..."
    sleep 3
    
    # 检查后端是否运行
    if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
        warning "后端可能未正常启动，请检查 backend.log"
    fi
    
    # 检查是否在集群环境
    if [ ! -z "$SLURM_JOB_ID" ] || [ ! -z "$PBS_JOBID" ]; then
        info "检测到集群环境，启用 Gradio Share（公共 URL）..."
        export GRADIO_SHARE=true
    fi
    
    # 启动前端（前台运行）
    info "启动前端（前台运行）..."
    echo ""
    info "🌐 Gradio Share 已启用，将生成公共访问链接..."
    info "⏳ 请等待 10-20 秒生成链接..."
    echo ""
    python gradio_app.py
}

# 停止服务
stop_services() {
    info "停止服务..."
    
    if [ -f backend.pid ]; then
        BACKEND_PID=$(cat backend.pid)
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            kill $BACKEND_PID
            success "后端已停止 (PID: $BACKEND_PID)"
        fi
        rm backend.pid
    fi
    
    # 查找并停止可能的进程
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    pkill -f "gradio_app.py" 2>/dev/null || true
    
    success "所有服务已停止"
}

# 主函数
main() {
    echo "=================================="
    echo "  GAIC Detector - GPU 启动脚本"
    echo "=================================="
    echo ""
    
    # 检查 GPU
    GPU_AVAILABLE=false
    if check_gpu; then
        GPU_AVAILABLE=true
        echo ""
        check_pytorch_cuda
    fi
    
    echo ""
    echo "=================================="
    echo ""
    
    MODE=${1:-all}
    
    case $MODE in
        backend)
            if [ "$GPU_AVAILABLE" = true ]; then
                start_backend
            else
                error "GPU 不可用，请使用 ./start.sh backend 启动 CPU 模式"
                exit 1
            fi
            ;;
        frontend)
            start_frontend
            ;;
        all)
            if [ "$GPU_AVAILABLE" = true ]; then
                start_all
            else
                error "GPU 不可用，请使用 ./start.sh 启动 CPU 模式"
                exit 1
            fi
            ;;
        stop)
            stop_services
            ;;
        *)
            echo "Usage: $0 [backend|frontend|all|stop]"
            echo ""
            echo "  backend   - 启动后端 API 服务 (GPU 模式)"
            echo "  frontend  - 启动前端 Web UI"
            echo "  all       - 启动全部服务 (默认)"
            echo "  stop      - 停止所有服务"
            echo ""
            echo "Examples:"
            echo "  $0          # 启动全部服务"
            echo "  $0 backend  # 只启动后端"
            echo "  $0 stop     # 停止服务"
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
