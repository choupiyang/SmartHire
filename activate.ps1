# SmartHire 虚拟环境激活脚本
# Version: 2.0.0
# Compliance: LAW-ENV-001 (无容器化), LAW-ENV-002 (无绝对路径)

<#
.SYNOPSIS
    激活 SmartHire Python 虚拟环境

.DESCRIPTION
    此脚本用于激活 SmartHire 项目的 Python 虚拟环境 (swanvenv/)。
    激活后，所有 Python 命令将在虚拟环境中执行。

.USAGE
    .\activate.ps1

.EXAMPLE
    PS> .\activate.ps1
    激活虚拟环境后，命令提示符前会显示 (swanvenv) 标记

.COMPLIANCE
    - LAW-ENV-001: 无容器化（使用 Python venv）
    - LAW-ENV-002: 无绝对路径硬编码
#>

# =============================================================================
# 辅助函数
# =============================================================================

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "  $Title" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "  ✅ $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "  ℹ️  $Message" -ForegroundColor White
}

function Write-Warning {
    param([string]$Message)
    Write-Host "  ⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "  ❌ $Message" -ForegroundColor Red
}

# =============================================================================
# 主逻辑
# =============================================================================

function Activate-VirtualEnvironment {
    # 获取脚本根目录
    $ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
    $VenvPath = Join-Path $ScriptRoot "swanvenv"

    Write-Section "激活 SmartHire 虚拟环境"

    # 检查虚拟环境是否存在
    if (-not (Test-Path $VenvPath)) {
        Write-Error "虚拟环境不存在: $VenvPath"
        Write-Info "请先运行: python swan.py --init-venv"
        Write-Info "或者直接运行: python swan.py (会自动创建虚拟环境)"
        return $false
    }

    # 检查激活脚本
    $ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
    if (-not (Test-Path $ActivateScript)) {
        Write-Error "激活脚本不存在: $ActivateScript"
        Write-Warning "虚拟环境可能已损坏，请重新创建"
        return $false
    }

    # 激活虚拟环境
    try {
        & $ActivateScript
        Write-Success "SmartHire 虚拟环境已激活"
        Write-Info "虚拟环境路径: $VenvPath"
        Write-Info "Python 可执行文件: $(Join-Path $VenvPath 'Scripts\python.exe')"
        Write-Info ""
        Write-Info "现在可以运行 Python 命令，它们将在虚拟环境中执行"
        Write-Info "输入 'deactivate' 可以停用虚拟环境"
        return $true
    }
    catch {
        Write-Error "激活虚拟环境失败: $_"
        return $false
    }
}

# 执行激活
Activate-VirtualEnvironment
