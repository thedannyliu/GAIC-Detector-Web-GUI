# SSH Tunnel Setup for PACE Phoenix GPU Cluster

## 問題說明

在 PACE Phoenix GPU cluster 上運行的服務（backend:8000, frontend:7860）無法直接從本地瀏覽器存取，需要透過 SSH tunnel 轉發。

## 解決方案

### Step 1: 確認遠端節點資訊

在 PACE 的 Jupyter 或終端機中執行：

```bash
# 查看當前節點名稱
hostname

# 範例輸出: atl1-1-03-004-29-0.pace.gatech.edu
```

記下這個完整的 hostname，後面會用到。

### Step 2: 在本地 Windows PowerShell 建立 SSH Tunnel

#### 選項 A: 使用不同的本地 Port（推薦）

如果本地的 8000 port 被佔用，改用其他 port：

```powershell
# 在本地 PowerShell 執行
# 將遠端 8000 → 本地 8001
# 將遠端 7860 → 本地 7860

ssh -N -L 7860:atl1-1-03-004-29-0.pace.gatech.edu:7860 `
     -L 8001:atl1-1-03-004-29-0.pace.gatech.edu:8000 `
     eliu354@login-phoenix.pace.gatech.edu
```

然後：
- Backend API: `http://localhost:8001`
- Frontend UI: `http://localhost:7860`

#### 選項 B: 釋放本地 8000 Port

如果你想用 8000，先找出佔用的程式：

```powershell
# 查看誰佔用了 8000 port
netstat -ano | findstr :8000

# 假設輸出: TCP  127.0.0.1:8000  0.0.0.0:0  LISTENING  12345
# 最後的數字 12345 是 PID

# 結束該程式（請確認是什麼程式再做！）
taskkill /PID 12345 /F
```

然後重試原本的命令：

```powershell
ssh -N -L 7860:atl1-1-03-004-29-0.pace.gatech.edu:7860 `
     -L 8000:atl1-1-03-004-29-0.pace.gatech.edu:8000 `
     eliu354@login-phoenix.pace.gatech.edu
```

### Step 3: 在遠端啟動服務

**終端機 1 - Backend:**
```bash
# SSH 進入 PACE
ssh eliu354@login-phoenix.pace.gatech.edu

# 進入 interactive node（如果還沒在 GPU node 上）
# （如果已經在 Jupyter 的 node 上就跳過這步）

# 啟動 backend
cd /storage/home/hcoda1/9/eliu354/r-agarg35-0/projects/GAIC-Detector-Web-GUI
conda activate gaic-detector
python -m app.main

# 應該會看到:
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

**終端機 2 - Frontend (在 Jupyter 的 Terminal 中):**
```bash
cd /storage/home/hcoda1/9/eliu354/r-agarg35-0/projects/GAIC-Detector-Web-GUI
conda activate gaic-detector

# 設定 backend URL（使用本地網路）
export GAIC_BACKEND_URL=http://localhost:8000

python gradio_app.py

# 應該會看到:
# Running on local URL:  http://0.0.0.0:7860
```

### Step 4: 從本地瀏覽器存取

**重要**: 確保 SSH tunnel 保持連線（不要關閉 PowerShell 視窗）

開啟瀏覽器：
- **Frontend**: http://localhost:7860
- **Backend API docs**: http://localhost:8000/docs (或 8001，看你用哪個)

### Step 5: 測試 Grad-CAM

1. 在瀏覽器開啟 http://localhost:7860
2. 進入 "📷 Image Analysis" 標籤
3. 確認 "Include Grad-CAM Heatmap" 已勾選 ✓
4. 上傳測試圖片
5. 點擊 "🔍 Analyze Image"
6. 應該會看到：
   - 左側：原始圖片
   - 右側：Grad-CAM 熱力圖 overlay

## 常見問題排解

### Q1: SSH tunnel 建立後立刻斷線

**原因**: 登入節點 (login-phoenix) 可能不允許直接 tunnel 到 compute node

**解法**: 使用 ProxyJump

```powershell
# 先 SSH 到 compute node，再建立 tunnel
ssh -N -L 7860:localhost:7860 `
     -L 8001:localhost:8000 `
     -J eliu354@login-phoenix.pace.gatech.edu `
     eliu354@atl1-1-03-004-29-0.pace.gatech.edu
```

### Q2: "Connection refused" 錯誤

**檢查項目**:
1. 遠端服務是否正在運行？
   ```bash
   # 在遠端檢查
   netstat -tuln | grep -E ':(7860|8000)'
   ```

2. hostname 是否正確？
   ```bash
   hostname  # 確認節點名稱
   ```

3. 防火牆設定（PACE 通常沒問題）

### Q3: Frontend 無法連到 Backend

**問題**: Frontend 顯示 "Connection Error" 或 "Backend unavailable"

**解法**: 確認 frontend 的 backend URL 設定

```bash
# 在啟動 gradio 之前設定
export GAIC_BACKEND_URL=http://localhost:8000

# 或在 gradio_app.py 的開頭加上
# API_URL = "http://localhost:8000"
```

