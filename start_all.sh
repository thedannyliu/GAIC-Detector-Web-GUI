#!/bin/bash
# 🚀 一鍵啟動腳本 - Phoenix GPU Cluster
# 這個腳本會在背景啟動後端，前端在前台運行

set -e

PROJECT_DIR="/storage/home/hcoda1/9/eliu354/r-agarg35-0/projects/GAIC-Detector-Web-GUI"
cd "$PROJECT_DIR"

echo "=========================================="
echo "  🚀 GAIC Detector - 一鍵啟動"
echo "=========================================="
echo ""

# 激活環境
source ~/miniconda3/etc/profile.d/conda.sh
conda activate gaic-detector

echo "✅ Conda 環境已激活: gaic-detector"
echo ""

# 檢查模型是否存在
if [ ! -f "models/weights/GenImage_train.pth" ]; then
    echo "❌ AIDE 模型未找到！"
    echo "   請先執行: ./download_aide_weights.sh"
    exit 1
fi

echo "✅ AIDE 模型已存在"
echo ""

# 停止舊的進程
echo "🛑 停止舊的進程..."
pkill -f "uvicorn app.main" 2>/dev/null || true
pkill -f "gradio_app.py" 2>/dev/null || true
sleep 2

# 啟動後端
echo "📡 啟動後端 (背景運行)..."
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > backend.pid
echo "   後端 PID: $BACKEND_PID"
echo "   日誌: $PROJECT_DIR/backend.log"
echo ""

# 等待後端啟動
echo "⏳ 等待後端啟動 (需要 15-20 秒載入模型)..."
for i in {1..30}; do
    sleep 1
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        echo "   ✅ 後端已就緒！"
        break
    fi
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "   ❌ 後端啟動失敗！"
        echo ""
        echo "📋 錯誤日誌:"
        tail -30 backend.log
        exit 1
    fi
    if [ $((i % 5)) -eq 0 ]; then
        echo "   等待中... ($i/30 秒)"
    fi
done

if ! curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "   ⚠️  後端還在載入中，繼續等待..."
    echo "   💡 首次啟動需要下載 ConvNeXt 模型 (~3GB)"
    echo ""
fi

# 啟動前端
echo "🎨 啟動前端 (Gradio Share 已啟用)..."
echo "=========================================="
echo ""

export GRADIO_SHARE=true
python gradio_app.py

# 清理函數
cleanup() {
    echo ""
    echo "🛑 停止服務..."
    kill $BACKEND_PID 2>/dev/null || true
    pkill -f "uvicorn app.main" 2>/dev/null || true
    echo "✅ 已停止"
}

trap cleanup EXIT INT TERM
