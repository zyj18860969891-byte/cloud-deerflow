#!/usr/bin/env powershell
<#
.SYNOPSIS
DeerFlow 本地开发环境快速启动脚本

.DESCRIPTION
在三个独立的 PowerShell 窗口中启动 LangGraph、Gateway 和 Frontend 服务

.EXAMPLE
.\start-dev-services.ps1

.NOTES
确保在项目根目录运行此脚本
#>

param(
    [switch]$NoNewWindows = $false,
    [switch]$Sequential = $false,
    [switch]$Verbose = $false
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommandPath
$rootDir = if ($scriptDir) { $scriptDir } else { Get-Location }

Write-Host "================================" -ForegroundColor Cyan
Write-Host "DeerFlow 本地开发环境启动脚本" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 验证项目结构
$requiredDirs = @("backend", "frontend", "logs")
$missingDirs = @()
foreach ($dir in $requiredDirs) {
    if (-not (Test-Path "$rootDir\$dir")) {
        $missingDirs += $dir
    }
}

if ($missingDirs) {
    Write-Host "❌ 错误：缺少必要目录: $($missingDirs -join ', ')" -ForegroundColor Red
    Write-Host "请确保在项目根目录运行此脚本" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ 项目结构验证通过" -ForegroundColor Green
Write-Host ""

# 检查配置文件
if (-not (Test-Path "$rootDir\config.yaml")) {
    Write-Host "⚠️  config.yaml 不存在，正在从示例创建..." -ForegroundColor Yellow
    if (Test-Path "$rootDir\config.example.yaml") {
        Copy-Item "$rootDir\config.example.yaml" "$rootDir\config.yaml"
        Write-Host "✅ config.yaml 已创建" -ForegroundColor Green
    } else {
        Write-Host "❌ config.example.yaml 不存在" -ForegroundColor Red
        exit 1
    }
}

Write-Host "启动参数:" -ForegroundColor Cyan
Write-Host "  - NoNewWindows: $NoNewWindows"
Write-Host "  - Sequential: $Sequential"
Write-Host "  - Verbose: $Verbose"
Write-Host ""

if ($NoNewWindows) {
    # 在当前窗口中顺序启动（仅用于测试）
    Write-Host "⚠️  在当前窗口中启动服务（仅用于测试）" -ForegroundColor Yellow
    
    # LangGraph
    Write-Host ""
    Write-Host "========== 启动 LangGraph 服务 ==========" -ForegroundColor Cyan
    cd "$rootDir\backend"
    .\.venv\Scripts\python.exe -m langgraph dev
    
} else {
    # 在新窗口中启动
    Write-Host "在新窗口中启动三个服务..." -ForegroundColor Cyan
    Write-Host ""
    
    # LangGraph 服务
    Write-Host "🔸 启动 LangGraph (端口 2024)..." -ForegroundColor Yellow
    $langgraphCmd = {
        cd "$using:rootDir\backend"
        Write-Host "========== LangGraph 服务已启动 ==========" -ForegroundColor Green
        Write-Host "地址: http://localhost:2024" -ForegroundColor Cyan
        Write-Host "API 文档: http://localhost:2024/docs" -ForegroundColor Cyan
        Write-Host ""
        .\.venv\Scripts\python.exe -m langgraph dev --no-browser --allow-blocking --no-reload
    }
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $langgraphCmd -WindowStyle Normal
    Start-Sleep -Seconds 3
    
    # Gateway 服务
    Write-Host "🔸 启动 Gateway API (端口 8001)..." -ForegroundColor Yellow
    $gatewayCmd = {
        cd "$using:rootDir\backend"
        $env:OPENAI_API_KEY = "sk-test-temporary"
        Write-Host "========== Gateway API 已启动 ==========" -ForegroundColor Green
        Write-Host "地址: http://localhost:8001" -ForegroundColor Cyan
        Write-Host "健康检查: http://localhost:8001/health" -ForegroundColor Cyan
        Write-Host ""
        .\.venv\Scripts\python.exe -m uvicorn app.gateway.app:app --host 127.0.0.1 --port 8001
    }
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $gatewayCmd -WindowStyle Normal
    Start-Sleep -Seconds 3
    
    # Frontend 服务
    Write-Host "🔸 启动 Next.js 前端 (端口 3000)..." -ForegroundColor Yellow
    $frontendCmd = {
        cd "$using:rootDir\frontend"
        Write-Host "========== Next.js 前端已启动 ==========" -ForegroundColor Green
        Write-Host "地址: http://localhost:3000" -ForegroundColor Cyan
        Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Cyan
        Write-Host ""
        pnpm dev
    }
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd -WindowStyle Normal
    
    Write-Host ""
    Write-Host "================================" -ForegroundColor Green
    Write-Host "✅ 所有服务已启动！" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "访问应用:" -ForegroundColor Cyan
    Write-Host "  🌐 前端:          http://localhost:3000" -ForegroundColor White
    Write-Host "  🔧 Gateway API:   http://localhost:8001" -ForegroundColor White
    Write-Host "  🔗 LangGraph:     http://localhost:2024" -ForegroundColor White
    Write-Host "  📚 API 文档:      http://localhost:2024/docs" -ForegroundColor White
    Write-Host ""
    Write-Host "查看详细信息请参考: LOCAL_DEVELOPMENT.md" -ForegroundColor Yellow
    Write-Host ""
}
