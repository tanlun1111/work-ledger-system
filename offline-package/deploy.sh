# 警情案件工作台账登记系统 v1.0.3 离线部署脚本
#
# 用法:
#   1. 将 offline-package 文件夹拷贝到目标服务器
#   2. 在目标服务器上运行:
#      cd offline-package
#      docker build -t ledger-app:1.0.3 -f backend/Dockerfile .
#      docker-compose up -d
#
# 默认账号: admin / admin123
# 访问地址: http://localhost:5000

param(
    [string]$Password  = "ledger2026",
    [string]$SecretKey = "",
    [int]   $AppPort   = 5000,
    [int]   $DbPort    = 3307
)

$ErrorActionPreference = "Stop"
$ROOT        = $PSScriptRoot
$COMPOSE     = Join-Path $ROOT "docker-compose.yml"
$ENV_FILE    = Join-Path $ROOT ".env"
$DOCKERFILE  = Join-Path $ROOT "backend\Dockerfile"
$STARTED     = Get-Date

# ---- 工具函数 ----
function Write-Step($num, $total, $title) {
    Write-Host ""
    Write-Host ("-" * 56) -ForegroundColor DarkGray
    Write-Host "  [$num/$total]  $title" -ForegroundColor Yellow
    Write-Host ("-" * 56) -ForegroundColor DarkGray
}
function Write-OK($msg)  { Write-Host "    OK  $msg" -ForegroundColor Green }
function Write-ERR($msg) { Write-Host "    ERROR  $msg" -ForegroundColor Red; exit 1 }
function Write-INFO($msg) { Write-Host "    ..  $msg" -ForegroundColor Gray }

# ==============================================
Write-Host "" -ForegroundColor Cyan
Write-Host "  ==================================================" -ForegroundColor Cyan
Write-Host "  警情案件工作台账登记系统 - v1.0.3 离线部署" -ForegroundColor Cyan
Write-Host "  ==================================================" -ForegroundColor Cyan
Write-Host ""
Write-INFO "项目根目录:  $ROOT"
Write-INFO "应用端口:    $AppPort"
Write-INFO "MySQL 端口:  $DbPort"

# [1/5] 环境自检
Write-Step 1 5 "环境自检"

try {
    $dockerVer = docker version --format '{{.Server.Version}}' 2>&1
    Write-OK "Docker Engine v$dockerVer"
} catch {
    Write-ERR "Docker 未运行，请先安装并启动 Docker"
}

if (-not (Test-Path $COMPOSE)) { Write-ERR "找不到 docker-compose.yml" }
Write-OK "docker-compose.yml 存在"

if (-not (Test-Path $DOCKERFILE)) { Write-ERR "找不到 backend/Dockerfile" }
Write-OK "Dockerfile 存在"

$drive = (Get-Item $ROOT).PSDrive
$freeGB = $drive.Free / 1GB
if ($freeGB -lt 2) { Write-ERR "磁盘剩余空间不足 (${freeGB:N1} GB < 2 GB)" }
Write-OK "磁盘剩余: ${freeGB:N1} GB"

# [2/5] 构建镜像
Write-Step 2 5 "构建 Docker 镜像"

Write-INFO "docker build -t ledger-app:1.0.3 -f backend/Dockerfile ."
$sw = [Diagnostics.Stopwatch]::StartNew()
Push-Location $ROOT
try {
    docker build -t ledger-app:1.0.3 -f backend/Dockerfile .
    if ($LASTEXITCODE -ne 0) { Write-ERR "镜像构建失败" }
} finally { Pop-Location }
$sw.Stop()
Write-OK "镜像构建完成 (耗时 $($sw.Elapsed.TotalSeconds.ToString('0'))s)"

# [3/5] 生成 .env
Write-Step 3 5 "生成环境配置 .env"

if (-not $SecretKey) {
    $chars = (48..57) + (65..90) + (97..122)
    $SecretKey = -join ($chars | Get-Random -Count 32 | ForEach-Object { [char]$_ })
}

@"
# 台账系统 - 由 deploy.sh 自动生成 ($(Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
FLASK_ENV=production
MYSQL_HOST=db
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=$Password
MYSQL_DATABASE=work_ledger
SECRET_KEY=$SecretKey
"@ | Set-Content -Path $ENV_FILE -Encoding UTF8

Write-OK ".env 已生成"

# [4/5] 启动容器
Write-Step 4 5 "启动 Docker 容器"

Write-INFO "docker-compose up -d (首次启动约 30-60 秒)"
Push-Location $ROOT
try {
    docker-compose up -d 2>&1 | ForEach-Object {
        if ($_ -match "Creating|Starting|done|Running") { Write-INFO $_ }
    }
    if ($LASTEXITCODE -ne 0) { Write-ERR "容器启动失败" }
} finally { Pop-Location }

# [5/5] 等待服务就绪
Write-Step 5 5 "等待服务就绪"

Write-INFO "等待服务就绪..."
Start-Sleep -Seconds 10

try {
    $response = Invoke-WebRequest -Uri "http://localhost:$AppPort/login" -TimeoutSec 30 -UseBasicParsing
    Write-OK "应用响应 HTTP $($response.StatusCode)"
} catch {
    Write-INFO "应用尚未就绪，请稍后手动验证: http://localhost:$AppPort"
}

$ELAPSED = (Get-Date) - $STARTED

Write-Host ""
Write-Host "  ==================================================" -ForegroundColor Cyan
Write-Host "             部署成功！" -ForegroundColor Green
Write-Host "  --------------------------------------------------" -ForegroundColor Cyan
Write-Host "  应用:    http://localhost:$AppPort" -ForegroundColor White
Write-Host "  账号:    admin / admin123" -ForegroundColor White
Write-Host "  MySQL:   localhost:$DbPort" -ForegroundColor Gray
Write-Host "  耗时:    $($ELAPSED.TotalMinutes.ToString('0'))m$($ELAPSED.Seconds)s" -ForegroundColor Gray
Write-Host "  --------------------------------------------------" -ForegroundColor Cyan
Write-Host "  常用命令:" -ForegroundColor Cyan
Write-Host "    查看日志   docker-compose logs -f app" -ForegroundColor Gray
Write-Host "    停止服务   docker-compose down" -ForegroundColor Gray
Write-Host "    重启服务   docker-compose restart" -ForegroundColor Gray
Write-Host "  ==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  登录后请立即修改默认管理员密码！" -ForegroundColor DarkYellow
Write-Host ""
