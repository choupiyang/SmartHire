#!/usr/bin/env python3
"""
SmartHire System Starter (系统点火入口)

Version: 1.0.0
Compliance: LAW-ENV-002 (无绝对路径硬编码), LAW-ENG-001 (职责物理隔离)

Description:
    SmartHire 系统的主启动入口，负责初始化环境、启动四进程架构（MESSAGE/PLAN/EXECUTE/WATCHDOG）。
    严格遵循相对路径原则，支持 Windows 原生运行。

Architecture:
    - MESSAGE (进程 A): SOUL 层 - 职业管家渲染
    - PLAN (进程 B): SKILLS 层 - 契约认知层
    - EXECUTE (进程 C): INTUITION 层 - 物理存证层
    - WATCHDOG (进程 D): 免疫层 - 故障自愈与合规监控

Usage:
    python ss.py

Environment:
    - Windows 11 Native (无容器化)
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
║                    Phase 1 Development                      ║
║              System Starter (系统点火入口)                  ║
║                                                            ║
║  Version: 1.0.0 | Architecture: MESSAGE/PLAN/EXECUTE/WATCHDOG ║
║  Compliance: LAW-ENV-002 | LAW-ENG-001 | COMPOUND.md ENV-01  ║
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
            print("  python ss.py              # 启动 SmartHire 系统")
            print("  python ss.py --init       # 仅初始化环境")
            print("  python ss.py --stop       # 停止所有进程")
            print("  python ss.py --status     # 查看进程状态")
            print("  python ss.py --help       # 显示帮助信息")
            sys.exit(0)
        
        if command == "--init":
            # 仅初始化环境
            config = SystemConfig()
            initializer = EnvironmentInitializer(config)
            initializer.initialize()
            print("✅ 环境初始化完成")
            sys.exit(0)
        
        if command == "--stop":
            # 停止所有进程
            print("🛑 停止 SmartHire 系统...")
            # TODO: 实现进程查找和停止逻辑
            sys.exit(0)
        
        if command == "--status":
            # 查看进程状态
            print("📊 查看进程状态...")
            # TODO: 实现进程状态查询逻辑
            sys.exit(0)
    
    # 创建系统配置
    config = SystemConfig()
    
    # 初始化环境
    initializer = EnvironmentInitializer(config)
    initializer.initialize()
    
    # 创建进程管理器
    process_manager = ProcessManager(config)
    
    # 启动所有进程
    process_manager.start_all()
    
    # 监控进程
    process_manager.monitor()


if __name__ == "__main__":
    main()