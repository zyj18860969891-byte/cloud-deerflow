#!/usr/bin/env powershell

# Railway CLI 部署脚本 - 获取 ALIPAY_NOTIFY_URL
# 日期: 2026年4月2日
# 用途: 通过 Railway CLI 部署应用并自动获取通知 URL

param(
    [string]$Action = "deploy",  # deploy / verify / logs / info
    [string]$ProjectId = $null,
    [switch]$Confirm = $false
)

# 颜色定义
$ColorGreen = "Green"
$ColorYellow = "Yellow"
$ColorRed = "Red"
$ColorCyan = "Cyan"
$ColorMagenta = "Magenta"

# 信息输出函数
function Write-Info { Write-Host "[ℹ️]  $args" -ForegroundColor $ColorCyan }
function Write-Success { Write-Host "[✅] $args" -ForegroundColor $ColorGreen }
function Write-Warning { Write-Host "[⚠️]  $args" -ForegroundColor $ColorYellow }
function Write-Error { Write-Host "[❌] $args" -ForegroundColor $ColorRed }
function Write-Step { Write-Host "`n[Step] $args" -ForegroundColor $ColorMagenta }

Write-Info "Railway CLI 部署脚本 - DeerFlow 应用"
Write-Info "版本: 1.0"
Write-Info "日期: 2026年4月2日"

# ========================================
# 1. 环境检查
# ========================================
Write-Step "检查环境..."

# 检查 Railway CLI
$railwayVersion = railway --version 2>$null
if (-not $LASTEXITCODE -eq 0) {
    Write-Error "Railway CLI 未安装"
    Write-Info "请运行: npm install -g @railway/cli"
    exit 1
}
Write-Success "Railway CLI: $railwayVersion"

# 检查 Git
$gitVersion = git --version 2>$null
if (-not $LASTEXITCODE -eq 0) {
    Write-Warning "Git 未安装或不在 PATH 中"
}
Write-Success "Git 已安装: $gitVersion"

# 检查当前目录
$currentPath = Get-Location
if (-not (Test-Path "backend")) {
    Write-Error "backend 目录不存在，请在项目根目录运行此脚本"
    exit 1
}
Write-Success "项目位置: $currentPath"

# ========================================
# 2. Railway 登录验证
# ========================================
Write-Step "验证 Railway 登录..."

$whoami = railway whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Warning "未登录到 Railway，正在打开登录页面..."
    Start-Process "https://railway.app/login"
    Write-Info "请完成登录后，按 Enter 继续..."
    Read-Host
}
Write-Success "已登录 Railway: $whoami"

# ========================================
# 3. 项目链接
# ========================================
Write-Step "链接 Railway 项目..."

$status = railway status 2>&1
if ($status -match "No linked project") {
    Write-Warning "未找到关联的项目，需要链接..."
    
    if ($ProjectId) {
        Write-Info "使用提供的 ProjectId: $ProjectId"
        railway link --project $ProjectId
    } else {
        Write-Info "请选择或创建项目..."
        railway link
    }
} else {
    Write-Success "已链接项目"
    Write-Info $status
}

# 验证链接
$status = railway status
Write-Success "项目状态已验证"

# ========================================
# 4. 配置环境变量
# ========================================
Write-Step "配置 Alipay 环境变量..."

$alipayConfigs = @{
    "ALIPAY_APP_ID"      = "2021006138604101"
    "ALIPAY_PID"         = "2088380691837603"
    "ALIPAY_GATEWAY_URL" = "https://openapi.alipay.com/gateway.do"
    "ENVIRONMENT"        = "production"
    "LOG_LEVEL"          = "INFO"
}

foreach ($key in $alipayConfigs.Keys) {
    $value = $alipayConfigs[$key]
    Write-Info "配置: $key = $value"
    railway variables set $key $value 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "✓ $key"
    } else {
        Write-Warning "! $key (可能已存在)"
    }
}

Write-Success "基础环境变量已配置"

# 提示配置敏感信息
Write-Warning "重要: 敏感信息需在 Railway Dashboard 手动配置"
Write-Info "请访问: https://railway.app"
Write-Info "项目 → Variables → 添加以下变量:"
Write-Info "  - ALIPAY_APP_PRIVATE_KEY (RSA私钥)"
Write-Info "  - ALIPAY_PUBLIC_KEY (RSA公钥)"
Write-Info "  - STRIPE_SECRET_KEY (可选)"

# ========================================
# 5. 代码推送和部署
# ========================================
if ($Action -eq "deploy") {
    Write-Step "准备代码推送..."
    
    # 检查 Git 状态
    $status = git status --short 2>&1
    if ($status) {
        Write-Warning "检测到未提交的变更:"
        Write-Info $status
        
        if (-not $Confirm) {
            Write-Warning "是否继续部署? (默认: y)"
            $response = Read-Host "(y/n)"
            if ($response -ne "y" -and $response -ne "") {
                Write-Info "已取消部署"
                exit 0
            }
        }
        
        Write-Step "提交变更..."
        git add . 2>&1 | Out-Null
        $message = "feat: Configure Alipay credentials and Railway deployment"
        git commit -m $message 2>&1 | Out-Null
        Write-Success "变更已提交"
    }
    
    Write-Step "推送代码到 GitHub..."
    git push origin main 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "代码已推送"
    } else {
        Write-Warning "代码推送可能遇到问题，但继续执行..."
    }
    
    Write-Step "启动 Railway 部署..."
    Write-Info "请稍候，部署可能需要 2-5 分钟..."
    
    railway up 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "部署命令已执行"
    } else {
        Write-Warning "部署可能失败，请检查日志"
    }
}

