# 🚀 PACE Phoenix 快速啟動指南

## 目標
從本地瀏覽器存取在 PACE Phoenix GPU cluster 上運行的 GAIC Detector（含 Grad-CAM 熱力圖）

---

## ⚡ 快速步驟

### 1️⃣ 在 PACE 上啟動服務

```bash
# 在 PACE Jupyter Terminal 中執行
cd /storage/home/hcoda1/9/eliu354/r-agarg35-0/projects/GAIC-Detector-Web-GUI
./start_services.sh
```

**預期輸出:**
```
✅ Backend 啟動成功 (http://localhost:8000)
✅ Frontend 啟動中... (http://0.0.0.0:7860)
```

保持這個終端開啟！

---

### 2️⃣ 取得計算節點名稱

```bash
# 在 PACE 上執行
hostname
```

**範例輸出:**
```
atl1-1-03-004-29-0.pace.gatech.edu
```

記下這個完整名稱！

---

### 3️⃣ 在本地建立 SSH Tunnel

**在本地 Windows PowerShell 中:**

```powershell
cd C:\path\to\GAIC-Detector-Web-GUI

# 方法 A: 使用腳本（推薦）
.\tunnel.ps1 atl1-1-03-004-29-0.pace.gatech.edu

# 方法 B: 手動建立
ssh -N -L 7860:atl1-1-03-004-29-0.pace.gatech.edu:7860 `
     -L 8001:atl1-1-03-004-29-0.pace.gatech.edu:8000 `
     eliu354@login-phoenix.pace.gatech.edu
```

⚠️ **注意**: 將 `atl1-1-03-004-29-0.pace.gatech.edu` 替換成你的節點名稱！

保持這個視窗開啟！

---

### 4️⃣ 開啟瀏覽器測試

```
http://localhost:7860
```

**測試 Grad-CAM:**
1. 進入 "📷 Image Analysis" 標籤
2. 確認 "Include Grad-CAM Heatmap" 已勾選 ✓
3. 上傳圖片
4. 點擊 "🔍 Analyze Image"
5. 查看熱力圖！

---

## 🛑 關閉服務

1. **在 PACE Terminal**: 按 `Ctrl+C`
2. **在本地 PowerShell**: 按 `Ctrl+C`

---

## 🔧 常見問題

### ❌ "Permission denied" on port 8000

**解法**: 使用 port 8001

```powershell
# 在腳本中已自動處理
# 手動時使用: -L 8001:...:8000
```

然後 Frontend 會自動連到 `http://localhost:8000`（遠端）

### ❌ "Connection refused"

**檢查:**
1. 遠端服務是否在運行？
   ```bash
   netstat -tuln | grep -E ':(7860|8000)'
   ```

2. hostname 正確嗎？
   ```bash
   hostname
   ```

### ❌ Frontend 連不到 Backend

**解法**: 確認環境變數

```bash
# 在啟動 frontend 前
export GAIC_BACKEND_URL=http://localhost:8000
```

### ❌ 熱力圖不顯示

**檢查:**
1. Backend log: `tail -f backend.log`
2. Browser console: F12
3. API response: 
   ```bash
   curl http://localhost:8001/analyze/image -F "file=@test.jpg" | jq '.heatmap_png_b64'
   ```

---

## 📁 相關檔案

| 檔案 | 說明 |
|------|------|
| `SSH_TUNNEL_SETUP.md` | 完整 SSH tunnel 設定指南 |
| `GRADCAM_IMPLEMENTATION.md` | Grad-CAM 實作說明 |
| `tunnel.ps1` | Windows PowerShell tunnel 腳本 |
| `start_services.sh` | PACE 服務啟動腳本 |
| `test_gradcam_simple.py` | 結構驗證測試 |

---

## 🎯 一行命令版

**在 PACE:**
```bash
cd ~/r-agarg35-0/projects/GAIC-Detector-Web-GUI && ./start_services.sh
```

**在本地 PowerShell:**
```powershell
.\tunnel.ps1 $(你的節點名稱)
```

**在瀏覽器:**
```
http://localhost:7860
```

---

## ✅ 成功標誌

- ✅ Backend log 顯示: `Uvicorn running on http://0.0.0.0:8000`
- ✅ Frontend 顯示: `Running on local URL: http://0.0.0.0:7860`
- ✅ SSH tunnel 沒有錯誤訊息
- ✅ 瀏覽器可以開啟 `http://localhost:7860`
- ✅ 上傳圖片後可以看到左右兩張圖（原圖 + 熱力圖）

---

## 📞 需要更多幫助？

查看詳細文件:
- `SSH_TUNNEL_SETUP.md` - SSH tunnel 詳細說明
- `GRADCAM_IMPLEMENTATION.md` - Grad-CAM 技術細節
- `docs/master_plan.md` - 完整專案文件

或執行測試:
```bash
python test_gradcam_simple.py  # 結構驗證
./test_gradcam_guide.sh        # 完整測試指南
```
