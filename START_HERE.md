# 🚀 GAIC Detector - 一鍵啟動

## 快速開始（3 步驟）

### 1️⃣ Phoenix 服務器上執行：

```bash
cd /storage/home/hcoda1/9/eliu354/r-agarg35-0/projects/GAIC-Detector-Web-GUI
./run_local.sh
```

### 2️⃣ 本地電腦終端執行：

```bash
ssh -N -L 7860:localhost:7860 -L 8000:localhost:8000 eliu354@login-phoenix-slurm.pace.gatech.edu
```

### 3️⃣ 本地瀏覽器打開：

```
http://localhost:7860
```

## ✅ 完成！

---

## 📚 詳細文檔

- **[快速開始指南](QUICK_START.md)** - 完整使用說明（推薦閱讀）
- **[本地訪問指南](LOCAL_ACCESS_GUIDE.md)** - SSH 隧道詳細說明
- **[Phoenix 啟動指南](PHOENIX_START_GUIDE.md)** - Phoenix 專屬說明

---

## 🛠️ 管理命令

```bash
# 啟動服務
./run_local.sh

# 停止服務
./stop.sh

# 查看日誌
tail -f backend.log  # 後端
tail -f frontend.log # 前端
```

---

## 📖 詳細說明

請查看 [QUICK_START.md](QUICK_START.md) 獲取：
- 完整流程圖
- 常見問題解答
- 故障排除指南
- 技術細節說明

---

**項目**: GAIC Detector Web GUI  
**版本**: 2.0 - Local Access Edition  
**環境**: Georgia Tech PACE Phoenix GPU
