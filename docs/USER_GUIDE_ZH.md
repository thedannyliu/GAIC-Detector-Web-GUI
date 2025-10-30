# GAIC Detector - 完整使用指南

## 📋 目錄

1. [系統需求](#系統需求)
2. [安裝步驟](#安裝步驟)
3. [模型下載](#模型下載)
4. [啟動服務](#啟動服務)
5. [使用介面](#使用介面)
6. [測試驗證](#測試驗證)
7. [常見問題](#常見問題)

---

## 系統需求

### 硬體需求
- **CPU**: 4 核心以上
- **記憶體**: 最少 8GB RAM（建議 16GB）
- **儲存空間**: 至少 10GB 可用空間
- **GPU** (可選): NVIDIA GPU with CUDA support（大幅提升速度）

### 軟體需求
- **作業系統**: Linux / macOS / Windows (with WSL2)
- **Conda**: Anaconda 或 Miniconda
- **網路**: 用於下載模型和依賴

---

## 安裝步驟

### 步驟 1: 確認 Conda 已安裝

```bash
conda --version
```

如果未安裝，請先安裝 [Miniconda](https://docs.conda.io/en/latest/miniconda.html)。

### 步驟 2: Clone 專案（如果還沒有）

```bash
cd /storage/home/hcoda1/9/eliu354/r-agarg35-0/projects
git clone <your-repo-url> GAIC-Detector-Web-GUI
cd GAIC-Detector-Web-GUI
```

### 步驟 3: 執行安裝腳本

```bash
./setup.sh
```

這個腳本會：
- ✅ 創建名為 `gaic-detector` 的 conda 環境（Python 3.10）
- ✅ 安裝所有必需的 Python 套件
- ✅ 創建必要的目錄結構
- ✅ 複製環境變數範例檔案

**預計時間**: 5-10 分鐘（取決於網路速度）

---

## 模型下載

### 方法 1: 使用自動下載腳本 ⭐ (推薦)

```bash
./download_models.sh
```

這個腳本會自動下載：
1. **SuSy** (TorchScript) - 從 Hugging Face
2. **FatFormer** (4-class) - 從 Google Drive
3. **DistilDIRE** (ImageNet-11e) - 從 Hugging Face

**下載大小**: 
- SuSy: ~100MB
- FatFormer: ~200MB
- DistilDIRE: ~150MB
- **總計**: ~450MB

**預計時間**: 5-15 分鐘（取決於網路速度）

### 方法 2: 手動下載

如果自動下載失敗，可以手動下載：

#### SuSy
```bash
wget -O models/weights/susy.pt \
  https://huggingface.co/HPAI-BSC/SuSy/resolve/main/SuSy.pt
```

#### FatFormer
1. 訪問 Google Drive: https://drive.google.com/file/d/1Q_Kgq4ygDf8XEHgAf-SgDN6Ru_IOTLkj
2. 下載檔案
3. 移動到 `models/weights/fatformer_4class_ckpt.pth`

或使用 `gdown`:
```bash
pip install gdown
gdown https://drive.google.com/uc?id=1Q_Kgq4ygDf8XEHgAf-SgDN6Ru_IOTLkj \
  -O models/weights/fatformer_4class_ckpt.pth
```

#### DistilDIRE
```bash
wget -O models/weights/distildire-imagenet-11e.pth \
  https://huggingface.co/yevvonlim/distildire/resolve/main/imagenet-distil-dire-11e.pth
```

### 驗證下載

```bash
ls -lh models/weights/
```

應該看到：
```
susy.pt                      (~100M)
fatformer_4class_ckpt.pth    (~200M)
distildire-imagenet-11e.pth  (~150M)
```

---

## 啟動服務

### 一鍵啟動（推薦）

```bash
./start.sh
```

這會同時啟動：
- 🔧 **後端 API** (FastAPI) - Port 8000
- 🎨 **前端 UI** (Gradio) - Port 7860

### 分別啟動（用於除錯）

**終端 1 - 啟動後端**:
```bash
conda activate gaic-detector
python -m app.main
```

**終端 2 - 啟動前端**:
```bash
conda activate gaic-detector
python gradio_app.py
```

### 檢查服務狀態

**檢查後端 API**:
```bash
curl http://localhost:8000/
```

應該返回:
```json
{
  "status": "ok",
  "service": "GAIC Detector API",
  "version": "1.0.0",
  "available_models": ["SuSy", "FatFormer", "DistilDIRE"]
}
```

**檢查前端 UI**:
在瀏覽器打開: http://localhost:7860

---

## 使用介面

### 1. 訪問 Web UI

打開瀏覽器，訪問: **http://localhost:7860**

### 2. 介面說明

```
┌─────────────────────────────────────────────────┐
│  🔍 GAIC Detector                               │
│  AI-Generated Image Detection                   │
├─────────────────────────────────────────────────┤
│  Model: [SuSy ▼]  ☑ Include Heatmap           │
├─────────────────────────────────────────────────┤
│  ┌───────────────┐  ┌───────────────┐          │
│  │  Upload Image │  │  Score: 78    │          │
│  │               │  │  █████████    │          │
│  │  [拖放圖片]   │  │  Medium       │          │
│  │               │  │               │          │
│  └───────────────┘  └───────────────┘          │
├─────────────────────────────────────────────────┤
│  Original Image      Heatmap Overlay            │
│  ┌──────────┐       ┌──────────┐               │
│  │          │       │  [熱圖]  │               │
│  └──────────┘       └──────────┘               │
├─────────────────────────────────────────────────┤
│  📝 Detailed Explanation [展開 ▼]              │
├─────────────────────────────────────────────────┤
│  History: [縮圖1] [縮圖2] [縮圖3] ...          │
└─────────────────────────────────────────────────┘
```

### 3. 上傳圖片的方式

**方式 A: 拖放上傳**
- 直接將圖片拖放到上傳區域

**方式 B: 點擊上傳**
- 點擊上傳區域
- 選擇圖片檔案

**方式 C: 剪貼簿貼上**
- 複製圖片（Ctrl+C / Cmd+C）
- 點擊上傳區域
- 貼上（Ctrl+V / Cmd+V）

**方式 D: 網路攝影機**
- 點擊 "Webcam" 標籤
- 拍照

### 4. 選擇模型

從下拉選單選擇：
- **SuSy** - TorchScript 模型，平衡速度和準確度
- **FatFormer** - Transformer 架構，較慢但可能更準確
- **DistilDIRE** - 輕量級模型，最快

### 5. 分析圖片

1. 上傳圖片
2. 選擇模型
3. 選擇是否包含熱圖
4. 點擊 **🔍 Analyze Image**
5. 等待結果（通常 1-5 秒）

### 6. 理解結果

**分數卡片**:
- **0-30**: Low - 可能是真實圖片
- **31-70**: Medium - 不確定，需要進一步檢查
- **71-100**: High - 可能是 AI 生成

**熱圖疊加**:
- 顏色較深的區域 = 更可能被 AI 生成
- 使用 Viridis 色圖（藍→綠→黃）

**詳細說明**:
- 點擊 "Show explanation" 查看詳細分析
- 包含檢測因素和建議

### 7. 查看歷史

- 最近 5 次分析會顯示在底部
- 點擊任何縮圖可以重新查看結果
- **不會重新計算**，直接載入快取

---

## 測試驗證

### 快速測試

```bash
# 確保服務正在運行
conda activate gaic-detector

# 運行 API 測試
python test_api.py
```

預期輸出:
```
🧪 GAIC Detector API Test Suite
==================================================
🔍 Testing health endpoint...
✅ Health check passed
   Response: {'status': 'ok', ...}

🔍 Testing models endpoint...
✅ Models endpoint passed
   Available models: ['SuSy', 'FatFormer', 'DistilDIRE']

🔍 Testing analyze endpoint...
   Creating test image...
✅ Analyze endpoint passed
   Score: 45/100
   Model: SuSy
   Inference time: 823ms
   Heatmap: ✓
   Errors: []

==================================================
📊 Test Summary:
==================================================
   Health Check         ✅ PASS
   Models List          ✅ PASS
   Image Analysis       ✅ PASS
==================================================
   Total: 3/3 tests passed

🎉 All tests passed!
```

### 用自己的圖片測試

```bash
python test_api.py path/to/your/image.jpg
```

### 性能基準測試

```bash
# 小圖片 (< 1MB)
time python test_api.py small_image.jpg

# 大圖片 (5-10 MB)
time python test_api.py large_image.jpg
```

預期處理時間:
- **小圖片** (< 1MB): 1-3 秒
- **中圖片** (1-5 MB): 3-8 秒
- **大圖片** (5-10 MB): 8-20 秒

---

## 常見問題

### Q1: 啟動時顯示 "Port already in use"

**解決方法**:
```bash
# 終止佔用 port 的進程
lsof -ti:8000 | xargs kill -9
lsof -ti:7860 | xargs kill -9

# 重新啟動
./start.sh
```

### Q2: 模型載入失敗

**症狀**: 看到 "Using mock detector" 訊息

**檢查**:
```bash
# 確認模型檔案存在
ls -lh models/weights/

# 應該看到三個 .pth/.pt 檔案
```

**解決方法**:
1. 重新下載模型: `./download_models.sh`
2. 檢查檔案權限: `chmod 644 models/weights/*`
3. 檢查檔案完整性

### Q3: CUDA 錯誤

**症狀**: "CUDA out of memory" 或類似錯誤

**解決方法**:
```bash
# 編輯 .env 檔案
echo "CUDA_VISIBLE_DEVICES=" >> .env

# 強制使用 CPU
# 重新啟動服務
```

### Q4: 處理速度很慢

**優化建議**:

1. **使用 GPU**（如果可用）:
   ```bash
   # 檢查 CUDA 是否可用
   python -c "import torch; print(torch.cuda.is_available())"
   ```

2. **減少圖片大小**:
   - 上傳前先壓縮圖片
   - 系統會自動縮放到 1536px

3. **選擇較快的模型**:
   - DistilDIRE 通常最快
   - SuSy 中等速度
   - FatFormer 較慢但可能更準確

4. **關閉熱圖生成**:
   - 取消勾選 "Include Heatmap"
   - 可節省 30-50% 處理時間

### Q5: LLM 報告生成失敗

**症狀**: 看到 "Explanation fallback in use" 通知

**原因**: 
- 未配置 OpenAI API Key
- API 配額用盡
- 網路問題

**解決方法**:
1. **使用模板報告**（預設）:
   - 系統會自動使用內建模板
   - 不需要任何配置

2. **啟用 LLM**（可選）:
   ```bash
   # 編輯 .env
   nano .env
   
   # 添加
   LLM_ENABLED=true
   OPENAI_API_KEY=your_api_key_here
   ```

### Q6: 無法訪問 Web UI

**檢查清單**:

1. **確認服務正在運行**:
   ```bash
   ps aux | grep python
   ```

2. **檢查 port**:
   ```bash
   netstat -tuln | grep 7860
   ```

3. **檢查防火牆**:
   ```bash
   # 允許 port 7860
   sudo ufw allow 7860
   ```

4. **使用正確的 URL**:
   - 本地: http://localhost:7860
   - 遠端: http://your-server-ip:7860

### Q7: 記憶體不足

**症狀**: "Out of memory" 錯誤

**解決方法**:

1. **降低最大圖片尺寸**:
   ```python
   # 編輯 app/config.py
   MAX_LONG_SIDE = 1024  # 從 1536 降到 1024
   ```

2. **一次只處理一張圖片**

3. **關閉其他應用程式**

4. **增加系統 swap 空間**

---

## 進階配置

### 環境變數設定

編輯 `.env` 檔案:

```bash
# API 設定
API_HOST=0.0.0.0
API_PORT=8000

# LLM 設定（可選）
LLM_ENABLED=false
OPENAI_API_KEY=
LLM_MODEL=gpt-3.5-turbo

# 處理設定
MAX_FILE_SIZE_MB=10
MAX_LONG_SIDE=1536
TIMEOUT_TOTAL=40

# 開發設定
DEBUG=false
LOG_LEVEL=INFO
```

### 自定義模型路徑

如果模型檔案在其他位置:

```python
# 編輯 app/config.py
MODELS_DIR = Path("/custom/path/to/models")
```

### 效能調優

```python
# app/config.py

# 更快但品質較低
DEFAULT_STRIDE = 224  # 從 112 改為 224

# 更短的超時時間
TIMEOUT_TOTAL = 30  # 從 40 改為 30
```

---

## 停止服務

### 方法 1: Ctrl+C

在終端按 `Ctrl+C` 停止服務

### 方法 2: 終止進程

```bash
# 找到進程
ps aux | grep "python.*app.main"
ps aux | grep "python.*gradio_app"

# 終止
kill <PID>

# 或強制終止
kill -9 <PID>
```

### 方法 3: 終止所有相關進程

```bash
pkill -f "python.*app.main"
pkill -f "python.*gradio_app"
```

---

## 生產部署

請參考 `docs/DEPLOYMENT.md` 了解:
- Nginx 反向代理設置
- Systemd 服務配置
- Docker 容器化
- SSL/HTTPS 配置
- 監控和日誌

---

## 獲取幫助

### 文檔資源
- **README.md** - 專案概覽
- **docs/PROJECT_SUMMARY_ZH.md** - 中文總結
- **docs/MODEL_SOURCES.md** - 模型資訊
- **docs/DEPLOYMENT.md** - 部署指南

### 診斷工具
```bash
# 檢查環境
conda info

# 檢查套件
conda list

# 查看日誌
tail -f /path/to/logs
```

### 回報問題
如果遇到問題:
1. 檢查本指南的「常見問題」章節
2. 運行 `python test_api.py` 診斷
3. 查看終端錯誤訊息
4. 在 GitHub 開 issue（附上錯誤訊息）

---

## 快速參考

### 常用命令

```bash
# 安裝
./setup.sh

# 下載模型
./download_models.sh

# 啟動服務
./start.sh

# 測試
python test_api.py

# 停止
Ctrl+C
```

### 檔案位置

```
配置: .env
模型: models/weights/
日誌: (終端輸出)
測試: test_api.py
```

### 重要 URL

- **前端**: http://localhost:7860
- **API 文檔**: http://localhost:8000/docs
- **健康檢查**: http://localhost:8000/

---

**祝您使用愉快！** 🎉
