# Phoenix GPU 一鍵啟動指南

## 🎯 完整流程（3 步驟）

### 1️⃣ 登入 Phoenix 並查找 GPU 節點
```bash
# 從本地電腦 SSH 到 Phoenix
ssh eliu354@login-phoenix.pace.gatech.edu

# 查看你的 GPU job
squeue -u $USER
```

輸出示例：
```
JOBID  PARTITION    NAME      USER   ST   TIME  NODES  NODELIST(REASON)
2280838 gpu-l40s  sys/dash  eliu354  R  3:00:00   1    atl1-1-03-004-29-0
                                                         ↑ 這是你的 GPU 節點
```

### 2️⃣ SSH 到 GPU 計算節點並啟動服務
```bash
# SSH 到你的 GPU 節點（用上面查到的節點名）
ssh atl1-1-03-004-29-0

# 進入專案目錄
cd /storage/home/hcoda1/9/eliu354/r-agarg35-0/projects/GAIC-Detector-Web-GUI

# 一鍵啟動！
./run_local.sh
```

### 3️⃣ 在本地電腦設置 SSH tunnel
啟動腳本會顯示一個命令，**複製它**並在**本地電腦**的新終端執行：

```bash
# 示例（根據你的節點名會不同）
ssh -N -L 7860:atl1-1-03-004-29-0:7860 -L 8000:atl1-1-03-004-29-0:8000 eliu354@login-phoenix.pace.gatech.edu
```

然後在瀏覽器打開：
- **前端界面**: http://localhost:7860
- **API 文檔**: http://localhost:8000/docs

## 🛑 停止服務
在 GPU 節點上執行：
```bash
cd /storage/home/hcoda1/9/eliu354/r-agarg35-0/projects/GAIC-Detector-Web-GUI
./stop.sh
```

## ❓ 常見問題

### Q: 為什麼不能在 login 節點運行？
A: Login 節點沒有 GPU，模型加載會失敗或被系統 kill。

### Q: 如何找到我的 GPU 節點？
A: 執行 `squeue -u $USER`，查看 `NODELIST` 列。

### Q: SSH tunnel 斷開怎麼辦？
A: 重新執行步驟 3 的 `ssh -N -L ...` 命令。

### Q: 如何確認服務正在運行？
A: 在 GPU 節點執行：
```bash
ps aux | grep -E "uvicorn|gradio" | grep -v grep
```

## 📁 文件說明
- `run_local.sh` - 一鍵啟動腳本（會自動檢查節點）
- `stop.sh` - 停止服務腳本
- `backend.log` - 後端日誌
- `frontend.log` - 前端日誌
