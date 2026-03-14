# SmartHire Windows Environment Setup Script
# Version: 1.0.0
# Compliance: LAW-ENV-002 (无绝对路径硬编码), LAW-ENV-001 (Windows Native)

# =============================================================================
# 文档说明
# =============================================================================

<#
.DESCRIPTION
    SmartHire Windows 环境变量注入脚本
    
    本脚本用于设置 SmartHire 系统运行所需的 Windows 环境变量。
    严格遵循相对路径原则，不使用绝对路径硬编码。

.USAGE
    .\start.ps1              # 设置环境变量并显示状态
    .\start.ps1 -Reset      # 重置环境变量
    .\start.ps1 -Test       # 测试环境变量有效性
    .\start.ps1 -Help       # 显示帮助信息

.REQUIREMENTS
    - Windows 11 Native
    - PowerShell 5.1+
    - Python 3.10+
    - Redis Server (可选)

.COMPLIANCE
    - LAW-ENV-002: 无绝对路径硬编码
    - LAW-ENV-001: Windows 原生运行（无容器化）
    - COMPOUND.md ENV-01: 根路径锚定
#>

# =============================================================================
# 参数定义
# =============================================================================

param(
    [switch]$Reset,
    [switch]$Test,
    [switch]$Help
)

# =============================================================================
# 全局常量
# =============================================================================

$SMARTHIRE_VERSION = "1.0.0"
$SMARTHIRE_NAME = "SmartHire"
$ENV_PREFIX = "SMARTHIRE_"

# =============================================================================
# 辅助函数
# =============================================================================

function Write-Banner {
    <#
    .SYNOPSIS
        打印启动横幅
    #>
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                                                            ║" -ForegroundColor Cyan
    Write-Host "║  ████████ ███████ ██   ██ ████████ ██ ██████  ████████     ║" -ForegroundColor Cyan
    Write-Host "║  ██       ██       ██  ██     ██     ██ ██   ██ ██          ║" -ForegroundColor Cyan
    Write-Host "║  █████    █████     ████      ██     ██ ██████  █████       ║" -ForegroundColor Cyan
    Write-Host "║  ██       ██        ██ ██     ██     ██ ██   ██ ██          ║" -ForegroundColor Cyan
    Write-Host "║  ██       ███████   ██  ██    ██     ██ ██   ██ ██          ║" -ForegroundColor Cyan
    Write-Host "║                                                            ║" -ForegroundColor Cyan
    Write-Host "║                Windows Environment Setup                   ║" -ForegroundColor Yellow
    Write-Host "║                   环境变量注入脚本                            ║" -ForegroundColor Yellow
    Write-Host "║                                                            ║" -ForegroundColor Cyan
    Write-Host "║  Version: $SMARTHIRE_VERSION | PowerShell 5.1+              ║" -ForegroundColor Cyan
    Write-Host "║  Compliance: LAW-ENV-002 | LAW-ENV-001                     ║" -ForegroundColor Cyan
    Write-Host "║                                                            ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Section {
    <#
    .SYNOPSIS
        打印章节标题
    
    .PARAMETER Title
        章节标题
    #>
    param([string]$Title)
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
    Write-Host "  $Title" -ForegroundColor Green
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
}

function Write-Info {
    <#
    .SYNOPSIS
        打印信息消息
    
    .PARAMETER Message
        消息内容
    #>
    param([string]$Message)
    Write-Host "  ℹ️  $Message" -ForegroundColor White
}

function Write-Success {
    <#
    .SYNOPSIS
        打印成功消息
    
    .PARAMETER Message
        消息内容
    #>
    param([string]$Message)
    Write-Host "  ✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    <#
    .SYNOPSIS
        打印警告消息
    
    .PARAMETER Message
        消息内容
    #>
    param([string]$Message)
    Write-Host "  ⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error {
    <#
    .SYNOPSIS
        打印错误消息
    
    .PARAMETER Message
        消息内容
    #>
    param([string]$Message)
    Write-Host "  ❌ $Message" -ForegroundColor Red
}

