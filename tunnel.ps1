# SSH Tunnel Script for GAIC Detector on PACE Phoenix
# 用法: .\tunnel.ps1 [compute_node_hostname]
# 
# 範例: 
#   .\tunnel.ps1                                          # 使用預設節點
#   .\tunnel.ps1 atl1-1-03-004-29-0.pace.gatech.edu      # 指定節點

param(
    [string]$ComputeNode = "atl1-1-03-004-29-0.pace.gatech.edu"
)

# 設定變數
$REMOTE_USER = "eliu354"
$LOGIN_NODE = "login-phoenix.pace.gatech.edu"
$LOCAL_PORT_FRONTEND = 7860
$LOCAL_PORT_BACKEND = 8001  # 使用 8001 避免衝突
$REMOTE_PORT_FRONTEND = 7860
$REMOTE_PORT_BACKEND = 8000

# 顯示資訊
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GAIC Detector SSH Tunnel" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "連線資訊:" -ForegroundColor Yellow
Write-Host "  遠端使用者: $REMOTE_USER" -ForegroundColor White
Write-Host "  登入節點:   $LOGIN_NODE" -ForegroundColor White
Write-Host "  計算節點:   $ComputeNode" -ForegroundColor White
Write-Host ""
Write-Host "Port 轉發:" -ForegroundColor Yellow
Write-Host "  Frontend (Gradio):  http://localhost:$LOCAL_PORT_FRONTEND --> $ComputeNode`:$REMOTE_PORT_FRONTEND" -ForegroundColor Green
Write-Host "  Backend (API):      http://localhost:$LOCAL_PORT_BACKEND --> $ComputeNode`:$REMOTE_PORT_BACKEND" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 檢查本地 port 是否被佔用
$portInUse = $false

$frontendPort = Get-NetTCPConnection -LocalPort $LOCAL_PORT_FRONTEND -ErrorAction SilentlyContinue
if ($frontendPort) {
    Write-Host "⚠️  警告: 本地 port $LOCAL_PORT_FRONTEND 已被使用" -ForegroundColor Yellow
    $portInUse = $true
}

$backendPort = Get-NetTCPConnection -LocalPort $LOCAL_PORT_BACKEND -ErrorAction SilentlyContinue
if ($backendPort) {
    Write-Host "⚠️  警告: 本地 port $LOCAL_PORT_BACKEND 已被使用" -ForegroundColor Yellow
    $portInUse = $true
}

if ($portInUse) {
    Write-Host ""
    Write-Host "建議:" -ForegroundColor Yellow
    Write-Host "  1. 關閉佔用 port 的程式" -ForegroundColor White
    Write-Host "  2. 或使用不同的本地 port" -ForegroundColor White
    Write-Host ""
    $continue = Read-Host "是否繼續嘗試建立 tunnel? (y/N)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        Write-Host "已取消" -ForegroundColor Red
        exit 1
    }
}

Write-Host "正在建立 SSH Tunnel..." -ForegroundColor Green
Write-Host ""
Write-Host "提示:" -ForegroundColor Yellow
Write-Host "  - 保持此視窗開啟" -ForegroundColor White
Write-Host "  - 按 Ctrl+C 結束 tunnel" -ForegroundColor White
Write-Host "  - 在瀏覽器開啟: http://localhost:$LOCAL_PORT_FRONTEND" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 建立 SSH tunnel
try {
    ssh -N `
        -L ${LOCAL_PORT_FRONTEND}:${ComputeNode}:${REMOTE_PORT_FRONTEND} `
        -L ${LOCAL_PORT_BACKEND}:${ComputeNode}:${REMOTE_PORT_BACKEND} `
        ${REMOTE_USER}@${LOGIN_NODE}
}
catch {
    Write-Host ""
    Write-Host "❌ SSH Tunnel 建立失敗" -ForegroundColor Red
    Write-Host ""
    Write-Host "可能的原因:" -ForegroundColor Yellow
    Write-Host "  1. 計算節點名稱不正確" -ForegroundColor White
    Write-Host "  2. 本地 port 被佔用" -ForegroundColor White
    Write-Host "  3. SSH 連線問題" -ForegroundColor White
    Write-Host ""
    Write-Host "請檢查:" -ForegroundColor Yellow
    Write-Host "  1. 在遠端執行 'hostname' 確認節點名稱" -ForegroundColor White
    Write-Host "  2. 確認遠端服務正在運行 (port 7860, 8000)" -ForegroundColor White
    Write-Host "  3. 檢查 SSH 設定和網路連線" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "Tunnel 已關閉" -ForegroundColor Yellow
Write-Host ""
