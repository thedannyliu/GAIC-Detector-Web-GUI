# 🎯 GAIC Detector - 實際使用步驟指南

## 📌 當前狀態確認

您已經完成：
- ✅ 更新了 `setup.sh` 以使用 conda
- ✅ 更新了 `download_models.sh` 包含實際模型連結
- ✅ 系統已經整合了三個真實的 AI 偵測模型

---

## 🚀 第一部分：環境準備和模型下載

### 步驟 1: 進入專案目錄

```bash
cd /storage/home/hcoda1/9/eliu354/r-agarg35-0/projects/GAIC-Detector-Web-GUI
```

### 步驟 2: 執行環境設置

```bash
./setup.sh
```

**預期輸出：**
```
🔧 Setting up GAIC Detector Web GUI...
✅ Conda environment 'gaic-detector' already exists
✅ Python version: 3.10
⬆️  Upgrading pip...
📥 Installing dependencies...
📁 Creating directories...
✅ Setup complete!
```

**這需要：** 約 5-10 分鐘（第一次執行）

### 步驟 3: 下載模型權重

```bash
./download_models.sh
```

**會發生什麼：**
1. 從 Hugging Face 下載 SuSy (~100MB)
2. 從 Google Drive 下載 FatFormer (~200MB)
3. 從 Hugging Face 下載 DistilDIRE (~150MB)

**預期輸出：**
```
📦 GAIC Detector Model Download Script
========================================
📥 Downloading (HF): susy.pt
✅ Saved: models/weights/susy.pt (98M)
📥 Downloading (Google Drive): fatformer_4class_ckpt.pth
✅ Saved: models/weights/fatformer_4class_ckpt.pth (196M)
📥 Downloading (HF): distildire-imagenet-11e.pth
✅ Saved: models/weights/distildire-imagenet-11e.pth (142M)
========================================
📋 Model Download Summary
========================================
✅ susy.pt (98M)
✅ fatformer_4class_ckpt.pth (196M)
✅ distildire-imagenet-11e.pth (142M)
```

**這需要：** 約 5-15 分鐘（取決於網路速度）

### 步驟 4: 驗證安裝

```bash
./verify_system.sh
```

**預期輸出：**
```
🔍 GAIC Detector - 系統完整驗證
==================================

📋 檢查 1/7: Conda 環境
-------------------
✅ PASS: Conda 已安裝
✅ PASS: gaic-detector 環境已創建

📋 檢查 2/7: 專案結構
-------------------
✅ PASS: 目錄存在: app
✅ PASS: 目錄存在: models/weights
...

📋 檢查 3/7: 模型權重
-------------------
✅ PASS: 模型已下載: susy.pt (98M)
✅ PASS: 模型已下載: fatformer_4class_ckpt.pth (196M)
✅ PASS: 模型已下載: distildire-imagenet-11e.pth (142M)

...

==================================
📊 驗證摘要
==================================
通過: 20
警告: 2
失敗: 0

✅ 系統基本就緒，但有一些警告
```

---

## 🎮 第二部分：啟動和使用系統

### 步驟 5: 啟動服務

```bash
./start.sh
```

**預期輸出：**
```
🚀 Starting GAIC Detector Web GUI...
📡 Starting backend API on port 8000...
Using device: cuda  # 或 cpu
Loading SuSy from models/weights/susy.pt
Loading FatFormer from models/weights/fatformer_4class_ckpt.pth
Loading DistilDIRE from models/weights/distildire-imagenet-11e.pth
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
✅ Backend API is running (PID: 12345)

🎨 Starting frontend UI on port 7860...
Running on local URL:  http://127.0.0.1:7860

✅ GAIC Detector is running!

📍 Access the application at:
   Frontend UI:  http://localhost:7860
   API Docs:     http://localhost:8000/docs

Press Ctrl+C to stop both services...
```

**這需要：** 約 30 秒 - 1 分鐘（首次載入模型較慢）

### 步驟 6: 在瀏覽器中訪問

打開瀏覽器，訪問：

```
http://localhost:7860
```

**您應該看到：**
- 🎨 漂亮的紫色漸層標題 "GAIC Detector"
- 📤 圖片上傳區域
- 🔽 模型選擇下拉選單（SuSy, FatFormer, DistilDIRE）
- ☑️ "Include Heatmap" 複選框
- 🔍 大大的 "Analyze Image" 按鈕

---

## 🧪 第三部分：測試和驗證結果

### 測試 A: 命令列測試（確認 API 運作）

在**另一個終端**中：

