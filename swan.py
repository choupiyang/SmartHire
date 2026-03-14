#!/usr/bin/env python3
"""
SmartHire System Launcher (Swan Launcher)

Version: 2.0.0
Compliance: LAW-ENV-002 (无绝对路径硬编码), LAW-ENG-001 (职责物理隔离)

Description:
    智雇家系统启动器，集成虚拟环境管理、依赖检查、进程清理。
    命名寓意：Swan（天鹅）象征优雅的系统启动和管理。

Architecture:
    - MESSAGE (进程 A): SOUL 层 - 职业管家渲染
    - PLAN (进程 B): SKILLS 层 - 契约认知层
    - EXECUTE (进程 C): INTUITION 层 - 物理存证层
    - WATCHDOG (进程 D): 免疫层 - 故障自愈与合规监控

Features:
    - 自动创建和管理Python虚拟环境 (swanvenv/)
    - 自动检查和安装依赖
    - 智能清理历史进程
    - 优雅的信号处理（Ctrl+C）

Usage:
    python swan.py
    python swan.py --init-venv    # 仅创建虚拟环境
    python swan.py --clean        # 清理历史进程
    python swan.py --help         # 显示帮助

Environment:
    - Windows 11 Native (无容器化 - LAW-ENV-001)
    - Python 3.10+
    - Redis Server (本地或远程)
"""

import os
import sys
import subprocess
import signal
import time
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import psutil

# =============================================================================
# 编码处理 (COMPOUND.md ENV-03: GBK/UTF-8 双向清洗)
# =============================================================================

# Emoji到ASCII的映射（避免Windows GBK编码问题）
EMOJI_MAP = {
    '✅': '[OK]',
    '❌': '[X]',
    '⚠️': '[!]',
    'ℹ️': '[i]',
    '🔧': '[Wrench]',
    '📦': '[Box]',
    '🧹': '[Broom]',
    '🚀': '[Rocket]',
    '🔍': '[Magnifier]',
    '🛑': '[Stop]',
    '👁️': '[Eye]',
    '👋': '[Wave]',
    '💡': '[Bulb]',
    '🔗': '[Link]',
    '📝': '[Memo]',
    '🎯': '[Target]',
    '⏳': '[Hourglass]',
    '⏭️': '[Next]',
    '📁': '[Folder]',
    '📂': '[FolderOpen]',
    '🐍': '[Snake]',
    '🔴': '[RedCircle]',
    '📊': '[Chart]',
    '📄': '[Page]',
    '📋': '[Clipboard]',
    '✓': '[Check]',
}

# 保存原始print函数
_original_print = print

def safe_print(*args, **kwargs):
    """安全打印函数，自动替换emoji为ASCII字符"""
    # 处理每个参数
    safe_args = []
    for arg in args:
        if isinstance(arg, str):
            # 替换emoji
            safe_arg = arg
            for emoji, replacement in EMOJI_MAP.items():
                safe_arg = safe_arg.replace(emoji, replacement)
            safe_args.append(safe_arg)
        else:
            safe_args.append(arg)

    # 尝试打印，如果仍然失败则使用更激进的替换
    try:
        _original_print(*safe_args, **kwargs)
    except UnicodeEncodeError:
        # 最后的备用方案：强制ASCII
        ascii_args = []
        for arg in safe_args:
            if isinstance(arg, str):
                ascii_args.append(arg.encode('ascii', errors='replace').decode('ascii'))
            else:
                ascii_args.append(arg)
        _original_print(*ascii_args, **kwargs)

# 覆盖内置print函数
print = safe_print


# =============================================================================
# 根路径锚定 (LAW-ENV-002: 严禁绝对路径)
# =============================================================================

