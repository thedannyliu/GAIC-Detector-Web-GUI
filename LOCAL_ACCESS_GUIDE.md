# 🚀 本地訪問指南 - Phoenix GPU 服務器

## 快速開始（一鍵啟動）

### 在 Phoenix 服務器上執行：

```bash
cd /storage/home/hcoda1/9/eliu354/r-agarg35-0/projects/GAIC-Detector-Web-GUI
conda activate gaic-detector
./start_local.sh
```

### 在你的本地電腦上執行：

1. **打開本地電腦的終端**（Windows 用 PowerShell 或 Git Bash）

2. **執行 SSH 隧道命令**：
   ```bash
   ssh -N -L 7860:localhost:7860 -L 8000:localhost:8000 eliu354@login-phoenix-slurm.pace.gatech.edu
   ```

3. **打開本地瀏覽器**，訪問：
   ```
   http://localhost:7860
   ```

4. **完成！** 現在可以在本地瀏覽器使用 GAIC Detector

---

## 詳細說明

### SSH 隧道是什麼？

SSH 隧道讓你的本地電腦可以安全地訪問遠端服務器上的端口，就像服務運行在你本地一樣。

- `7860` - Gradio 前端界面
- `8000` - FastAPI 後端 API

### 如何停止服務？

**在 Phoenix 服務器上：**
```bash
pkill -f uvicorn && pkill -f gradio
```

**在本地電腦上：**
- 按 `Ctrl+C` 關閉 SSH 隧道即可

### 如何重啟服務？

```bash
cd /storage/home/hcoda1/9/eliu354/r-agarg35-0/projects/GAIC-Detector-Web-GUI
conda activate gaic-detector
./start_local.sh
```

### 查看日誌

```bash
# 查看後端日誌
tail -f backend.log

# 查看前端日誌
tail -f frontend.log
```

---

## 常見問題

### Q: SSH 隧道連接後沒反應？

**A:** 這是正常的！SSH 隧道會保持連接但不顯示任何輸出。只要終端沒有報錯，就是成功的。

### Q: 無法訪問 localhost:7860？

**A:** 
1. 確認 SSH 隧道還在運行（沒有按 Ctrl+C）
2. 確認 Phoenix 服務器上服務已啟動
3. 檢查瀏覽器是否輸入正確：`http://localhost:7860`

### Q: Connection refused 錯誤？

**A:** 
1. 確認服務器上服務正在運行：
   ```bash
   lsof -i:7860
   lsof -i:8000
   ```
2. 如果沒有輸出，重新執行 `./start_local.sh`

### Q: 服務啟動失敗？

**A:** 
1. 查看日誌：`cat backend.log` 或 `cat frontend.log`
2. 清理端口：`pkill -f uvicorn && pkill -f gradio`
3. 重新啟動：`./start_local.sh`

---

## 架構圖

```
┌─────────────────┐         SSH 隧道          ┌──────────────────┐
│  你的本地電腦    │ ←──────────────────────→ │  Phoenix 服務器   │
│                 │   7860:localhost:7860    │                  │
│  瀏覽器訪問:    │   8000:localhost:8000    │  Gradio: 7860    │
│  localhost:7860 │                          │  FastAPI: 8000   │
└─────────────────┘                          └──────────────────┘
```

---

## 優勢

✅ **穩定** - 不依賴 Gradio Share（常常超時）  
✅ **安全** - 所有流量通過加密的 SSH 連接  
✅ **快速** - 直連服務器，無需經過第三方  
✅ **可靠** - 不受防火牆或網絡限制影響  

---

## 提示

💡 **保持 SSH 隧道運行** - 使用期間不要關閉 SSH 隧道終端  
💡 **背景運行** - Phoenix 服務器上的服務會在背景運行，可以關閉那個終端  
💡 **多次使用** - SSH 隧道可以重複使用，不需要每次都重啟服務器上的服務  

---

**技術支援**: GitHub Issues  
**專案首頁**: https://github.com/thedannyliu/GAIC-Detector-Web-GUI
