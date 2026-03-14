# SmartHire 虚拟环境停用脚本
# Version: 2.0.0
# Compliance: LAW-ENV-001 (无容器化), LAW-ENV-002 (无绝对路径)

<#
.SYNOPSIS
    停用 SmartHire Python 虚拟环境

.DESCRIPTION
    此脚本用于停用 SmartHire 项目的 Python 虚拟环境。
    停用后，Python 命令将恢复使用系统全局环境。

.USAGE
    deactivate

.EXAMPLE
    PS> deactivate
    命令提示符前的 (swanvenv) 标记将消失

.COMPLIANCE
    - LAW-ENV-001: 无容器化（使用 Python venv）
    - LAW-ENV-002: 无绝对路径硬编码

.NOTES
    此脚本需要在已激活的虚拟环境中运行。
    如果虚拟环境未激活，此命令将无效。
#>

# =============================================================================
# 辅助函数
# =============================================================================

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

# =============================================================================
# 主逻辑
# =============================================================================

function Deactivate-VirtualEnvironment {
    # 检查是否在虚拟环境中
    if (-not $env:VIRTUAL_ENV) {
        Write-Warning "虚拟环境未激活，无需停用"
        Write-Info "提示: 使用 .\activate.ps1 激活虚拟环境"
        return $false
    }

    # 停用虚拟环境
    try {
        deactivate
        Write-Success "SmartHire 虚拟环境已停用"
        Write-Info "现在 Python 命令将使用系统全局环境"
        return $true
    }
    catch {
        Write-Warning "停用虚拟环境时出错: $_"
        Write-Info "提示: 关闭当前终端窗口也可以退出虚拟环境"
        return $false
    }
}

# 执行停用
Deactivate-VirtualEnvironment
