#!/bin/bash

# GAIC Detector - Complete Verification Script
# 完整的系統驗證腳本

set -e

echo "🔍 GAIC Detector - 系統完整驗證"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
PASS=0
FAIL=0
WARN=0

# Helper functions
pass_test() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
    ((PASS++))
}

fail_test() {
    echo -e "${RED}❌ FAIL${NC}: $1"
    ((FAIL++))
}

warn_test() {
    echo -e "${YELLOW}⚠️  WARN${NC}: $1"
    ((WARN++))
}

echo "📋 檢查 1/7: Conda 環境"
echo "-------------------"
if command -v conda &> /dev/null; then
    pass_test "Conda 已安裝"
    
    if conda env list | grep -q "gaic-detector"; then
        pass_test "gaic-detector 環境已創建"
    else
        fail_test "gaic-detector 環境未找到（請運行 ./setup.sh）"
    fi
else
    fail_test "Conda 未安裝"
fi
echo ""

echo "📋 檢查 2/7: 專案結構"
echo "-------------------"
required_dirs=("app" "models/weights" "docs")
for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        pass_test "目錄存在: $dir"
    else
        fail_test "目錄缺失: $dir"
    fi
done

required_files=("app/main.py" "app/models.py" "gradio_app.py" "requirements.txt")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        pass_test "檔案存在: $file"
    else
        fail_test "檔案缺失: $file"
    fi
done
echo ""

echo "📋 檢查 3/7: 模型權重"
echo "-------------------"
model_files=("models/weights/susy.pt" "models/weights/fatformer_4class_ckpt.pth" "models/weights/distildire-imagenet-11e.pth")
model_found=0

for model in "${model_files[@]}"; do
    if [ -f "$model" ]; then
        size=$(du -h "$model" | cut -f1)
        pass_test "模型已下載: $(basename $model) ($size)"
        ((model_found++))
    else
        warn_test "模型未找到: $(basename $model)（系統將使用 Mock 模式）"
    fi
done

if [ $model_found -eq 0 ]; then
    echo ""
    echo "💡 提示: 運行 ./download_models.sh 下載所有模型"
fi
echo ""

echo "📋 檢查 4/7: Python 依賴"
echo "-------------------"
if conda env list | grep -q "gaic-detector"; then
    eval "$(conda shell.bash hook)"
    conda activate gaic-detector 2>/dev/null || true
    
    required_packages=("fastapi" "uvicorn" "gradio" "torch" "PIL" "numpy")
    for pkg in "${required_packages[@]}"; do
        if python -c "import $pkg" 2>/dev/null; then
            pass_test "套件已安裝: $pkg"
        else
            fail_test "套件缺失: $pkg"
        fi
    done
else
    warn_test "無法檢查 Python 套件（環境未啟動）"
fi
echo ""

echo "📋 檢查 5/7: 服務連接性"
echo "-------------------"

# Check if services are running
backend_running=false
frontend_running=false

if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    pass_test "後端 API 正在運行 (Port 8000)"
    backend_running=true
    
    # Test API endpoints
    if curl -s http://localhost:8000/models | grep -q "SuSy"; then
        pass_test "API /models 端點正常"
    else
        warn_test "API /models 端點響應異常"
    fi
else
    warn_test "後端 API 未運行（使用 ./start.sh 啟動）"
fi

if curl -s http://localhost:7860/ > /dev/null 2>&1; then
    pass_test "前端 UI 正在運行 (Port 7860)"
    frontend_running=true
else
    warn_test "前端 UI 未運行（使用 ./start.sh 啟動）"
fi
echo ""

echo "📋 檢查 6/7: 配置檔案"
echo "-------------------"
if [ -f ".env" ]; then
    pass_test ".env 檔案存在"
elif [ -f ".env.example" ]; then
    warn_test ".env 檔案不存在（使用 .env.example 中的預設值）"
else
    fail_test ".env 和 .env.example 都不存在"
fi
echo ""

echo "📋 檢查 7/7: 功能測試"
echo "-------------------"
if [ "$backend_running" = true ]; then
    echo "執行 API 測試..."
    if python test_api.py > /tmp/gaic_test.log 2>&1; then
        pass_test "API 功能測試通過"
        
        # Show summary from test output
        if grep -q "All tests passed" /tmp/gaic_test.log; then
            pass_test "所有 API 測試通過"
        fi
    else
        fail_test "API 功能測試失敗（查看 /tmp/gaic_test.log）"
    fi
else
    warn_test "跳過功能測試（服務未運行）"
fi
echo ""

echo "=================================="
echo "📊 驗證摘要"
echo "=================================="
echo -e "${GREEN}通過:${NC} $PASS"
echo -e "${YELLOW}警告:${NC} $WARN"
echo -e "${RED}失敗:${NC} $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
    if [ $WARN -eq 0 ]; then
        echo -e "${GREEN}🎉 完美！所有檢查都通過了！${NC}"
        echo ""
        echo "✨ 您的系統已完全就緒："
        if [ "$backend_running" = true ] && [ "$frontend_running" = true ]; then
            echo "   🌐 訪問 UI: http://localhost:7860"
            echo "   📚 API 文檔: http://localhost:8000/docs"
        else
            echo "   🚀 啟動服務: ./start.sh"
            echo "   🌐 然後訪問: http://localhost:7860"
        fi
    else
        echo -e "${YELLOW}✅ 系統基本就緒，但有一些警告${NC}"
        echo ""
        echo "💡 建議操作："
        
        if [ $model_found -eq 0 ]; then
            echo "   • 下載模型以獲得最佳體驗: ./download_models.sh"
        fi
        
        if [ "$backend_running" = false ] || [ "$frontend_running" = false ]; then
            echo "   • 啟動服務: ./start.sh"
        fi
    fi
else
    echo -e "${RED}⚠️  發現一些問題需要解決${NC}"
    echo ""
    echo "🔧 建議操作："
    echo "   1. 檢查上述失敗的項目"
    echo "   2. 運行 ./setup.sh 修復環境"
    echo "   3. 運行 ./download_models.sh 下載模型"
    echo "   4. 查看文檔: docs/USER_GUIDE_ZH.md"
    exit 1
fi

echo ""
echo "📚 更多資訊:"
echo "   • 快速開始: QUICKSTART_ZH.md"
echo "   • 使用指南: docs/USER_GUIDE_ZH.md"
echo "   • 專案總結: docs/PROJECT_SUMMARY_ZH.md"
echo ""
