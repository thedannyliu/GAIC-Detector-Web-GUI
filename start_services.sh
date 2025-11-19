#!/bin/bash
# start_services.sh - 在 PACE Phoenix 上啟動 GAIC Detector 服務
# 
# 用法: ./start_services.sh

set -e

WORK_DIR="/storage/home/hcoda1/9/eliu354/r-agarg35-0/projects/GAIC-Detector-Web-GUI"
ENV_NAME="gaic-detector"

cd "$WORK_DIR"

echo "=========================================="
echo "GAIC Detector - 服務啟動"
echo "=========================================="
echo ""
echo "工作目錄: $WORK_DIR"
echo "Conda 環境: $ENV_NAME"
echo "當前節點: $(hostname)"
echo ""

# 檢查 conda 環境
if ! conda info --envs | grep -q "$ENV_NAME"; then
    echo "❌ 錯誤: Conda 環境 '$ENV_NAME' 不存在"
    echo ""
    echo "請先創建環境:"
    echo "  conda create -n $ENV_NAME python=3.10"
    echo "  conda activate $ENV_NAME"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# 檢查模型權重
WEIGHT_FILE="$WORK_DIR/models/weights/GenImage_train.pth"
if [ ! -f "$WEIGHT_FILE" ]; then
    echo "❌ 錯誤: 模型權重檔案不存在: $WEIGHT_FILE"
    echo ""
    echo "請先下載模型權重"
    exit 1
fi

echo "✅ 環境檢查通過"
echo ""

# 清理舊的 PID 檔案
rm -f backend.pid frontend.pid

# 啟動 Backend
echo "=========================================="
echo "啟動 Backend (FastAPI)"
echo "=========================================="
echo ""

conda run -n "$ENV_NAME" python -m app.main > backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > backend.pid
echo "Backend PID: $BACKEND_PID"
echo "Backend Log: backend.log"

# 等待 backend 啟動
echo "等待 backend 啟動..."
sleep 8

# 檢查 backend 是否正常
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ Backend 啟動成功 (http://localhost:8000)"
else
    echo "❌ Backend 啟動失敗"
    echo ""
    echo "請檢查 backend.log:"
    tail -20 backend.log
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo ""

# 啟動 Frontend
echo "=========================================="
echo "啟動 Frontend (Gradio)"
echo "=========================================="
echo ""

export GAIC_BACKEND_URL=http://localhost:8000
echo "Backend URL: $GAIC_BACKEND_URL"
echo ""

# 設定 trap 以便 Ctrl+C 時清理
cleanup() {
    echo ""
    echo "=========================================="
    echo "正在關閉服務..."
    echo "=========================================="
    
    if [ -f backend.pid ]; then
        BACKEND_PID=$(cat backend.pid)
        echo "停止 Backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null || true
        rm -f backend.pid
    fi
    
    if [ -f frontend.pid ]; then
        FRONTEND_PID=$(cat frontend.pid)
        echo "停止 Frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null || true
        rm -f frontend.pid
    fi
    
    echo "✅ 所有服務已關閉"
    exit 0
}

trap cleanup SIGINT SIGTERM

# 啟動 frontend (前景執行)
echo "Frontend 啟動中..."
echo "使用 Ctrl+C 停止所有服務"
echo ""

conda run -n "$ENV_NAME" python gradio_app.py

# 如果 frontend 意外結束，清理 backend
cleanup
