# 🚀 PACE Phoenix 手動啟動指南

## ⚠️ 重要提醒

**不要在 login node 運行！**
Login node 資源有限，無法運行深度學習模型。

檢查你是否在 compute node：
```bash
hostname

# ✅ 正確 (compute node): atl1-1-01-010-31-0.pace.gatech.edu
# ❌ 錯誤 (login node):   login-phoenix.pace.gatech.edu
```

---

## 📋 取得 Compute Node

### 方法 1: Interactive Job (命令列)

```bash
# SSH 進入 PACE
ssh eliu354@login-phoenix.pace.gatech.edu

# 申請 interactive job (GPU node)
salloc --nodes=1 --ntasks-per-node=4 --mem=32GB --gres=gpu:1 --time=2:00:00

# 等待分配...分配後會自動進入 compute node
# 可以用 hostname 確認
```

### 方法 2: PACE OnDemand - Jupyter (推薦)

1. 前往 https://ondemand-phoenix.pace.gatech.edu
2. 點選 **Interactive Apps** → **Jupyter**
3. 設定資源：
   - **Number of hours**: 2
   - **Number of nodes**: 1
   - **CPU cores per node**: 4
   - **Memory per node (GB)**: 32
   - **GPU type**: Any
   - **Number of GPUs**: 1
4. 點選 **Launch**
5. 等待資源分配（可能需要幾分鐘）
6. 點選 **Connect to Jupyter**
7. 在 Jupyter 中開啟 **Terminal**

---

## 🔧 手動啟動服務

在 Jupyter Terminal 或 interactive job 中執行：

### Step 1: 進入專案目錄

```bash
cd ~/r-agarg35-0/projects/GAIC-Detector-Web-GUI
```

### Step 2: 啟動環境

```bash
conda activate gaic-detector
```

### Step 3: 啟動 Backend (終端機 1)

```bash
# 啟動 backend
python -m app.main

# 看到以下訊息表示成功:
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

**保持這個終端開啟！**

### Step 4: 啟動 Frontend (終端機 2)

在 Jupyter 開啟**另一個 Terminal**，或使用 `tmux`：

```bash
cd ~/r-agarg35-0/projects/GAIC-Detector-Web-GUI
conda activate gaic-detector

# 設定 backend URL
export GAIC_BACKEND_URL=http://localhost:8000

# 啟動 frontend
python gradio_app.py

# 看到以下訊息表示成功:
# Running on local URL:  http://0.0.0.0:7860
```

**保持這個終端也開啟！**

### Step 5: 記下節點名稱

```bash
hostname

# 範例輸出: atl1-1-01-010-31-0.pace.gatech.edu
```

**記下這個完整名稱！**後面建立 SSH tunnel 會用到。

---

## 🌐 建立 SSH Tunnel (在本地電腦)

### Windows PowerShell:

```powershell
# 替換成你的節點名稱
$NODE = "atl1-1-01-010-31-0.pace.gatech.edu"

ssh -N -L 7860:${NODE}:7860 -L 8001:${NODE}:8000 eliu354@login-phoenix.pace.gatech.edu
```

或使用腳本：
```powershell
.\tunnel.ps1 atl1-1-01-010-31-0.pace.gatech.edu
```

### Mac/Linux:

```bash
# 替換成你的節點名稱
NODE="atl1-1-01-010-31-0.pace.gatech.edu"

ssh -N -L 7860:${NODE}:7860 -L 8001:${NODE}:8000 eliu354@login-phoenix.pace.gatech.edu
```

**保持 SSH tunnel 視窗開啟！**

---

## 🎯 開啟瀏覽器

```
http://localhost:7860
```

測試 Grad-CAM:
1. 上傳圖片
2. 確認 "Include Grad-CAM Heatmap" 已勾選
3. 點擊 "Analyze Image"
4. 應該看到熱力圖！

---

## 🔍 故障排除

### ❌ Backend 啟動失敗

**檢查 1: 是否在 compute node？**
```bash
hostname
# 如果顯示 "login-phoenix" 就是在 login node (錯誤)
```

**檢查 2: 查看錯誤訊息**
```bash
# 前景運行看完整錯誤
conda activate gaic-detector
python -m app.main
```

常見錯誤：
- `No module named 'app'` → 確認在正確目錄
- `CUDA out of memory` → 需要申請更多記憶體或 GPU
- `Model file not found` → 檢查權重檔案是否存在

**檢查 3: 權重檔案**
```bash
ls -lh models/weights/GenImage_train.pth
# 應該顯示 ~3.35GB
```

### ❌ Frontend 連不到 Backend

**檢查 1: Backend 是否運行？**
```bash
curl http://localhost:8000/
# 應該返回: {"status":"ok",...}
```

**檢查 2: 環境變數**
```bash
echo $GAIC_BACKEND_URL
# 應該顯示: http://localhost:8000
```

**解法:**
```bash
export GAIC_BACKEND_URL=http://localhost:8000
python gradio_app.py
```

### ❌ 本地瀏覽器連不上

**檢查 1: SSH tunnel 是否正常？**
- 檢查 PowerShell/Terminal 是否有錯誤訊息
- 確認節點名稱正確

**檢查 2: 本地 port 是否被佔用？**
```powershell
# Windows
netstat -ano | findstr :7860
netstat -ano | findstr :8001

# Mac/Linux
lsof -i :7860
lsof -i :8001
```

**解法:** 關閉佔用的程式，或使用不同 port

---

## 📊 使用 tmux 管理多個終端

更方便的方式：在單一 SSH session 中管理多個程序

```bash
# 創建 tmux session
tmux new -s gaic

# 啟動 backend
cd ~/r-agarg35-0/projects/GAIC-Detector-Web-GUI
conda activate gaic-detector
python -m app.main

# 創建新窗格 (Ctrl+b 然後按 ")
# 在新窗格啟動 frontend
cd ~/r-agarg35-0/projects/GAIC-Detector-Web-GUI
conda activate gaic-detector
export GAIC_BACKEND_URL=http://localhost:8000
python gradio_app.py

# 切換窗格: Ctrl+b 然後方向鍵
# 離開 tmux (服務繼續運行): Ctrl+b 然後按 d
# 重新連接: tmux attach -s gaic
# 關閉整個 session: Ctrl+b 然後輸入 :kill-session
```

---

## ✅ 成功檢查清單

- [ ] 在 compute node 上 (用 `hostname` 確認)
- [ ] Backend 正在運行 (看到 "Uvicorn running on http://0.0.0.0:8000")
- [ ] Frontend 正在運行 (看到 "Running on local URL: http://0.0.0.0:7860")
- [ ] SSH tunnel 已建立 (本地 PowerShell 無錯誤)
- [ ] 瀏覽器可以開啟 http://localhost:7860
- [ ] 可以上傳圖片並看到結果
- [ ] 可以看到 Grad-CAM 熱力圖

---

## 🛑 關閉服務

1. **Frontend**: 在 frontend 終端按 `Ctrl+C`
2. **Backend**: 在 backend 終端按 `Ctrl+C`
3. **SSH Tunnel**: 在本地 PowerShell/Terminal 按 `Ctrl+C`
4. **如果用 tmux**: `tmux kill-session -t gaic`

---

## 📞 需要幫助？

- 查看完整文件: `SSH_TUNNEL_SETUP.md`
- 查看 Grad-CAM 說明: `GRADCAM_IMPLEMENTATION.md`
- 運行測試: `python test_gradcam_simple.py`