function Get-ScriptRoot {
    <#
    .SYNOPSIS
        获取脚本根目录（相对路径）
    
    .OUTPUTS
        System.IO.DirectoryInfo: 脚本根目录
    #>
    $scriptPath = $MyInvocation.MyCommand.Path
    $scriptRoot = Split-Path -Parent $scriptPath
    
    # 验证路径深度（COMPOUND.md ENV-01: 目录嵌套 ≤ 5 层）
    $depth = ($scriptRoot -split '\\|/').Count
    if ($depth -gt 5) {
        Write-Error "路径深度违规: $depth > 5 层"
        Write-Info "当前路径: $scriptRoot"
        exit 1
    }
    
    # 验证路径长度（Windows MAX_PATH = 260 字符）
    if ($scriptRoot.Length -gt 260) {
        Write-Error "路径长度违规: $($scriptRoot.Length) > 260 字符"
        Write-Info "当前路径: $scriptRoot"
        exit 1
    }
    
    return $scriptRoot
}

function Test-PathCompliance {
    <#
    .SYNOPSIS
        测试路径合规性（LAW-ENV-002: 无绝对路径硬编码）
    
    .PARAMETER Path
        待测试的路径
    
    .OUTPUTS
        bool: 是否合规
    #>
    param([string]$Path)
    
    # 检查是否为绝对路径
    if ([System.IO.Path]::IsPathRooted($Path)) {
        # 允许的绝对路径前缀
        $allowedPrefixes = @(
            "env:",
            "variable:",
            "$env:",
            "$SMARTHIRE_ROOT"
        )
        
        $isAllowed = $false
        foreach ($prefix in $allowedPrefixes) {
            if ($Path.StartsWith($prefix)) {
                $isAllowed = $true
                break
            }
        }
        
        if (-not $isAllowed) {
            return $false
        }
    }
    
    return $true
}

# =============================================================================
# 环境变量管理
# =============================================================================