```bash
cd /storage/home/hcoda1/9/eliu354/r-agarg35-0/projects/GAIC-Detector-Web-GUI
conda activate gaic-detector
python test_api.py
```

**預期輸出：**
```
🧪 GAIC Detector API Test Suite
==================================================
🔍 Testing health endpoint...
✅ Health check passed
   Response: {'status': 'ok', 'service': 'GAIC Detector API', ...}

🔍 Testing models endpoint...
✅ Models endpoint passed
   Available models: ['SuSy', 'FatFormer', 'DistilDIRE']
   Default model: SuSy

🔍 Testing analyze endpoint...
   Creating test image...
✅ Analyze endpoint passed
   Score: 67/100
   Model: SuSy
   Inference time: 1523ms
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

### 測試 B: UI 測試（實際使用體驗）

#### 準備測試圖片

找一張測試圖片（可以是任何 JPG/PNG/WEBP 圖片）

#### 在 UI 中測試

1. **上傳圖片**
   - 方法 1: 拖放圖片到上傳區域
   - 方法 2: 點擊上傳區域，選擇檔案
   - 方法 3: 複製圖片，點擊上傳區域，按 Ctrl+V

2. **選擇模型**
   - 選擇 "SuSy" (預設，推薦)
   - 確保 "Include Heatmap" 已勾選

3. **點擊分析**
   - 點擊 "🔍 Analyze Image" 按鈕
   - 等待 2-10 秒（取決於圖片大小）

4. **查看結果**

   **應該看到：**
   
   a) **分數卡片**（紫色漸層背景）
   ```
   ┌─────────────┐
   │     78      │  ← 大大的數字（0-100）
   │ Low·Medium·High│ ← 範圍標籤（對應的會加粗）
   │ Model: SuSy │
   │ Inference: 1523ms │
   └─────────────┘
   ```

   b) **並排圖片**
   - 左側：原始圖片
   - 右側：熱圖疊加（如果模型支援）
     - 藍色區域 = 可能是真實
     - 黃色/綠色區域 = 可能是 AI 生成

   c) **詳細說明**（摺疊）
   - 點擊 "📝 Detailed Explanation" 展開
   - 查看完整的分析報告

   d) **歷史記錄**
   - 底部顯示最近的 5 次分析
   - 點擊任何縮圖可以重新查看

### 測試 C: 不同模型比較

對同一張圖片測試三個模型：

1. **SuSy 模型**
   - 選擇 "SuSy"
   - 點擊分析
   - 記錄分數和處理時間

2. **FatFormer 模型**
   - 選擇 "FatFormer"
   - 點擊分析
   - 比較結果

3. **DistilDIRE 模型**
   - 選擇 "DistilDIRE"
   - 點擊分析
   - 注意這個通常最快

**觀察重點：**
- ✓ 不同模型可能給出不同分數
- ✓ DistilDIRE 通常最快
- ✓ FatFormer 可能最慢但更仔細
- ✓ SuSy 是平衡選擇

---

## 📊 第四部分：理解和解讀結果

### 分數解讀

| 分數範圍 | 標籤 | 含義 | 建議 |
|---------|------|------|------|
| 0-30 | Low | 很可能是真實圖片 | 可信度高 |
| 31-70 | Medium | 不確定，需進一步檢查 | 謹慎使用 |
| 71-100 | High | 很可能是 AI 生成 | 高度懷疑 |

### 影響分數的因素

1. **圖片來源**
   - 相機直接拍攝 → 通常低分
   - AI 生成器輸出 → 通常高分
   - 過度編輯的圖片 → 可能中等分數

2. **圖片品質**
   - 高解析度 → 更準確
   - 嚴重壓縮 → 可能誤判
   - 多次轉存 → 增加不確定性

3. **內容類型**
   - 人臉 → 通常檢測較準
   - 風景 → 較難判斷
   - 藝術作品 → 可能誤判

### 熱圖解讀

- **藍色區域**: 特徵像真實照片
- **綠色區域**: 有一些可疑特徵
- **黃色區域**: 強烈的 AI 生成特徵

---

## 🎯 第五部分：實際使用案例

### 案例 1: 檢測新聞圖片

```
1. 收到一張新聞圖片
2. 上傳到 GAIC Detector
3. 使用 SuSy 模型分析
4. 如果分數 > 70:
   - 進一步調查
   - 尋找原始來源
   - 諮詢專家
5. 如果分數 < 30:
   - 可能是真實照片
   - 仍需檢查其他證據
