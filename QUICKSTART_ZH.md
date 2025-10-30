# 🚀 GAIC Detector - 5分鐘快速開始

## 第一步：安裝環境（2分鐘）

```bash
cd /storage/home/hcoda1/9/eliu354/r-agarg35-0/projects/GAIC-Detector-Web-GUI

# 一鍵安裝
./setup.sh
```

**這會做什麼？**
- ✅ 創建 conda 環境 `gaic-detector`
- ✅ 安裝所有 Python 依賴
- ✅ 創建必要的目錄

---

## 第二步：下載模型（3-10分鐘）

```bash
# 自動下載所有三個模型
./download_models.sh
```

**下載內容：**
- 📦 SuSy.pt (~100MB)
- 📦 FatFormer (~200MB)  
- 📦 DistilDIRE (~150MB)

**總計：** ~450MB

---

## 第三步：啟動服務（30秒）

```bash
# 一鍵啟動
./start.sh
```

**服務狀態：**
- 🔧 後端 API: http://localhost:8000
- 🎨 前端 UI: http://localhost:7860

---

## 第四步：開始使用！

### 在瀏覽器中打開

```
http://localhost:7860
```

### 上傳圖片

1. 拖放圖片到上傳區域
2. 或點擊選擇檔案
3. 或貼上剪貼簿中的圖片

### 選擇模型

- **SuSy** - 平衡速度和準確度 ⭐推薦
- **FatFormer** - 較慢但可能更準確
- **DistilDIRE** - 最快

### 點擊分析

點擊 **🔍 Analyze Image** 按鈕

### 查看結果

- **分數** (0-100)
  - 0-30: 可能是真實圖片
  - 31-70: 不確定
  - 71-100: 可能是 AI 生成

- **熱圖疊加**（如果可用）
  - 顏色越深 = 越可能是 AI 生成

- **詳細說明**
  - 點擊展開查看完整分析

---

## 測試驗證

```bash
# 運行自動測試
conda activate gaic-detector
python test_api.py
```

**預期結果：** ✅ 3/3 tests passed

---

## 常見問題速查

### Port 被佔用？
```bash
lsof -ti:8000 | xargs kill -9
lsof -ti:7860 | xargs kill -9
./start.sh
```

### 模型沒下載完整？
```bash
# 重新下載
./download_models.sh
```

### 看到 "Using mock detector"？
- 表示模型檔案缺失
- 運行 `./download_models.sh` 下載模型

### 處理速度慢？
- ✅ 使用 DistilDIRE 模型（最快）
- ✅ 取消勾選 "Include Heatmap"
- ✅ 上傳前先壓縮圖片

---

## 完整文檔

- 📘 **完整使用指南**: `docs/USER_GUIDE_ZH.md`
- 📗 **專案總結**: `docs/PROJECT_SUMMARY_ZH.md`
- 📙 **模型資訊**: `docs/MODEL_SOURCES.md`
- 📕 **部署指南**: `docs/DEPLOYMENT.md`

---

## 需要幫助？

### 診斷問題
```bash
# 檢查環境
conda info

# 檢查模型檔案
ls -lh models/weights/

# 測試 API
python test_api.py
```

### 查看日誌
- 終端會顯示所有輸出
- 注意錯誤訊息

### 回報問題
在 GitHub 開 issue，附上：
- 錯誤訊息
- 執行步驟
- 環境資訊

---

## 快速命令參考

```bash
# 環境管理
conda activate gaic-detector    # 啟動環境
conda deactivate                # 退出環境

# 服務管理  
./start.sh                      # 啟動服務
Ctrl+C                          # 停止服務

# 測試
python test_api.py              # API 測試
python test_api.py image.jpg    # 測試特定圖片

# 模型管理
./download_models.sh            # 下載模型
ls -lh models/weights/          # 檢查模型
```

---

## 系統需求

- **記憶體**: 最少 8GB RAM
- **儲存**: 10GB 可用空間
- **網路**: 用於下載模型
- **GPU**: 可選（大幅提升速度）

---

**就這麼簡單！享受使用 GAIC Detector！** 🎉

有問題隨時查看 `docs/USER_GUIDE_ZH.md` 獲取詳細說明。