function Set-SmartHireEnvironment {
    <#
    .SYNOPSIS
        设置 SmartHire 环境变量
    
    .PARAMETER Reset
        是否重置环境变量
    #>
    param([switch]$Reset)
    
    Write-Section "设置 SmartHire 环境变量"
    
    $scriptRoot = Get-ScriptRoot
    
    # 根路径（LAW-ENV-002: 相对路径）
    $env:SMARTHIRE_ROOT = $scriptRoot
    Write-Success "SMARTHIRE_ROOT = $scriptRoot"
    
    # 项目配置
    $env:SMARTHIRE_VERSION = $SMARTHIRE_VERSION
    Write-Success "SMARTHIRE_VERSION = $SMARTHIRE_VERSION"
    
    $env:SMARTHIRE_ENV = "development"
    Write-Success "SMARTHIRE_ENV = development"
    
    # 目录结构（相对路径）
    $env:SMARTHIRE_APPS_DIR = Join-Path $scriptRoot "apps"
    Write-Info "SMARTHIRE_APPS_DIR = apps"
    
    $env:SMARTHIRE_PACKAGES_DIR = Join-Path $scriptRoot "packages"
    Write-Info "SMARTHIRE_PACKAGES_DIR = packages"
    
    $env:SMARTHIRE_DATA_DIR = Join-Path $scriptRoot "data"
    Write-Info "SMARTHIRE_DATA_DIR = data"
    
    $env:SMARTHIRE_EVIDENCE_DIR = Join-Path $scriptRoot "data" "evidence"
    Write-Info "SMARTHIRE_EVIDENCE_DIR = data/evidence"
    
    $env:SMARTHIRE_PROFILES_DIR = Join-Path $scriptRoot "data" "profiles"
    Write-Info "SMARTHIRE_PROFILES_DIR = data/profiles"
    
    $env:SMARTHIRE_WORKSPACE_DIR = Join-Path $scriptRoot "workspace"
    Write-Info "SMARTHIRE_WORKSPACE_DIR = workspace"
    
    $env:SMARTHIRE_LOGS_DIR = Join-Path $scriptRoot "logs"
    Write-Info "SMARTHIRE_LOGS_DIR = logs"
    
    $env:SMARTHIRE_BACKUPS_DIR = Join-Path $scriptRoot "backups"
    Write-Info "SMARTHIRE_BACKUPS_DIR = backups"
    
    # 进程配置
    $env:SMARTHIRE_MESSAGE_ENABLED = "1"
    Write-Info "SMARTHIRE_MESSAGE_ENABLED = 1"
    
    $env:SMARTHIRE_PLAN_ENABLED = "1"
    Write-Info "SMARTHIRE_PLAN_ENABLED = 1"
    
    $env:SMARTHIRE_EXECUTE_ENABLED = "1"
    Write-Info "SMARTHIRE_EXECUTE_ENABLED = 1"
    
    $env:SMARTHIRE_WATCHDOG_ENABLED = "1"
    Write-Info "SMARTHIRE_WATCHDOG_ENABLED = 1"
    
    # Redis 配置
    $env:SMARTHIRE_REDIS_HOST = "127.0.0.1"
    Write-Info "SMARTHIRE_REDIS_HOST = 127.0.0.1"
    
    $env:SMARTHIRE_REDIS_PORT = "6379"
    Write-Info "SMARTHIRE_REDIS_PORT = 6379"
    
    $env:SMARTHIRE_REDIS_DB = "0"
    Write-Info "SMARTHIRE_REDIS_DB = 0"
    
    # Python 配置
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Python 版本: $pythonVersion"
        $env:SMARTHIRE_PYTHON_PATH = "python"
    } else {
        Write-Warning "Python 未找到，请安装 Python 3.10+"
    }
    
    # 编码配置（COMPOUND.md ENV-03: GBK/UTF-8 双向清洗）
    $env:PYTHONIOENCODING = "utf-8"
    Write-Info "PYTHONIOENCODING = utf-8"
    
    $env:SMARTHIRE_ENCODING = "utf-8"
    Write-Info "SMARTHIRE_ENCODING = utf-8"
    
    # Job Objects 配置（COMPOUND.md ENV-04: Win32 Job Objects）
    $env:SMARTHIRE_USE_JOB_OBJECTS = "1"
    Write-Info "SMARTHIRE_USE_JOB_OBJECTS = 1"
    
    # 路径深度限制（COMPOUND.md ENV-01）
    $env:SMARTHIRE_MAX_PATH_DEPTH = "5"
    Write-Info "SMARTHIRE_MAX_PATH_DEPTH = 5"
    
    $env:SMARTHIRE_MAX_PATH_LENGTH = "260"
    Write-Info "SMARTHIRE_MAX_PATH_LENGTH = 260"
    
    # 测试覆盖率目标（MAP v2.0 Phase 1）
    $env:SMARTHIRE_TARGET_COVERAGE = "80"
    Write-Info "SMARTHIRE_TARGET_COVERAGE = 80%"
    
    # MTTR 目标（MAP v2.0 Phase 1）
    $env:SMARTHIRE_TARGET_MTTR = "30"
    Write-Info "SMARTHIRE_TARGET_MTTR = 30 分钟"
    
    Write-Section "环境变量设置完成"
    Write-Success "所有 SmartHire 环境变量已设置"
    Write-Info "运行 'python swan.py --help' 查看可用命令"
}