```

### 案例 2: 批次檢測

```bash
# 對資料夾中的所有圖片進行測試
for img in test_images/*.jpg; do
    echo "Testing: $img"
    python test_api.py "$img"
done
```

### 案例 3: 整合到工作流程

```python
import requests

def check_image_authenticity(image_path):
    with open(image_path, 'rb') as f:
        response = requests.post(
            'http://localhost:8000/analyze/image',
            files={'file': f},
            data={'model': 'SuSy', 'include_heatmap': 'true'}
        )
    
    result = response.json()
    score = result['score']
    
    if score > 70:
        return "SUSPICIOUS"
    elif score < 30:
        return "LIKELY_REAL"
    else:
        return "UNCERTAIN"
```

---

## 🔧 第六部分：效能優化建議

### 如果處理速度慢

1. **使用更快的模型**
   ```
   DistilDIRE > SuSy > FatFormer
   （速度從快到慢）
   ```

2. **關閉熱圖生成**
   - 取消勾選 "Include Heatmap"
   - 可節省 30-50% 時間

3. **預先縮小圖片**
   ```bash
   # 使用 ImageMagick 縮小
   convert large.jpg -resize 1536x1536\> smaller.jpg
   ```

4. **使用 GPU**
   ```bash
   # 檢查是否使用 GPU
   python -c "import torch; print(torch.cuda.is_available())"
   # 應該輸出 True
   ```

### 如果記憶體不足

1. **降低最大解析度**
   ```python
   # 編輯 app/config.py
   MAX_LONG_SIDE = 1024  # 從 1536 改為 1024
   ```

2. **一次只處理一張圖片**

3. **關閉其他程式**

---

## 🛑 第七部分：停止服務

### 正常停止

在運行 `./start.sh` 的終端按：
```
Ctrl + C
```

**應該看到：**
```
^C
🛑 Stopping services...
✅ Services stopped
```

### 強制停止

如果正常停止失敗：
```bash
# 終止所有相關進程
pkill -f "python.*app.main"
pkill -f "python.*gradio_app"

# 或者
lsof -ti:8000 | xargs kill -9
lsof -ti:7860 | xargs kill -9
```

---

## 📝 第八部分：記錄和檢視結果

### 查看終端日誌

服務運行時會在終端顯示：
- 請求記錄
- 模型載入訊息
- 錯誤警告

**重要日誌：**
```
Using device: cuda  ← GPU 或 CPU
Loading SuSy from ...  ← 模型載入
INFO: 127.0.0.1:xxxxx - "POST /analyze/image" 200  ← 請求成功
```

### 儲存結果

UI 自動保存最近 5 次結果在瀏覽器中

如果需要永久保存：
1. 截圖結果
2. 或使用 API 並保存 JSON 回應

---

## ❓ 第九部分：常見問題排查

### 問題 1: "Using mock detector" 訊息

**原因**: 模型檔案未找到

**解決**:
```bash
# 檢查模型檔案
ls -lh models/weights/

# 如果檔案缺失
./download_models.sh
```

### 問題 2: 分析很慢 (>30秒)

**檢查**:
```bash
# 是否使用 GPU?
python -c "import torch; print('GPU:', torch.cuda.is_available())"

# 圖片多大?
du -h your_image.jpg
```

**解決**:
- 選擇 DistilDIRE 模型
- 關閉熱圖
- 縮小圖片

### 問題 3: 分數總是相同

**可能原因**:
- 測試的圖片太相似
- 模型還在使用 Mock 模式

**檢查**: 確認模型已正確載入

### 問題 4: UI 無法訪問

**檢查**:
```bash
# Port 是否被佔用?
lsof -i:7860

# 服務是否運行?
ps aux | grep gradio
```

---

## 🎉 總結

您現在應該能夠：

✅ 完整安裝和配置系統
✅ 下載和驗證模型權重
✅ 啟動前後端服務
✅ 在 UI 中上傳和分析圖片
✅ 理解和解讀分析結果
✅ 使用三種不同的模型
✅ 進行效能優化
✅ 排查常見問題

---

## 📚 下一步

1. **深入學習**: 閱讀 `docs/USER_GUIDE_ZH.md`
2. **生產部署**: 參考 `docs/DEPLOYMENT.md`
3. **模型研究**: 查看 `docs/MODEL_SOURCES.md`
4. **自定義**: 根據需求調整配置

---

**享受使用 GAIC Detector！** 🚀

如有問題，隨時查看文檔或運行 `./verify_system.sh` 診斷。