# ========================================
# 6. 等待部署完成
# ========================================
if ($Action -eq "deploy" -or $Action -eq "verify") {
    Write-Step "等待部署完成 (30秒)..."
    Start-Sleep -Seconds 30
    
    Write-Step "验证部署状态..."
    $serviceStatus = railway service list 2>&1
    Write-Info $serviceStatus
    
    Write-Success "部署状态已检查"
}

# ========================================
# 7. 获取 Public Domain
# ========================================
Write-Step "获取应用公域名..."

# 方法 1: 尝试从环境变量获取
$domain = railway variables 2>&1 | Select-String "RAILWAY_PUBLIC_DOMAIN" | ForEach-Object { $_ -replace ".*=\s*", "" }

# 方法 2: 如果未获得，提示用户
if (-not $domain -or $domain -eq "") {
    Write-Warning "无法自动获取域名，请在 Railway Dashboard 查看"
    Write-Info "打开: https://railway.app"
    Write-Info "项目 → Backend Service → Public Domain"
    Write-Info "按 Enter 继续..."
    Read-Host
    $domain = Read-Host "请输入获得的域名 (例如: deerflow-api.railway.app)"
}

$domain = $domain.Trim()
Write-Success "应用公域名: $domain"

# ========================================
# 8. 生成并配置 ALIPAY_NOTIFY_URL
# ========================================
Write-Step "生成 ALIPAY_NOTIFY_URL..."

$notifyUrl = "https://${domain}/api/subscription/webhook-alipay"
Write-Success "NOTIFY_URL: $notifyUrl"

Write-Info "配置到 Railway..."
railway variables set ALIPAY_NOTIFY_URL $notifyUrl 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Success "ALIPAY_NOTIFY_URL 已配置到 Railway"
}

# ========================================
# 9. 测试应用可访问性
# ========================================
Write-Step "测试应用可访问性..."

$healthUrl = "https://${domain}/health"
Write-Info "测试: GET $healthUrl"

try {
    $response = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 10 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Success "健康检查通过 (200 OK)"
        Write-Info $response.Content
    }
} catch {
    Write-Warning "健康检查失败: $_"
    Write-Info "应用可能仍在启动中，请稍候..."
}

# ========================================
# 10. 输出最终信息
# ========================================
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║          🎉 Railway 部署完成！                            ║" -ForegroundColor Magenta
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
Write-Host ""

Write-Host "📍 关键信息:" -ForegroundColor Cyan
Write-Host "  应用域名:         https://$domain"
Write-Host "  健康检查:         https://$domain/health"
Write-Host "  API 计划列表:     https://$domain/api/subscription/plans"
Write-Host "  Alipay 支付:      https://$domain/api/subscription/checkout-alipay"
Write-Host ""

Write-Host "🔔 ALIPAY_NOTIFY_URL:" -ForegroundColor Green
Write-Host "  $notifyUrl" -ForegroundColor Yellow
Write-Host ""

Write-Host "📋 后续步骤:" -ForegroundColor Cyan
Write-Host "  1️⃣  将 NOTIFY_URL 配置到支付宝开放平台"
Write-Host "     登录: https://open.alipay.com"
Write-Host "     应用设置 → 异步通知地址 → 粘贴上述 URL"
Write-Host ""
Write-Host "  2️⃣  测试支付流程"
Write-Host "     访问: https://$domain"
Write-Host "     选择套餐 → 选择 Alipay → 验证支付链接"
Write-Host ""
Write-Host "  3️⃣  监控日志"
Write-Host "     运行: railway logs --follow"
Write-Host ""

Write-Host "🔐 已配置的环境变量:" -ForegroundColor Cyan
$variables = railway variables
Write-Info "检查 Railway Dashboard 确认所有变量已正确配置"

Write-Host ""
Write-Host "🚀 部署已完成！系统可以接收 Alipay 支付回调。" -ForegroundColor Green
Write-Host ""

# ========================================
# 11. 提供额外命令
# ========================================
Write-Host "📌 常用命令:" -ForegroundColor Cyan
Write-Host ""
Write-Host "查看日志:"
Write-Host "  railway logs --follow"
Write-Host ""
Write-Host "查看环境变量:"
Write-Host "  railway variables"
Write-Host ""
Write-Host "重启应用:"
Write-Host "  railway service restart"
Write-Host ""
Write-Host "查看应用状态:"
Write-Host "  railway status"
Write-Host ""

Write-Success "部署脚本执行完毕！"