function Reset-SmartHireEnvironment {
    <#
    .SYNOPSIS
        重置 SmartHire 环境变量
    #>
    Write-Section "重置 SmartHire 环境变量"
    
    $envVars = @(
        "SMARTHIRE_ROOT",
        "SMARTHIRE_VERSION",
        "SMARTHIRE_ENV",
        "SMARTHIRE_APPS_DIR",
        "SMARTHIRE_PACKAGES_DIR",
        "SMARTHIRE_DATA_DIR",
        "SMARTHIRE_EVIDENCE_DIR",
        "SMARTHIRE_PROFILES_DIR",
        "SMARTHIRE_WORKSPACE_DIR",
        "SMARTHIRE_LOGS_DIR",
        "SMARTHIRE_BACKUPS_DIR",
        "SMARTHIRE_MESSAGE_ENABLED",
        "SMARTHIRE_PLAN_ENABLED",
        "SMARTHIRE_EXECUTE_ENABLED",
        "SMARTHIRE_WATCHDOG_ENABLED",
        "SMARTHIRE_REDIS_HOST",
        "SMARTHIRE_REDIS_PORT",
        "SMARTHIRE_REDIS_DB",
        "SMARTHIRE_PYTHON_PATH",
        "SMARTHIRE_ENCODING",
        "SMARTHIRE_USE_JOB_OBJECTS",
        "SMARTHIRE_MAX_PATH_DEPTH",
        "SMARTHIRE_MAX_PATH_LENGTH",
        "SMARTHIRE_TARGET_COVERAGE",
        "SMARTHIRE_TARGET_MTTR"
    )
    
    foreach ($var in $envVars) {
        if (Test-Path "env:$var") {
            Remove-Item -Path "env:$var" -Force
            Write-Info "已清除: $var"
        }
    }
    
    Write-Success "所有 SmartHire 环境变量已重置"
}

function Test-SmartHireEnvironment {
    <#
    .SYNOPSIS
        测试 SmartHire 环境变量有效性
    #>
    Write-Section "测试 SmartHire 环境变量"
    
    $testResults = @()
    
    # 必需的环境变量
    $requiredVars = @{
        "SMARTHIRE_ROOT" = "项目根目录"
        "SMARTHIRE_VERSION" = "项目版本"
        "SMARTHIRE_ENV" = "运行环境"
        "SMARTHIRE_APPS_DIR" = "应用目录"
        "SMARTHIRE_PACKAGES_DIR" = "包目录"
        "SMARTHIRE_DATA_DIR" = "数据目录"
        "SMARTHIRE_WORKSPACE_DIR" = "工作空间目录"
        "SMARTHIRE_LOGS_DIR" = "日志目录"
    }
    
    foreach ($var in $requiredVars.Keys) {
        $value = [System.Environment]::GetEnvironmentVariable($var)
        if ($value) {
            Write-Success "$($requiredVars[$var]): $value"
            $testResults += $true
        } else {
            Write-Error "$($requiredVars[$var]): 未设置"
            $testResults += $false
        }
    }
    
    # 测试路径合规性（LAW-ENV-002）
    Write-Section "测试路径合规性"
    
    $scriptRoot = Get-ScriptRoot
    
    # 测试根路径深度
    $depth = ($scriptRoot -split '\\|/').Count
    if ($depth -le 5) {
        Write-Success "根路径深度: $depth 层 (≤ 5 层) ✅"
    } else {
        Write-Error "根路径深度: $depth 层 (> 5 层) ❌"
    }
    
    # 测试根路径长度
    if ($scriptRoot.Length -le 260) {
        Write-Success "根路径长度: $($scriptRoot.Length) 字符 (≤ 260 字符) ✅"
    } else {
        Write-Error "根路径长度: $($scriptRoot.Length) 字符 (> 260 字符) ❌"
    }
    
    # 测试 Python 环境
    Write-Section "测试 Python 环境"
    
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Python: $pythonVersion"
    } else {
        Write-Warning "Python 未找到"
    }
    
    # 测试 Redis 连接
    Write-Section "测试 Redis 连接"
    
    try {
        $redisClient = redis-cli ping 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Redis: 连接成功"
        } else {
            Write-Warning "Redis: 连接失败或未运行"
        }
    } catch {
        Write-Warning "Redis: redis-cli 未找到"
    }
    
    # 总结
    Write-Section "测试总结"
    
    $passedTests = ($testResults | Where-Object { $_ -eq $true }).Count
    $totalTests = $testResults.Count
    
    if ($passedTests -eq $totalTests) {
        Write-Success "所有测试通过 ($passedTests/$totalTests)"
    } else {
        Write-Warning "部分测试失败 ($passedTests/$totalTests)"
    }
}

