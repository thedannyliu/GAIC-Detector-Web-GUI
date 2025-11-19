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

# 檢查是否在 login node
CURRENT_NODE=$(hostname)
if [[ $CURRENT_NODE == *"login"* ]]; then
    echo "❌ 錯誤: 不能在 login node 上運行此服務"
    echo ""
    echo "Login node 資源有限，無法運行深度學習模型。"
    echo ""
    echo "請使用以下方式獲取 compute node:"
    echo ""
    echo "方法 1: Interactive Job (推薦用於測試)"
    echo "  salloc --nodes=1 --ntasks-per-node=4 --mem=32GB --gres=gpu:1 --time=2:00:00"
    echo "  # 等待分配到節點後會自動 SSH 進去"
    echo ""
    echo "方法 2: PACE OnDemand - Interactive Apps"
    echo "  1. 前往 https://ondemand-phoenix.pace.gatech.edu"
    echo "  2. 選擇 'Interactive Apps' > 'Jupyter'"
    echo "  3. 設定資源 (GPU, Memory, Time)"
    echo "  4. 啟動後在 Jupyter Terminal 中執行此腳本"
    echo ""
    exit 1
fi

echo "✅ 在 compute node 上 ($CURRENT_NODE)"
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
echo "正在啟動 backend..."
echo "這可能需要 10-30 秒 (載入 AIDE 模型權重 3.35GB)"
echo ""

# 清空舊的 log
> backend.log

# 啟動 backend（背景運行）
conda run -n "$ENV_NAME" python -m app.main > backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > backend.pid
echo "Backend PID: $BACKEND_PID"
echo "Backend Log: backend.log"
echo ""

# 等待 backend 啟動（模型載入需要時間）
echo "等待 backend 啟動（載入模型中...）"
echo "這個過程需要時間，請耐心等待..."
echo ""

MAX_WAIT=45  # 最多等待 45 秒
WAITED=0

while [ $WAITED -lt $MAX_WAIT ]; do
    # 檢查進程是否還活著
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo ""
        echo "❌ Backend 進程已結束"
        echo ""
        echo "Backend log:"
        cat backend.log
        echo ""
        exit 1
    fi
    
    # 檢查是否有錯誤訊息
    if grep -qi "error.*failed\|traceback\|fatal" backend.log 2>/dev/null; then
        echo ""
        echo "❌ Backend 啟動時發現錯誤"
        echo ""
        echo "Backend log:"
        cat backend.log
        echo ""
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    
    # 檢查是否成功啟動
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        echo ""
        echo "✅ Backend 啟動成功 (http://localhost:8000)"
        echo ""
        break
    fi
    
    echo -n "."
    sleep 2
    WAITED=$((WAITED + 2))
done

# 最終檢查
if [ $WAITED -ge $MAX_WAIT ]; then
    echo ""
    echo "❌ Backend 啟動超時 (${MAX_WAIT}秒)"
    echo ""
    echo "Backend log (最後 50 行):"
    tail -50 backend.log
    echo ""
    echo "可能原因:"
    echo "  1. 模型權重載入需要更長時間（正常現象）"
    echo "  2. GPU/記憶體不足"
    echo "  3. 依賴套件缺失"
    echo ""
    echo "建議:"
    echo "  1. 手動啟動查看完整錯誤: conda activate gaic-detector && python -m app.main"
    echo "  2. 檢查是否有足夠的 GPU 記憶體"
    echo ""
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
