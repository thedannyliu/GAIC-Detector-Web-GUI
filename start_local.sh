#!/bin/bash
# GAIC Detector - 本地端訪問版本（Phoenix GPU 服務器）
# 使用 SSH 隧道在本地瀏覽器訪問

set -e

echo "🚀 GAIC Detector - 本地訪問版啟動"
echo ""

# 確認在正確的目錄
cd "$(dirname "$0")"

# 檢查 conda 環境
if [ "$CONDA_DEFAULT_ENV" != "gaic-detector" ]; then
    echo "❌ 錯誤: 請先執行 conda activate gaic-detector"
    exit 1
fi

echo "✅ Conda 環境: $CONDA_DEFAULT_ENV"
echo ""

# 檢查是否在 login 節點
HOSTNAME=$(hostname)
if [[ "$HOSTNAME" == *"login"* ]]; then
    echo "❌ 錯誤: 不能在 login 節點運行！"
    echo ""
    echo "請先申請計算節點："
    echo "  salloc --gres=gpu:1 --mem=32G -t 4:00:00 -N 1"
    echo ""
    echo "然後再運行此腳本。"
    exit 1
fi

echo "✅ 運行節點: $HOSTNAME"
echo ""

# 1. 清理舊進程
echo "🧹 清理舊進程..."
pkill -f "uvicorn app.main" 2>/dev/null || true
pkill -f "python gradio_app" 2>/dev/null || true
sleep 2

# 2. 清除 Python 快取
echo "🧹 清除 Python 快取..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# 3. 檢查端口
BACKEND_PORT=8000
FRONTEND_PORT=7860

if lsof -i:$BACKEND_PORT >/dev/null 2>&1; then
    echo "⚠️  端口 $BACKEND_PORT 被佔用，正在清理..."
    lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null || true
    sleep 2
fi

if lsof -i:$FRONTEND_PORT >/dev/null 2>&1; then
    echo "⚠️  端口 $FRONTEND_PORT 被佔用，正在清理..."
    lsof -ti:$FRONTEND_PORT | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# 4. 啟動後端
echo ""
echo "📡 啟動後端 API (port $BACKEND_PORT)..."
nohup uvicorn app.main:app \
    --host 0.0.0.0 \
    --port $BACKEND_PORT \
    --timeout-keep-alive 120 \
    > backend.log 2>&1 &

BACKEND_PID=$!
echo $BACKEND_PID > backend.pid
echo "   後端 PID: $BACKEND_PID"

# 5. 等待後端就緒（給大模型更多時間載入）
echo "⏳ 等待後端啟動（載入 3.35GB 模型需要時間）..."
MAX_WAIT=45
for i in $(seq 1 $MAX_WAIT); do
    # 檢查進程是否還活著
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "❌ 後端進程已停止！請查看 backend.log"
        echo ""
        echo "最後 30 行日誌："
        tail -30 backend.log
        exit 1
    fi
    
    # 檢查日誌中是否有致命錯誤
    if grep -qi "error.*failed\|traceback\|fatal" backend.log 2>/dev/null; then
        echo "⚠️  發現錯誤日誌，但繼續等待..."
    fi
    
    # 檢查後端是否就緒（但不在 login 節點執行 curl）
    if [ $i -gt 10 ]; then
        # 等待至少 10 秒後再開始測試連接
        if curl -s --max-time 2 http://localhost:$BACKEND_PORT/ >/dev/null 2>&1; then
            echo "✅ 後端就緒！（等待了 $i 秒）"
            break
        fi
    fi
    
    if [ $i -eq $MAX_WAIT ]; then
        echo "❌ 後端啟動超時！請查看 backend.log"
        echo ""
        echo "最後 30 行日誌："
        tail -30 backend.log
        echo ""
        echo "💡 提示: AIDE 模型需要載入 3.35GB 權重檔，可能需要更長時間"
        exit 1
    fi
    
    printf "."
    sleep 1
done
echo ""

# 6. 啟動前端（禁用 share）
echo ""
echo "🎨 啟動前端 (port $FRONTEND_PORT, Local Only)..."

# 禁用 GRADIO_SHARE
export GRADIO_SHARE=false

GRADIO_SERVER_PORT=$FRONTEND_PORT nohup python gradio_app.py > frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > frontend.pid
echo "   前端 PID: $FRONTEND_PID"

# 7. 等待前端啟動
echo "⏳ 等待前端啟動..."
MAX_WAIT_FRONTEND=30
for i in $(seq 1 $MAX_WAIT_FRONTEND); do
    # 檢查進程是否還活著
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "❌ 前端進程已停止！請查看 frontend.log"
        echo ""
        echo "前端日誌："
        cat frontend.log
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    
    # 等待至少 5 秒後再開始測試連接
    if [ $i -gt 5 ]; then
        if curl -s --max-time 2 http://localhost:$FRONTEND_PORT/ >/dev/null 2>&1; then
            echo "✅ 前端就緒！（等待了 $i 秒）"
            break
        fi
    fi
    
    if [ $i -eq $MAX_WAIT_FRONTEND ]; then
        echo "❌ 前端啟動超時！請查看 frontend.log"
        echo ""
        cat frontend.log
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    
    printf "."
    sleep 1
done
echo ""

# 8. 獲取當前服務器主機名
HOSTNAME=$(hostname)
USERNAME=$(whoami)

# 9. 顯示訪問指南
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ GAIC Detector 啟動成功！"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "🖥️  服務器信息:"
echo "   主機: $HOSTNAME"
echo "   用戶: $USERNAME"
echo "   後端 PID: $BACKEND_PID"
echo "   前端 PID: $FRONTEND_PID"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📱 如何在本地電腦訪問："
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "⚠️  重要: 需要通過 ProxyJump 方式連接到計算節點"
echo ""
echo "1️⃣  在你的【本地電腦】打開新的終端（PowerShell 或 CMD），執行："
echo ""
echo "   ssh -N -L 7860:localhost:7860 -L 8000:localhost:8000 -J ${USERNAME}@login-phoenix.pace.gatech.edu ${USERNAME}@${HOSTNAME}"
echo ""
echo "   說明: -J 參數會先跳轉到 login 節點，再連接到計算節點"
echo ""
echo "2️⃣  保持 SSH 隧道連接，然後在本地瀏覽器打開："
echo ""
echo "   🌐 http://localhost:7860"
echo ""
echo "3️⃣  使用完畢後，Ctrl+C 關閉 SSH 隧道"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "💡 快速複製（複製下面這行，在本地 PowerShell 執行）："
echo ""
echo "ssh -N -L 7860:localhost:7860 -L 8000:localhost:8000 -J ${USERNAME}@login-phoenix.pace.gatech.edu ${USERNAME}@${HOSTNAME}"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "🔧 如果上面的命令無法運行，可以用兩步法："
echo ""
echo "   步驟1: 先連到 login 節點並建立端口轉發"
echo "   ssh -L 7860:${HOSTNAME}:7860 -L 8000:${HOSTNAME}:8000 ${USERNAME}@login-phoenix.pace.gatech.edu"
echo ""
echo "   步驟2: 保持連接，然後在本地瀏覽器打開 http://localhost:7860"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📋 管理命令:"
echo ""
echo "   查看日誌:"
echo "     tail -f backend.log"
echo "     tail -f frontend.log"
echo ""
echo "   停止服務:"
echo "     pkill -f uvicorn && pkill -f gradio"
echo ""
echo "   重啟服務:"
echo "     ./start_local.sh"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✨ 服務已在背景運行，你可以關閉這個終端"
echo "════════════════════════════════════════════════════════════════"
echo ""