### Q4: 熱力圖不顯示

**檢查步驟**:

1. Backend log 有無錯誤？
   ```
   ⚠️ Grad-CAM heatmap generation failed: ...
   ```

2. API response 的 `heatmap_png_b64` 是否為 null？
   ```bash
   # 測試 API
   curl -X POST http://localhost:8001/analyze/image \
     -F "file=@test.jpg" \
     -F "include_heatmap=true" \
     | jq '.heatmap_png_b64'
   ```

3. 瀏覽器 console 有無錯誤？ (F12 開發者工具)

## 自動化腳本

### 本地 PowerShell 腳本 (tunnel.ps1)

```powershell
# tunnel.ps1
# 用法: .\tunnel.ps1

# 設定變數
$REMOTE_USER = "eliu354"
$LOGIN_NODE = "login-phoenix.pace.gatech.edu"
$COMPUTE_NODE = "atl1-1-03-004-29-0.pace.gatech.edu"  # 改成你的節點

Write-Host "建立 SSH Tunnel..." -ForegroundColor Green
Write-Host "Frontend (Gradio): http://localhost:7860" -ForegroundColor Cyan
Write-Host "Backend (API):     http://localhost:8001" -ForegroundColor Cyan
Write-Host ""
Write-Host "按 Ctrl+C 結束 tunnel" -ForegroundColor Yellow
Write-Host ""

ssh -N `
    -L 7860:${COMPUTE_NODE}:7860 `
    -L 8001:${COMPUTE_NODE}:8000 `
    ${REMOTE_USER}@${LOGIN_NODE}
```

使用方式：
```powershell
# 給予執行權限（只需執行一次）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 執行
.\tunnel.ps1
```

### 遠端啟動腳本 (start_services.sh)

```bash
#!/bin/bash
# start_services.sh - 在 PACE 上啟動 backend 和 frontend

WORK_DIR="/storage/home/hcoda1/9/eliu354/r-agarg35-0/projects/GAIC-Detector-Web-GUI"
ENV_NAME="gaic-detector"

cd "$WORK_DIR"

echo "=========================================="
echo "啟動 GAIC Detector 服務"
echo "=========================================="

# 啟動 backend (背景執行)
echo "啟動 Backend (port 8000)..."
conda run -n "$ENV_NAME" python -m app.main > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# 等待 backend 啟動
sleep 5

# 檢查 backend 是否正常
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✅ Backend 啟動成功"
else
    echo "❌ Backend 啟動失敗，請檢查 backend.log"
    exit 1
fi

# 啟動 frontend (前景執行)
echo "啟動 Frontend (port 7860)..."
export GAIC_BACKEND_URL=http://localhost:8000
conda run -n "$ENV_NAME" python gradio_app.py

# 清理
echo "正在關閉服務..."
kill $BACKEND_PID
```

## 完整工作流程

### 一次性設定

1. **在本地創建 tunnel 腳本** (`tunnel.ps1`)
2. **在遠端創建啟動腳本** (`start_services.sh`)
   ```bash
   cd /storage/home/hcoda1/9/eliu354/r-agarg35-0/projects/GAIC-Detector-Web-GUI
   chmod +x start_services.sh
   ```

### 每次使用流程

1. **開啟 PACE Jupyter** (Interactive Apps)
   
2. **在 Jupyter Terminal 中啟動服務**:
   ```bash
   cd /storage/home/hcoda1/9/eliu354/r-agarg35-0/projects/GAIC-Detector-Web-GUI
   ./start_services.sh
   ```

3. **在本地 PowerShell 建立 tunnel**:
   ```powershell
   .\tunnel.ps1
   ```
   （保持這個視窗開啟）

4. **在本地瀏覽器開啟**:
   ```
   http://localhost:7860
   ```

5. **測試 Grad-CAM**:
   - 上傳圖片
   - 確認熱力圖顯示

6. **完成後關閉**:
   - Ctrl+C 停止遠端的 `start_services.sh`
   - Ctrl+C 停止本地的 tunnel

## 進階：使用 tmux 持續運行

如果想讓服務在背景持續運行（即使關閉 SSH）：

```bash
# 在遠端 PACE 上
tmux new -s gaic

# 在 tmux 中啟動服務
cd /storage/home/hcoda1/9/eliu354/r-agarg35-0/projects/GAIC-Detector-Web-GUI
conda activate gaic-detector

# 分割視窗
Ctrl+b "

# 上半部運行 backend
python -m app.main

# 切換到下半部
Ctrl+b ↓

# 下半部運行 frontend
export GAIC_BACKEND_URL=http://localhost:8000
python gradio_app.py

# 離開 tmux (服務繼續運行)
Ctrl+b d

# 重新連接
tmux attach -t gaic
```

## 參考資料

- [PACE Documentation](https://pace.gatech.edu/documentation)
- [SSH Tunneling Guide](https://www.ssh.com/academy/ssh/tunneling)
- [GAIC Detector README](../README.md)
- [Grad-CAM Implementation](../GRADCAM_IMPLEMENTATION.md)
