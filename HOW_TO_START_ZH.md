# 🚀 啟動 GAIC Detector - 快速指南

## ✅ 問題已修復

已修復的問題：
- ✅ 修復了 `app/report.py` 中缺少的 `Tuple` 導入
- ✅ 創建了更可靠的 `start_simple.sh` 腳本

---

## 📋 正確啟動步驟

### 步驟 1: 確保環境已安裝

如果還沒有運行過安裝：

```bash
cd /storage/home/hcoda1/9/eliu354/r-agarg35-0/projects/GAIC-Detector-Web-GUI
./setup.sh
```

### 步驟 2: 確保模型已下載

如果還沒有下載模型：

```bash
./download_models.sh
```

### 步驟 3: **啟動環境（重要！）**

```bash
conda activate gaic-detector
```

**這一步很重要！** 必須先啟動環境。

### 步驟 4: 啟動服務

**方法 A - 使用簡化腳本（推薦）**:

```bash
./start_simple.sh
```

**方法 B - 手動啟動（用於除錯）**:

終端 1 - 後端：
```bash
conda activate gaic-detector
python -m app.main
```

終端 2 - 前端：
```bash
conda activate gaic-detector
python gradio_app.py
```

---

## 📊 預期輸出

### 成功啟動時應該看到：

```
🚀 Starting GAIC Detector Web GUI...

✅ Using conda environment: gaic-detector
✅ Python: /path/to/python
✅ Python version: Python 3.10.x

📡 Starting backend API on port 8000...
   Backend PID: 12345
⏳ Waiting for backend API to start...
✅ Backend API is ready!

🎨 Starting frontend UI on port 7860...
   Frontend PID: 12346
⏳ Waiting for frontend UI to start...
✅ Frontend UI is ready!

==========================================
✅ GAIC Detector is running!
==========================================

📍 Access points:
   🎨 Frontend UI:  http://localhost:7860
   📚 API Docs:     http://localhost:8000/docs
   ❤️  Health Check: http://localhost:8000/

📋 Logs:
   Backend:  tail -f /tmp/gaic_backend.log
   Frontend: tail -f /tmp/gaic_frontend.log

🛑 To stop:
   Press Ctrl+C in this terminal
   Or run: kill 12345 12346

==========================================

Monitoring services... (Press Ctrl+C to stop)
```

---

## 🔍 驗證服務運行

### 檢查後端 API

```bash
curl http://localhost:8000/
```

應該返回：
```json
{
  "status": "ok",
  "service": "GAIC Detector API",
  "version": "1.0.0",
  "available_models": ["SuSy", "FatFormer", "DistilDIRE"]
}
```

### 檢查前端 UI

在瀏覽器打開: http://localhost:7860

應該看到漂亮的 GAIC Detector 界面。

---

## 🐛 如果遇到問題

### 問題：conda activate 失敗

**錯誤訊息**: 
```
CommandNotFoundError: Your shell has not been properly configured
```

**解決**:
```bash
conda init bash
# 重新登入或執行
source ~/.bashrc
```

### 問題：Port 已被佔用

**錯誤訊息**:
```
⚠️  Port 8000 is already in use
```

**解決**:
```bash
# 找到並終止佔用 port 的進程
lsof -ti:8000 | xargs kill -9
lsof -ti:7860 | xargs kill -9

# 重新啟動
conda activate gaic-detector
./start_simple.sh
```

### 問題：模型載入失敗

**錯誤訊息**:
```
Warning: Model weights not found at models/weights/...
Using mock detector for ...
```

**解決**:
```bash
# 檢查模型檔案
ls -lh models/weights/

# 如果檔案缺失，重新下載
./download_models.sh
```

### 問題：後端 API 啟動失敗

**查看錯誤日誌**:
```bash
tail -50 /tmp/gaic_backend.log
```

**常見原因和解決方法**:

1. **導入錯誤** - 已修復（Tuple 導入）
2. **缺少依賴** - 運行 `pip install -r requirements.txt`
3. **Python 版本** - 確保使用 Python 3.10

### 問題：前端 UI 無法訪問

**查看錯誤日誌**:
```bash
tail -50 /tmp/gaic_frontend.log
```

**檢查**:
1. 後端 API 是否正在運行
2. Port 7860 是否被佔用
3. 防火牆設置

---

## 📝 完整啟動流程（複製貼上）

```bash
# 進入專案目錄
cd /storage/home/hcoda1/9/eliu354/r-agarg35-0/projects/GAIC-Detector-Web-GUI

# 啟動 conda 環境（重要！）
conda activate gaic-detector

# 啟動服務
./start_simple.sh
```

就這麼簡單！ 🎉

---

## 🎯 使用服務

### 訪問 Web UI

1. 打開瀏覽器
2. 訪問 http://localhost:7860
3. 上傳圖片
4. 選擇模型（SuSy、FatFormer 或 DistilDIRE）
5. 點擊 "Analyze Image"
6. 查看結果

### 使用 API

```bash
# 測試 API
python test_api.py

# 測試特定圖片
python test_api.py your_image.jpg
```

### 查看 API 文檔

在瀏覽器打開: http://localhost:8000/docs

可以看到完整的 API 文檔和測試界面。

---

## 🛑 停止服務

在運行 `start_simple.sh` 的終端按：

```
Ctrl + C
```

會自動清理並停止所有服務。

---

## 📚 更多資訊

- **詳細使用指南**: `docs/USER_GUIDE_ZH.md`
- **逐步教程**: `STEP_BY_STEP_ZH.md`
- **快速開始**: `QUICKSTART_ZH.md`
- **專案總結**: `docs/PROJECT_SUMMARY_ZH.md`

---

## 🆘 需要幫助？

### 運行系統驗證

```bash
./verify_system.sh
```

會檢查所有組件是否正確設置。

### 查看日誌

```bash
# 後端日誌
tail -f /tmp/gaic_backend.log

# 前端日誌
tail -f /tmp/gaic_frontend.log
```

### 測試 API

```bash
conda activate gaic-detector
python test_api.py
```

---

**現在可以開始使用了！** 🚀