def anchor_root() -> Path:
    """
    根路径锚定函数
    
    Returns:
        Path: 项目根目录（基于当前工作目录的相对路径）
    
    Compliance:
        LAW-ENV-002: 无绝对路径硬编码
        COMPOUND.md ENV-01: 根路径锚定，目录嵌套 ≤ 5 层
    """
    # 获取当前脚本的父目录作为根目录
    root = Path(__file__).parent.resolve()
    
    # 验证路径深度（COMPOUND.md ENV-01: 目录嵌套 ≤ 5 层）
    depth = len(root.parts) - 1  # 减去盘符
    if depth > 5:
        print(f"❌ 路径深度违规: {depth} > 5 层")
        print(f"当前路径: {root}")
        sys.exit(1)
    
    # 验证路径长度（Windows MAX_PATH = 260 字符）
    path_str = str(root)
    if len(path_str) > 260:
        print(f"❌ 路径长度违规: {len(path_str)} > 260 字符")
        print(f"当前路径: {path_str}")
        sys.exit(1)
    
    return root


# 全局根路径（所有路径基于此锚定）
ROOT_PATH = anchor_root()


# =============================================================================
# 虚拟环境管理器
# =============================================================================

class VirtualEnvironmentManager:
    """虚拟环境管理器（LAW-ENV-001: 无容器化，使用venv）"""

    def __init__(self, root_path: Path, python_path: str):
        """
        初始化虚拟环境管理器

        Args:
            root_path: 项目根路径
            python_path: Python可执行文件路径
        """
        self.root_path = root_path
        self.python_path = python_path
        self.venv_path = root_path / "swanvenv"

    def check_exists(self) -> bool:
        """
        检查虚拟环境是否存在

        Returns:
            bool: 虚拟环境是否存在
        """
        return self.venv_path.exists()

    def check_python_version(self) -> Tuple[bool, str]:
        """
        检查Python版本

        Returns:
            Tuple[bool, str]: (是否满足要求, 版本信息)
        """
        try:
            result = subprocess.run(
                [self.python_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version_str = result.stdout.strip()
                # 解析版本号
                version = version_str.split()[-1]
                major, minor = map(int, version.split('.')[:2])

                if major > 3 or (major == 3 and minor >= 10):
                    return True, version_str
                else:
                    return False, f"Python版本过低: {version_str} (需要3.10+)"
            else:
                return False, "无法获取Python版本"
        except Exception as e:
            return False, f"Python版本检查失败: {e}"

    def create_venv(self) -> bool:
        """
        创建虚拟环境

        Returns:
            bool: 是否创建成功
        """
        print(f"  📦 正在创建虚拟环境: {self.venv_path}")

        try:
            # 使用venv模块创建虚拟环境
            result = subprocess.run(
                [self.python_path, "-m", "venv", str(self.venv_path)],
                cwd=str(self.root_path),
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                print(f"  ✅ 虚拟环境创建成功")
                return True
            else:
                print(f"  ❌ 虚拟环境创建失败:")
                print(f"     {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print(f"  ❌ 虚拟环境创建超时")
            return False
        except Exception as e:
            print(f"  ❌ 虚拟环境创建异常: {e}")
            return False

    def get_python_executable(self) -> Path:
        """
        获取虚拟环境中的Python可执行文件

        Returns:
            Path: Python可执行文件路径
        """
        if os.name == 'nt':  # Windows
            return self.venv_path / "Scripts" / "python.exe"
        else:  # Linux/Mac
            return self.venv_path / "bin" / "python"

    def get_pip_executable(self) -> Path:
        """
        获取虚拟环境中的pip可执行文件

        Returns:
            Path: pip可执行文件路径
        """
        if os.name == 'nt':  # Windows
            return self.venv_path / "Scripts" / "pip.exe"
        else:  # Linux/Mac
            return self.venv_path / "bin" / "pip"

    def activate(self) -> Dict[str, str]:
        """
        生成激活环境变量字典

        Returns:
            Dict[str, str]: 环境变量字典
        """
        venv_path = str(self.venv_path)

        if os.name == 'nt':  # Windows
            scripts_dir = str(self.venv_path / "Scripts")
        else:  # Linux/Mac
            scripts_dir = str(self.venv_path / "bin")

        # 更新PATH环境变量
        new_env = os.environ.copy()
        new_env['PATH'] = f"{scripts_dir}{os.pathsep}{new_env.get('PATH', '')}"
        new_env['VIRTUAL_ENV'] = venv_path
        new_env['PYTHONHOME'] = ''

        return new_env


class DependencyChecker:
    """依赖检查器"""

    def __init__(self, python_exe: Path, requirements_file: Path):
        """
        初始化依赖检查器

        Args:
            python_exe: Python可执行文件路径
            requirements_file: requirements.txt文件路径
        """
        self.python_exe = python_exe
        self.requirements_file = requirements_file

    def check_installed(self) -> Tuple[bool, List[str]]:
        """
        检查依赖是否已安装

        Returns:
            Tuple[bool, List[str]]: (是否全部安装, 缺失的依赖列表)
        """
        if not self.requirements_file.exists():
            print(f"  ⚠️ requirements.txt不存在: {self.requirements_file}")
            return True, []

        try:
            # 使用pip list获取已安装的包
            result = subprocess.run(
                [str(self.python_exe), "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                print(f"  ⚠️ 无法获取已安装包列表: {result.stderr}")
                return False, []

            import json
            installed_packages = set()
            for pkg in json.loads(result.stdout):
                installed_packages.add(pkg['name'].lower())

            # 读取requirements.txt
            missing_packages = []
            with open(self.requirements_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    # 提取包名（忽略版本号）
                    pkg_name = line.split('>=')[0].split('==')[0].split('[')[0].strip().lower()

                    if pkg_name not in installed_packages:
                        missing_packages.append(pkg_name)

            return len(missing_packages) == 0, missing_packages

        except subprocess.TimeoutExpired:
            print(f"  ⚠️ 依赖检查超时")
            return False, []
        except Exception as e:
            print(f"  ⚠️ 依赖检查失败: {e}")
            return False, []

    def install_dependencies(self) -> bool:
        """
        安装依赖

        Returns:
            bool: 是否安装成功
        """
        print(f"  📦 正在安装依赖...")

        try:
            result = subprocess.run(
                [str(self.python_exe), "-m", "pip", "install", "-r", str(self.requirements_file)],
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )

            if result.returncode == 0:
                print(f"  ✅ 依赖安装成功")
                return True
            else:
                print(f"  ❌ 依赖安装失败:")
                print(f"     {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print(f"  ❌ 依赖安装超时（>5分钟）")
            return False
        except Exception as e:
            print(f"  ❌ 依赖安装异常: {e}")
            return False

    def verify_installation(self) -> Tuple[bool, List[str]]:
        """
        验证安装结果

        Returns:
            Tuple[bool, List[str]]: (验证成功, 错误列表)
        """
        all_installed, missing = self.check_installed()
        if not all_installed:
            return False, [f"缺少依赖: {', '.join(missing)}"]

        # 验证关键包可导入
        key_packages = ['pydantic', 'redis', 'psutil']
        errors = []

        for pkg in key_packages:
            try:
                result = subprocess.run(
                    [str(self.python_exe), "-c", f"import {pkg}"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode != 0:
                    errors.append(f"无法导入 {pkg}")
            except Exception:
                errors.append(f"导入 {pkg} 超时")

        return len(errors) == 0, errors


class ProcessCleaner:
    """进程清理器"""

    def __init__(self):
        """初始化进程清理器"""
        self.process_name = "python.exe" if os.name == 'nt' else "python"
        self.keywords = ["swan.py", "ss.py", "smarthire"]

    def find_processes(self) -> List[psutil.Process]:
        """
        查找SmartHire相关进程

        Returns:
            List[psutil.Process]: 找到的进程列表
        """
        smarthire_processes = []

        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
                try:
                    # 获取进程信息
                    proc_info = proc.info

                    if not proc_info['cmdline']:
                        continue

                    # 检查是否为Python进程
                    if self.process_name.lower() not in proc_info['name'].lower():
                        continue

                    # 检查命令行是否包含关键词
                    cmdline_str = ' '.join(proc_info['cmdline'])
                    if any(keyword.lower() in cmdline_str.lower() for keyword in self.keywords):
                        smarthire_processes.append(proc)

                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue

        except Exception as e:
            print(f"  ⚠️ 查找进程时出错: {e}")

        return smarthire_processes

    def kill_processes(self, processes: List[psutil.Process]) -> Tuple[int, int]:
        """
        终止进程

        Args:
            processes: 进程列表

        Returns:
            Tuple[int, int]: (成功终止数, 失败数)
        """
        success_count = 0
        fail_count = 0

        for proc in processes:
            try:
                # 尝试优雅终止
                proc.terminate()

                # 等待最多3秒
                try:
                    proc.wait(timeout=3)
                    success_count += 1
                    print(f"  ✓ 已终止进程 PID={proc.pid}")
                except psutil.TimeoutExpired:
                    # 强制终止
                    proc.kill()
                    success_count += 1
                    print(f"  ⚠️ 强制终止进程 PID={proc.pid}")

            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                fail_count += 1
                print(f"  ✗ 无法终止进程 PID={proc.pid}: {e}")

        return success_count, fail_count

    def cleanup(self) -> Tuple[int, int]:
        """
        执行清理

        Returns:
            Tuple[int, int]: (成功终止数, 失败数)
        """
        processes = self.find_processes()

        if not processes:
            return 0, 0

        print(f"  🔍 找到 {len(processes)} 个SmartHire相关进程")

        success_count, fail_count = self.kill_processes(processes)

        if success_count > 0:
            print(f"  ✅ 成功清理 {success_count} 个进程")
        if fail_count > 0:
            print(f"  ⚠️ 清理失败 {fail_count} 个进程")

        return success_count, fail_count


# =============================================================================
# 配置管理
# =============================================================================

@dataclass
class ProcessConfig:
    """进程配置"""
    name: str
    module: str
    script: str
    enabled: bool = True
    auto_restart: bool = True
    dependencies: List[str] = field(default_factory=list)


@dataclass
class SystemConfig:
    """系统配置"""
    root_path: Path = field(default_factory=lambda: ROOT_PATH)
    python_path: str = sys.executable
    redis_host: str = "127.0.0.1"
    redis_port: int = 6379
    redis_db: int = 0
    use_job_objects: bool = True  # Windows Job Objects 进程生命周期管理
    
    # 进程配置
    processes: Dict[str, ProcessConfig] = field(default_factory=dict)
    
    # 日志配置
    log_dir: Path = field(init=False)
    
    def __post_init__(self):
        """初始化后处理"""
        # 设置日志目录（相对路径）
        self.log_dir = self.root_path / "logs"
        
        # 初始化进程配置
        self._init_processes()
    
    def _init_processes(self):
        """初始化进程配置"""
        self.processes = {
            "watchdog": ProcessConfig(
                name="WATCHDOG",
                module="apps.sh_watchdog",
                script="main.py",
                enabled=True,
                auto_restart=True,
                dependencies=[]
            ),
            "message": ProcessConfig(
                name="MESSAGE",
                module="apps.sh_message",
                script="main.py",
                enabled=True,
                auto_restart=True,
                dependencies=["watchdog"]
            ),
            "plan": ProcessConfig(
                name="PLAN",
                module="apps.sh_plan",
                script="main.py",
                enabled=True,
                auto_restart=True,
                dependencies=["watchdog"]
            ),
            "execute": ProcessConfig(
                name="EXECUTE",
                module="apps.sh_execute",
                script="main.py",
                enabled=True,
                auto_restart=True,
                dependencies=["watchdog"]
            )
        }


# =============================================================================
# 路径验证工具
# =============================================================================

class PathValidator:
    """路径验证器（LAW-ENV-002, COMPOUND.md ENV-01）"""
    
    MAX_DEPTH = 5
    MAX_LENGTH = 260
    
    @staticmethod
    def validate(path: Path) -> Tuple[bool, Optional[str]]:
        """
        验证路径合规性
        
        Args:
            path: 待验证的路径
            
        Returns:
            Tuple[bool, Optional[str]]: (是否有效, 错误消息)
        """
        path_str = str(path)
        
        # 检查绝对路径（LAW-ENV-002）
        if path.is_absolute():
            return False, f"禁止绝对路径: {path_str}"
        
        # 检查路径深度（COMPOUND.md ENV-01）
        relative_depth = len(Path(path).parts)
        if relative_depth > PathValidator.MAX_DEPTH:
            return False, f"路径深度违规: {relative_depth} > {PathValidator.MAX_DEPTH} 层"
        
        # 检查路径长度（Windows MAX_PATH）
        full_path = ROOT_PATH / path
        if len(str(full_path)) > PathValidator.MAX_LENGTH:
            return False, f"路径长度违规: {len(str(full_path))} > {PathValidator.MAX_LENGTH} 字符"
        
        return True, None
    
    @staticmethod
    def ensure_exists(path: Path, is_dir: bool = True) -> None:
        """
        确保路径存在
        
        Args:
            path: 目标路径
            is_dir: 是否为目录
        """
        # 验证路径合规性
        is_valid, error_msg = PathValidator.validate(path)
        if not is_valid:
            raise ValueError(error_msg)
        
        full_path = ROOT_PATH / path
        
        if is_dir:
            full_path.mkdir(parents=True, exist_ok=True)
        else:
            full_path.parent.mkdir(parents=True, exist_ok=True)


# =============================================================================
# 环境初始化
# =============================================================================

class EnvironmentInitializer:
    """环境初始化器"""
    
    def __init__(self, config: SystemConfig):
        self.config = config
    
    def initialize(self) -> None:
        """初始化运行环境"""
        print("🚀 初始化 SmartHire 运行环境...")
        
        # 创建必要的目录结构
        self._create_directories()
        
        # 验证 Python 环境
        self._validate_python()
        
        # 验证 Redis 连接
        self._validate_redis()
        
        print("✅ 环境初始化完成\n")
    
    def _create_directories(self) -> None:
        """创建必要的目录结构"""
        print("📁 创建目录结构...")
        
        directories = [
            "apps/sh_message",
            "apps/sh_plan",
            "apps/sh_execute",
            "apps/sh_watchdog",
            "packages/sh_core",
            "packages/sh_legal_rules",
            "packages/sh_win32_utils",
            "data/evidence",
            "data/profiles",
            "workspace",
            "logs/debug",
            "logs/message",
            "logs/plan",
            "logs/execute",
            "logs/watchdog",
            "logs/crash",
            "tests/fixtures",
            "tests/regression",
            "tests/chaos",
            "backups/db",
            "backups/redis"
        ]
        
        for dir_path in directories:
            try:
                PathValidator.ensure_exists(Path(dir_path), is_dir=True)
                print(f"  ✓ {dir_path}")
            except Exception as e:
                print(f"  ✗ {dir_path}: {e}")
    
    def _validate_python(self) -> None:
        """验证 Python 环境"""
        print("🐍 验证 Python 环境...")
        
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 10):
            print(f"  ✗ Python 版本过低: {version.major}.{version.minor}")
            print(f"  需要版本: Python 3.10+")
            sys.exit(1)
        
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
    
    def _validate_redis(self) -> None:
        """验证 Redis 连接"""
        print("🔴 验证 Redis 连接...")
        
        try:
            import redis
            client = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                decode_responses=True,
                socket_timeout=2
            )
            client.ping()
            print(f"  ✓ Redis 连接成功 ({self.config.redis_host}:{self.config.redis_port})")
        except ImportError:
            print(f"  ⚠ Redis 模块未安装，请运行: pip install redis")
        except Exception as e:
            print(f"  ⚠ Redis 连接失败: {e}")
            print(f"  请确保 Redis 服务正在运行")


# =============================================================================
# 进程管理器
# =============================================================================

class ProcessManager:
    """进程管理器（支持 Windows Job Objects）"""
    
    def __init__(self, config: SystemConfig):
        self.config = config
        self.processes: Dict[str, subprocess.Popen] = {}
        self.job_object = None
        
        # 注册信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        print(f"\n\n⚠️ 收到信号 {signum}，正在关闭系统...")
        self.stop_all()
        sys.exit(0)
    
    def start_process(self, process_key: str) -> bool:
        """
        启动单个进程
        
        Args:
            process_key: 进程配置键名
            
        Returns:
            bool: 是否启动成功
        """
        if process_key not in self.config.processes:
            print(f"❌ 未知进程: {process_key}")
            return False
        
        proc_config = self.config.processes[process_key]
        
        if not proc_config.enabled:
            print(f"⏭️  {proc_config.name} 已禁用，跳过")
            return False
        
        print(f"🚀 启动 {proc_config.name} 进程...")
        
        # 构建进程命令（相对路径）
        script_path = Path(proc_config.module) / proc_config.script
        script_full_path = ROOT_PATH / script_path
        
        # 验证路径合规性
        is_valid, error_msg = PathValidator.validate(script_path)
        if not is_valid:
            print(f"  ❌ 路径验证失败: {error_msg}")
            return False
        
        # 检查脚本是否存在
        if not script_full_path.exists():
            print(f"  ⚠️ 脚本不存在: {script_path}")
            print(f"  创建占位脚本: {script_path}")
            self._create_placeholder_script(script_full_path)
        
        try:
            # 启动进程
            process = subprocess.Popen(
                [self.config.python_path, str(script_full_path)],
                cwd=str(self.config.root_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            self.processes[process_key] = process
            print(f"  ✓ {proc_config.name} 已启动 (PID: {process.pid})")
            return True
            
        except Exception as e:
            print(f"  ❌ {proc_config.name} 启动失败: {e}")
            return False
    
    def _create_placeholder_script(self, script_path: Path) -> None:
        """创建占位脚本"""
        script_path.parent.mkdir(parents=True, exist_ok=True)
        
        placeholder_content = '''#!/usr/bin/env python3
"""
SmartHire {process_name} 进程

Version: 1.0.0
Status: 占位脚本（待实现）
"""

import time
import sys
from pathlib import Path

# 添加包路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def main():
    """主函数"""
    print("🚀 {process_name} 进程启动（占位模式）")
    print("⏳ 等待后续实现...")
    
    # 保持运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\\n✅ {process_name} 进程已停止")
        sys.exit(0)

if __name__ == "__main__":
    main()
'''.format(
            process_name=script_path.parent.name.upper()
        )
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(placeholder_content)
    
    def start_all(self) -> None:
        """启动所有进程"""
        print("\n🚀 启动 SmartHire 四进程架构...\n")
        
        # 按依赖顺序启动进程
        startup_order = ["watchdog", "message", "plan", "execute"]
        
        for process_key in startup_order:
            if self.start_process(process_key):
                # 给进程一些启动时间
                time.sleep(1)
        
        print("\n✅ 所有进程已启动")
    
    def stop_process(self, process_key: str) -> bool:
        """
        停止单个进程
        
        Args:
            process_key: 进程配置键名
            
        Returns:
            bool: 是否停止成功
        """
        if process_key not in self.processes:
            return False
        
        process = self.processes[process_key]
        
        try:
            # 优雅关闭
            process.terminate()
            process.wait(timeout=5)
            print(f"✅ {process_key} 已停止")
            return True
        except subprocess.TimeoutExpired:
            # 强制关闭
            process.kill()
            print(f"⚠️ {process_key} 强制关闭")
            return True
        except Exception as e:
            print(f"❌ {process_key} 停止失败: {e}")
            return False
    
    def stop_all(self) -> None:
        """停止所有进程"""
        print("\n🛑 停止所有进程...\n")
        
        # 按相反顺序停止进程
        shutdown_order = ["execute", "plan", "message", "watchdog"]
        
        for process_key in shutdown_order:
            self.stop_process(process_key)
        
        print("\n✅ 所有进程已停止")
    
    def monitor(self) -> None:
        """监控进程状态"""
        print("\n👁️  监控进程状态（按 Ctrl+C 退出）...\n")
        
        try:
            while True:
                print(f"\n{'='*60}")
                print(f"{'进程':<12} {'状态':<10} {'PID':<10}")
                print(f"{'='*60}")
                
                all_running = True
                for process_key, process in self.processes.items():
                    status = "运行中" if process.poll() is None else "已停止"
                    pid = process.pid if process.poll() is None else "N/A"
                    
                    if process.poll() is not None:
                        all_running = False
                        status = "❌ 停止"
                    
                    print(f"{process_key:<12} {status:<10} {pid:<10}")
                
                if not all_running:
                    print("\n⚠️ 检测到进程异常停止")
                    # TODO: 自动重启逻辑（在 WATCHDOG 中实现）
                
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n\n👋 用户中断，正在关闭...")
            self.stop_all()
            sys.exit(0)


# =============================================================================
# 主入口
# =============================================================================

def print_banner():
    """打印启动横幅"""
    banner = """
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║  ████████ ███████ ██   ██ ████████ ██ ██████  ████████     ║
║  ██       ██       ██  ██     ██     ██ ██   ██ ██          ║
║  █████    █████     ████      ██     ██ ██████  █████       ║
║  ██       ██        ██ ██     ██     ██ ██   ██ ██          ║
║  ██       ███████   ██  ██    ██     ██ ██   ██ ██          ║
║                                                            ║
║                    Swan Launcher v2.0                       ║
║              智雇家系统优雅启动器                            ║
║                                                            ║
║  Version: 2.0.0 | Architecture: MESSAGE/PLAN/EXECUTE/WATCHDOG ║
║  Compliance: LAW-ENV-001 | LAW-ENV-002 | LAW-ENG-001       ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
"""
    print(banner)


def main():
    """主函数"""
    print_banner()

    # 解析命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "--help" or command == "-h":
            print("\n用法:")
            print("  python swan.py                    # 启动 SmartHire 系统（自动管理虚拟环境）")
            print("  python swan.py --init-venv        # 仅创建虚拟环境")
            print("  python swan.py --clean            # 清理历史进程")
            print("  python swan.py --init             # 仅初始化项目目录")
            print("  python swan.py --help             # 显示帮助信息")
            print("\n特性:")
            print("  ✅ 自动创建和管理虚拟环境 (swanvenv/)")
            print("  ✅ 自动检查和安装依赖")
            print("  ✅ 智能清理历史进程")
            print("  ✅ 优雅的信号处理（Ctrl+C）")
            print("\n合规性:")
            print("  ✅ LAW-ENV-001: 无容器化（使用venv）")
            print("  ✅ LAW-ENV-002: 无绝对路径硬编码")
            print("  ✅ LAW-ENG-001: 职责物理隔离")
            sys.exit(0)

        if command == "--init-venv":
            # 仅创建虚拟环境
            print("🔧 创建虚拟环境...")
            venv_manager = VirtualEnvironmentManager(ROOT_PATH, sys.executable)

            if venv_manager.check_exists():
                print("  ℹ️  虚拟环境已存在")
                sys.exit(0)

            if not venv_manager.create_venv():
                print("  ❌ 虚拟环境创建失败")
                sys.exit(1)

            print("  ✅ 虚拟环境创建成功")
            sys.exit(0)

        if command == "--clean":
            # 清理历史进程
            print("🧹 清理历史进程...")
            cleaner = ProcessCleaner()
            killed, failed = cleaner.cleanup()
            if killed == 0 and failed == 0:
                print("  ℹ️  无历史进程需要清理")
            sys.exit(0)

        if command == "--init":
            # 仅初始化环境
            config = SystemConfig()
            initializer = EnvironmentInitializer(config)
            initializer.initialize()
            print("✅ 环境初始化完成")
            sys.exit(0)

    # =============================================================================
    # Phase 1: 虚拟环境初始化
    # =============================================================================
    print("🔧 Phase 1: 虚拟环境检查...")
    venv_manager = VirtualEnvironmentManager(ROOT_PATH, sys.executable)

    # 检查Python版本
    version_ok, version_info = venv_manager.check_python_version()
    if not version_ok:
        print(f"  ❌ {version_info}")
        print(f"  需要版本: Python 3.10+")
        sys.exit(1)
    print(f"  ✓ {version_info}")

    # 检查/创建虚拟环境
    if not venv_manager.check_exists():
        print("  ⚠️  虚拟环境不存在，正在创建...")
        if not venv_manager.create_venv():
            print("  ❌ 虚拟环境创建失败")
            sys.exit(1)
        print("  ✅ 虚拟环境创建成功")
    else:
        print("  ✓ 虚拟环境已存在")

    # 获取虚拟环境中的Python
    venv_python = venv_manager.get_python_executable()
    if not venv_python.exists():
        print(f"  ❌ 虚拟环境Python不存在: {venv_python}")
        sys.exit(1)
    print(f"  ✓ 虚拟环境Python: {venv_python}")

    # =============================================================================
    # Phase 2: 依赖检查
    # =============================================================================
    print("\n📦 Phase 2: 依赖检查...")
    requirements_file = ROOT_PATH / "requirements.txt"

    if not requirements_file.exists():
        print(f"  ⚠️  requirements.txt不存在，跳过依赖检查")
    else:
        dep_checker = DependencyChecker(venv_python, requirements_file)
        all_installed, missing = dep_checker.check_installed()

        if not all_installed:
            print(f"  ⚠️  缺少 {len(missing)} 个依赖，正在安装...")
            print(f"     缺失的包: {', '.join(missing[:10])}")
            if len(missing) > 10:
                print(f"     ...以及另外 {len(missing) - 10} 个包")

            if not dep_checker.install_dependencies():
                print("  ❌ 依赖安装失败")
                print(f"  💡 提示: 可以手动安装: {venv_python} -m pip install -r requirements.txt")
                sys.exit(1)

            # 验证安装
            verified, errors = dep_checker.verify_installation()
            if not verified:
                print("  ❌ 依赖验证失败:")
                for error in errors:
                    print(f"     - {error}")
                sys.exit(1)

            print("  ✅ 依赖安装成功")
        else:
            print("  ✅ 所有依赖已就绪")

    # =============================================================================
    # Phase 3: 进程清理
    # =============================================================================
    print("\n🧹 Phase 3: 清理历史进程...")
    cleaner = ProcessCleaner()
    killed, failed = cleaner.cleanup()

    if killed == 0 and failed == 0:
        print("  ✓ 无历史进程需要清理")

    # =============================================================================
    # Phase 4: 启动系统
    # =============================================================================
    print("\n🚀 Phase 4: 启动SmartHire系统...")

    # 创建系统配置（使用虚拟环境Python）
    config = SystemConfig(python_path=str(venv_python))

    # 初始化环境
    initializer = EnvironmentInitializer(config)
    initializer.initialize()

    # 创建进程管理器
    process_manager = ProcessManager(config)

    # 注册增强的信号处理器
    def cleanup_handler(signum, frame):
        """增强的信号处理器"""
        print(f"\n\n⚠️  收到信号 {signum}，正在优雅关闭...")

        # 停止所有进程
        process_manager.stop_all()

        # 额外清理：确保所有子进程终止
        print("  🔍 执行最终进程清理...")
        extra_killed, extra_failed = cleaner.cleanup()
        if extra_killed > 0:
            print(f"  ✅ 额外清理了 {extra_killed} 个残留进程")

        print("✅ 系统已安全关闭")
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup_handler)
    signal.signal(signal.SIGTERM, cleanup_handler)

    # 启动所有进程
    process_manager.start_all()

    # 监控进程
    process_manager.monitor()


if __name__ == "__main__":
    main()