# 🚀 Phoenix GPU Cluster 啟動指南

## 🎯 最簡單方式：一鍵啟動（強烈推薦）

```bash
cd ~/r-agarg35-0/projects/GAIC-Detector-Web-GUI
./start_all.sh
```

這會自動：
- ✅ 停止舊的進程
- ✅ 在背景啟動後端
- ✅ 等待後端就緒
- ✅ 啟動前端（Gradio Share 自動啟用）
- ✅ 按 Ctrl+C 時自動清理

**就這麼簡單！** 等待出現 Gradio URL 即可使用。

---

## 方法 1: 使用兩個 Jupyter Cells

### Cell 1 - 啟動後端
```bash
%%bash --bg --out backend_output
cd ~/r-agarg35-0/projects/GAIC-Detector-Web-GUI
source ~/miniconda3/etc/profile.d/conda.sh
conda activate gaic-detector
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

等待 10-15 秒讓模型載入...

### Cell 2 - 啟動前端
```bash
cd ~/r-agarg35-0/projects/GAIC-Detector-Web-GUI
source ~/miniconda3/etc/profile.d/conda.sh
conda activate gaic-detector
export GRADIO_SHARE=true
python gradio_app.py
```

等待出現公共 URL，例如：`https://xxxxx.gradio.live`

---

## 方法 2: 使用啟動腳本（兩個終端）

### 終端 1 - 後端
```bash
cd ~/r-agarg35-0/projects/GAIC-Detector-Web-GUI
./start_backend_simple.sh
```

保持這個終端運行！

### 終端 2 - 前端
```bash
cd ~/r-agarg35-0/projects/GAIC-Detector-Web-GUI
source ~/miniconda3/etc/profile.d/conda.sh
conda activate gaic-detector
export GRADIO_SHARE=true
python gradio_app.py
```

---

## 方法 3: 使用 start_gpu.sh（自動化）

⚠️ **注意**: 這會在背景啟動後端，前端在前台運行

```bash
cd ~/r-agarg35-0/projects/GAIC-Detector-Web-GUI
source ~/miniconda3/etc/profile.d/conda.sh
conda activate gaic-detector
./start_gpu.sh all
```

---

## ⏱️ 預期載入時間

- **後端啟動**: ~10-20 秒
  - 載入 AIDE 模型 (3.6GB)
  - 載入 ConvNeXt-XXL
  - 第一次會下載 ConvNeXt 權重 (~3GB)
  
- **前端啟動**: ~5-10 秒
  - 生成 Gradio Share URL
  - 建立公共連結

---

## ✅ 驗證後端是否啟動

### 在新的終端或 Cell 中：
```bash
curl http://localhost:8000/
```

應該回傳 JSON：
```json
{"message": "GAIC Detector API is running", ...}
```

---

## 🔍 查看日誌

### 後端日誌（如果使用背景啟動）:
```bash
tail -f ~/r-agarg35-0/projects/GAIC-Detector-Web-GUI/backend.log
```

---

## 🛑 停止服務

### 停止後端:
```bash
pkill -f "uvicorn app.main"
# 或
kill $(cat ~/r-agarg35-0/projects/GAIC-Detector-Web-GUI/backend.pid)
```

### 停止前端:
按 `Ctrl+C`

### 停止全部:
```bash
cd ~/r-agarg35-0/projects/GAIC-Detector-Web-GUI
pkill -f "uvicorn app.main"
pkill -f "gradio_app.py"
```

---

## 🐛 常見問題

### 1. `ModuleNotFoundError: No module named 'clip'`
```bash
conda activate gaic-detector
pip install openai-clip
```

### 2. `Cannot import name 'SUPPORTED_FORMATS'`
已修復！確保使用最新代碼：
```bash
git pull origin first-version
```

### 3. 後端連不上 (Connection refused)
後端還沒啟動完成，等待 10-20 秒後再試

### 4. GPU 記憶體不足
```bash
export CUDA_VISIBLE_DEVICES=""  # 強制使用 CPU
```

### 5. Gradio Share 沒有生成公共 URL
手動設定：
```bash
export GRADIO_SHARE=true
python gradio_app.py
```

---

## 📊 系統需求

- **GPU**: NVIDIA GPU with 6GB+ VRAM (推薦)
- **RAM**: 16GB+ (模型載入需要)
- **磁碟**: 10GB+ (模型權重)
- **網路**: 穩定連線（首次下載 ConvNeXt 權重）

---

## 💡 提示

1. **首次啟動會很慢**（下載 ConvNeXt 權重）
2. **使用 GPU** 快約 10 倍（0.3s vs 3s per image）
3. **Gradio Share URL** 在 Phoenix 上會自動啟用
4. **保持後端運行**在背景，前端可以重啟
5. **檢查日誌**如果遇到問題

---

## 🎯 快速檢查清單

- [ ] Conda 環境已激活 (`conda activate gaic-detector`)
- [ ] 在正確目錄 (`~/r-agarg35-0/projects/GAIC-Detector-Web-GUI`)
- [ ] AIDE 模型已下載 (`models/weights/GenImage_train.pth`)
- [ ] 所有依賴已安裝 (`pip install -r requirements.txt`)
- [ ] 後端啟動並運行 (`curl localhost:8000`)
- [ ] 前端顯示 Gradio Share URL

全部打勾就可以開始使用了！🎉