function Show-Help {
    <#
    .SYNOPSIS
        显示帮助信息
    #>
    Write-Section "帮助信息"
    
    Write-Host ""
    Write-Host "用法:" -ForegroundColor Cyan
    Write-Host "  .\start.ps1              # 设置环境变量并显示状态" -ForegroundColor White
    Write-Host "  .\start.ps1 -Reset      # 重置环境变量" -ForegroundColor White
    Write-Host "  .\start.ps1 -Test       # 测试环境变量有效性" -ForegroundColor White
    Write-Host "  .\start.ps1 -Help       # 显示帮助信息" -ForegroundColor White
    Write-Host ""
    
    Write-Host "环境变量:" -ForegroundColor Cyan
    Write-Host "  SMARTHIRE_ROOT           项目根目录" -ForegroundColor White
    Write-Host "  SMARTHIRE_VERSION        项目版本" -ForegroundColor White
    Write-Host "  SMARTHIRE_ENV            运行环境 (development/production)" -ForegroundColor White
    Write-Host "  SMARTHIRE_APPS_DIR       应用目录 (apps)" -ForegroundColor White
    Write-Host "  SMARTHIRE_PACKAGES_DIR   包目录 (packages)" -ForegroundColor White
    Write-Host "  SMARTHIRE_DATA_DIR       数据目录 (data)" -ForegroundColor White
    Write-Host "  SMARTHIRE_LOGS_DIR       日志目录 (logs)" -ForegroundColor White
    Write-Host ""
    
    Write-Host "合规性:" -ForegroundColor Cyan
    Write-Host "  ✅ LAW-ENV-002: 无绝对路径硬编码" -ForegroundColor Green
    Write-Host "  ✅ LAW-ENV-001: Windows 原生运行（无容器化）" -ForegroundColor Green
    Write-Host "  ✅ COMPOUND.md ENV-01: 根路径锚定" -ForegroundColor Green
    Write-Host ""
}

# =============================================================================
# 主入口
# =============================================================================

function Main {
    # 显示横幅
    Write-Banner
    
    # 处理命令行参数
    if ($Help) {
        Show-Help
        return
    }
    
    if ($Reset) {
        Reset-SmartHireEnvironment
        return
    }
    
    if ($Test) {
        Test-SmartHireEnvironment
        return
    }
    
    # 默认行为：设置环境变量
    Set-SmartHireEnvironment
    
    # 显示环境变量状态
    Write-Section "当前环境变量"
    
    $envVars = @(
        "SMARTHIRE_ROOT",
        "SMARTHIRE_VERSION",
        "SMARTHIRE_ENV",
        "SMARTHIRE_APPS_DIR",
        "SMARTHIRE_PACKAGES_DIR",
        "SMARTHIRE_DATA_DIR",
        "SMARTHIRE_LOGS_DIR",
        "SMARTHIRE_REDIS_HOST",
        "SMARTHIRE_REDIS_PORT"
    )
    
    foreach ($var in $envVars) {
        $value = [System.Environment]::GetEnvironmentVariable($var)
        if ($value) {
            Write-Host "  $var = $value" -ForegroundColor Gray
        }
    }
    
    Write-Host ""
    Write-Success "环境变量设置完成，可以运行 'python swan.py' 启动系统"
}

# 执行主函数
Main