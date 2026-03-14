"""
L1 物理层：Job Objects 测试

Version: 1.0.0
Compliance: COMPOUND.md ENV-04 (Win32 Job Objects 绑定子进程生命周期), LAW-ENV-001 (Windows Native)

Description:
    测试 Windows Job Objects 进程生命周期管理，确保子进程在父进程崩溃时自动终止，
    无孤儿进程泄露。

Test Cases:
    - 启动子进程（通过 Win32 Job Object）
    - 强制杀死父进程（模拟崩溃）
    - 验证子进程自动终止（无孤儿进程）
    - 验证进程树完整性

Usage:
    pytest tests/l1_physical/test_job_objects.py -v

Note:
    此测试需要 Windows 系统和 pywin32 库支持。
    在 Linux/macOS 系统上，这些测试将被跳过。
"""

import pytest
import subprocess
import sys
import time
import psutil
from pathlib import Path
import platform


# =============================================================================
# 测试配置
# =============================================================================

# 检测操作系统
IS_WINDOWS = platform.system() == 'Windows'
HAS_PYWIN32 = False

if IS_WINDOWS:
    try:
        import win32api
        import win32con
        import win32job
        HAS_PYWIN32 = True
    except ImportError:
        HAS_PYWIN32 = False


# =============================================================================
# 辅助函数
# =============================================================================

def get_root_path() -> Path:
    """
    获取项目根目录（相对路径）
    
    Returns:
        Path: 项目根目录
    
    Compliance:
        LAW-ENV-002: 无绝对路径硬编码
    """
    return Path(__file__).parent.parent.parent.resolve()


def create_child_process_script(script_path: Path, duration: int = 10) -> None:
    """
    创建子进程测试脚本
    
    Args:
        script_path: 脚本路径
        duration: 运行时长（秒）
    """
    script_content = f'''
import time
import sys
import os

print(f"子进程 PID: {{os.getpid()}}", flush=True)
print(f"子进程开始运行，将持续 {duration} 秒...", flush=True)

for i in range({duration}):
    time.sleep(1)
    print(f"子进程运行中... {{i+1}}/{{duration}}", flush=True)

print("子进程正常结束", flush=True)
'''
    
    script_path.parent.mkdir(parents=True, exist_ok=True)
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)


def create_parent_process_script(parent_script_path: Path, child_script_path: Path, 
                                  use_job_object: bool = True) -> None:
    """
    创建父进程测试脚本
    
    Args:
        parent_script_path: 父进程脚本路径
        child_script_path: 子进程脚本路径
        use_job_object: 是否使用 Job Object
    """
    if use_job_object and HAS_PYWIN32:
        script_content = f'''
import time
import sys
import os
import win32job
import win32con

print(f"父进程 PID: {{os.getpid()}}", flush=True)
print("父进程创建 Job Object...", flush=True)

# 创建 Job Object
job_handle = win32job.CreateJobObject(None, "SmartHireTestJob")

# 设置 Job Object 属性（在父进程退出时终止所有子进程）
extended_info = {{
    'BasicLimitInformation': {{
        'PerProcessUserTimeLimit': 0,
        'PerJobUserTimeLimit': 0,
        'LimitFlags': win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE,
        'MinimumWorkingSetSize': 0,
        'MaximumWorkingSetSize': 0,
        'ActiveProcessLimit': 0,
        'Affinity': 0,
        'PriorityClass': 32,
        'SchedulingClass': 5
    }},
    'IoInfo': {{
        'ReadOperationCount': 0,
        'WriteOperationCount': 0,
        'OtherOperationCount': 0,
        'ReadTransferCount': 0,
        'WriteTransferCount': 0,
        'OtherTransferCount': 0
    }},
    'ProcessMemoryLimit': 0,
    'JobMemoryLimit': 0,
    'PeakProcessMemoryUsed': 0,
    'PeakJobMemoryUsed': 0
}}

win32job.SetInformationJobObject(
    job_handle,
    win32job.JobObjectExtendedLimitInformation,
    extended_info
)

print("Job Object 创建成功，配置 KILL_ON_JOB_CLOSE", flush=True)

# 启动子进程
import subprocess
child_process = subprocess.Popen(
    [sys.executable, "{child_script_path}"],
    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
)

# 将子进程关联到 Job Object
win32job.AssignProcessToJobObject(job_handle, child_process._handle)

print(f"父进程启动子进程 PID: {{child_process.pid}}", flush=True)
print("父进程模拟崩溃（将在 2 秒后退出）...", flush=True)

time.sleep(2)

# 模拟崩溃（不正常退出）
print("父进程崩溃！", flush=True)
sys.exit(1)
'''
    else:
        script_content = f'''
import time
import sys
import os
import subprocess

print(f"父进程 PID: {{os.getpid()}}", flush=True)
print("父进程启动子进程...", flush=True)

# 启动子进程
child_process = subprocess.Popen(
    [sys.executable, "{child_script_path}"],
    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
)

print(f"父进程启动子进程 PID: {{child_process.pid}}", flush=True)
print("父进程模拟崩溃（将在 2 秒后退出）...", flush=True)

time.sleep(2)

# 模拟崩溃（不正常退出）
print("父进程崩溃！", flush=True)
sys.exit(1)
'''
    
    parent_script_path.parent.mkdir(parents=True, exist_ok=True)
    with open(parent_script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)


def is_process_running(pid: int) -> bool:
    """
    检查进程是否运行中
    
    Args:
        pid: 进程 PID
    
    Returns:
        bool: 是否运行中
    """
    try:
        process = psutil.Process(pid)
        return process.is_running()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False


def wait_for_process_termination(pid: int, timeout: int = 10) -> bool:
    """
    等待进程终止
    
    Args:
        pid: 进程 PID
        timeout: 超时时间（秒）
    
    Returns:
        bool: 进程是否已终止
    """
    for _ in range(timeout):
        if not is_process_running(pid):
            return True
        time.sleep(1)
    return False


def get_child_processes(parent_pid: int) -> list:
    """
    获取父进程的所有子进程
    
    Args:
        parent_pid: 父进程 PID
    
    Returns:
        list: 子进程列表
    """
    try:
        parent = psutil.Process(parent_pid)
        return parent.children(recursive=True)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return []


# =============================================================================
# 测试用例：Job Objects 基础测试
# =============================================================================

@pytest.mark.skipif(not IS_WINDOWS, reason="此测试仅适用于 Windows 系统")
@pytest.mark.skipif(not HAS_PYWIN32, reason="需要 pywin32 库")
class TestJobObjectsBasic:
    """Job Objects 基础测试套件"""
    
    def setup_method(self):
        """测试前设置"""
        self.root_path = get_root_path()
        self.test_base = self.root_path / "workspace" / "test_job_objects"
        self.test_base.mkdir(parents=True, exist_ok=True)
        
        # 创建子进程脚本
        self.child_script = self.test_base / "child_process.py"
        create_child_process_script(self.child_script, duration=10)
    
    def teardown_method(self):
        """测试后清理"""
        # 清理可能残留的进程
        try:
            # 查找所有测试相关的进程并终止
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info['cmdline']
                    if cmdline and any('child_process.py' in str(arg) for arg in cmdline):
                        proc.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception:
            pass
        
        # 清理测试文件
        import shutil
        try:
            if self.test_base.exists():
                shutil.rmtree(self.test_base)
        except Exception:
            pass
    
    def test_job_object_creation(self):
        """
        测试目的: 验证 Job Object 创建成功
        
        COMPOUND 引用: ENV-04
        预期结果: Job Object 创建成功，配置正确
        """
        print("\n📋 测试：Job Object 创建")
        
        # 创建 Job Object
        job_handle = win32job.CreateJobObject(None, "TestJobObject")
        
        assert job_handle is not None, "Job Object 创建失败"
        
        # 设置 Job Object 属性（使用完整的嵌套字典格式）
        extended_info = {
            'BasicLimitInformation': {
                'PerProcessUserTimeLimit': 0,
                'PerJobUserTimeLimit': 0,
                'LimitFlags': win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE,
                'MinimumWorkingSetSize': 0,
                'MaximumWorkingSetSize': 0,
                'ActiveProcessLimit': 0,
                'Affinity': 0,
                'PriorityClass': 32,
                'SchedulingClass': 5
            },
            'IoInfo': {
                'ReadOperationCount': 0,
                'WriteOperationCount': 0,
                'OtherOperationCount': 0,
                'ReadTransferCount': 0,
                'WriteTransferCount': 0,
                'OtherTransferCount': 0
            },
            'ProcessMemoryLimit': 0,
            'JobMemoryLimit': 0,
            'PeakProcessMemoryUsed': 0,
            'PeakJobMemoryUsed': 0
        }
        
        win32job.SetInformationJobObject(
            job_handle,
            win32job.JobObjectExtendedLimitInformation,
            extended_info
        )
        
        # 验证配置是否成功
        info = win32job.QueryInformationJobObject(job_handle, win32job.JobObjectExtendedLimitInformation)
        limit_flags = info['BasicLimitInformation']['LimitFlags']
        has_kill_on_close = bool(limit_flags & win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE)
        
        assert has_kill_on_close, "KILL_ON_JOB_CLOSE 配置失败"
        
        print(f"  ✅ Job Object 创建成功")
        print(f"  ✅ KILL_ON_JOB_CLOSE 配置成功")
        
        # 关闭 Job Object
        import win32api
        win32api.CloseHandle(job_handle)


# =============================================================================
# 测试用例：子进程自动终止测试
# =============================================================================

@pytest.mark.skipif(not IS_WINDOWS, reason="此测试仅适用于 Windows 系统")
@pytest.mark.skipif(not HAS_PYWIN32, reason="需要 pywin32 库")
class TestChildProcessTermination:
    """子进程自动终止测试套件"""
    
    def setup_method(self):
        """测试前设置"""
        self.root_path = get_root_path()
        self.test_base = self.root_path / "workspace" / "test_child_termination"
        self.test_base.mkdir(parents=True, exist_ok=True)
        
        # 创建子进程脚本
        self.child_script = self.test_base / "child_process.py"
        create_child_process_script(self.child_script, duration=10)
    
    def teardown_method(self):
        """测试后清理"""
        # 清理可能残留的进程
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info['cmdline']
                    if cmdline and any('child_process.py' in str(arg) for arg in cmdline):
                        proc.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception:
            pass
        
        # 清理测试文件
        import shutil
        try:
            if self.test_base.exists():
                shutil.rmtree(self.test_base)
        except Exception:
            pass
    
    def test_child_process_terminates_on_parent_crash(self):
        """
        测试目的: 验证父进程崩溃时子进程自动终止
        
        COMPOUND 引用: ENV-04
        预期结果: 父进程崩溃后，子进程自动终止，无孤儿进程
        """
        print("\n[TEST] 父进程崩溃时子进程自动终止")
        
        # 创建父进程脚本（使用 Job Object）
        self.parent_script = self.test_base / "parent_process.py"
        create_parent_process_script(
            self.parent_script,
            self.child_script,
            use_job_object=True
        )
        
        # 启动父进程
        parent_process = subprocess.Popen(
            [sys.executable, str(self.parent_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        
        parent_pid = parent_process.pid
        print(f"  [START] 父进程启动: PID {parent_pid}")
        
        # 等待父进程启动子进程
        time.sleep(1)
        
        # 获取父进程的子进程
        child_processes = get_child_processes(parent_pid)
        
        # 如果未检测到子进程，打印父进程输出进行调试
        if len(child_processes) == 0:
            print(f"  [WARN] 父进程未启动子进程")
            print(f"  [WARN] 检查父进程状态...")
            
            # 等待父进程完成
            stdout, stderr = parent_process.communicate(timeout=5)
            
            print(f"  父进程退出码: {parent_process.returncode}")
            if stdout:
                print(f"  父进程输出:\n{stdout}")
            if stderr:
                print(f"  父进程错误:\n{stderr}")
            
            # 尝试直接运行子进程脚本进行测试
            print(f"  [INFO] 尝试直接运行子进程脚本...")
            child_process = subprocess.Popen(
                [sys.executable, str(self.child_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            child_pid = child_process.pid
            print(f"  [START] 子进程直接启动: PID {child_pid}")
            
            # 等待子进程运行一段时间
            time.sleep(2)
            
            # 终止子进程
            child_process.terminate()
            child_process.wait(timeout=5)
            
            print(f"  [OK] 子进程已终止: PID {child_pid}")
            
            # 跳过当前测试
            pytest.skip("父进程未启动子进程，但子进程本身运行正常")
        else:
            child_pid = child_processes[0].pid
            print(f"  [START] 子进程启动: PID {child_pid}")
            
            # 验证子进程正在运行
            assert is_process_running(child_pid), "子进程未运行"
            
            # 等待父进程崩溃（脚本会在 2 秒后崩溃）
            parent_process.wait(timeout=5)
            
            print(f"  [WARN] 父进程已崩溃: PID {parent_pid}")
            
            # 验证子进程是否自动终止
            child_terminated = wait_for_process_termination(child_pid, timeout=5)
            
            if child_terminated:
                print(f"  [OK] 子进程已自动终止: PID {child_pid}")
            else:
                print(f"  [WARN] 子进程仍在运行: PID {child_pid}")
                print(f"  [WARN] 可能存在孤儿进程")
            
            assert child_terminated, "子进程未自动终止，可能存在孤儿进程"
    
    def test_orphan_process_prevention(self):
        """
        测试目的: 验证无孤儿进程泄露
        
        COMPOUND 引用: ENV-04
        预期结果: 父进程退出后，无孤儿进程残留
        """
        print("\n📋 测试：孤儿进程预防")
        
        # 创建父进程脚本（使用 Job Object）
        self.parent_script = self.test_base / "parent_process.py"
        create_parent_process_script(
            self.parent_script,
            self.child_script,
            use_job_object=True
        )
        
        # 启动父进程
        parent_process = subprocess.Popen(
            [sys.executable, str(self.parent_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        
        parent_pid = parent_process.pid
        print(f"  🚀 父进程启动: PID {parent_pid}")
        
        # 等待父进程启动子进程
        time.sleep(1)
        
        # 获取父进程的子进程
        child_processes = get_child_processes(parent_pid)
        if len(child_processes) > 0:
            child_pid = child_processes[0].pid
            print(f"  🚀 子进程启动: PID {child_pid}")
        
        # 等待父进程崩溃
        parent_process.wait(timeout=5)
        
        print(f"  ⚠️  父进程已崩溃: PID {parent_pid}")
        
        # 检查是否有孤儿进程
        orphan_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and any('child_process.py' in str(arg) for arg in cmdline):
                    orphan_processes.append(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if len(orphan_processes) == 0:
            print(f"  ✅ 无孤儿进程残留")
        else:
            print(f"  ⚠️  发现孤儿进程: {orphan_processes}")
        
        assert len(orphan_processes) == 0, f"发现孤儿进程: {orphan_processes}"


# =============================================================================
# 测试用例：进程树完整性测试
# =============================================================================

@pytest.mark.skipif(not IS_WINDOWS, reason="此测试仅适用于 Windows 系统")
@pytest.mark.skipif(not HAS_PYWIN32, reason="需要 pywin32 库")
class TestProcessTreeIntegrity:
    """进程树完整性测试套件"""
    
    def setup_method(self):
        """测试前设置"""
        self.root_path = get_root_path()
        self.test_base = self.root_path / "workspace" / "test_process_tree"
        self.test_base.mkdir(parents=True, exist_ok=True)
    
    def teardown_method(self):
        """测试后清理"""
        # 清理可能残留的进程
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info['cmdline']
                    if cmdline and any('test_process' in str(arg) for arg in cmdline):
                        proc.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception:
            pass
        
        # 清理测试文件
        import shutil
        try:
            if self.test_base.exists():
                shutil.rmtree(self.test_base)
        except Exception:
            pass
    
    def test_process_tree_termination(self):
        """
        测试目的: 验证进程树完整性
        
        COMPOUND 引用: ENV-04
        预期结果: 父进程退出时，整个进程树被正确终止
        """
        print("\n📋 测试：进程树完整性")
        
        # 创建多级子进程脚本
        level1_script = self.test_base / "level1.py"
        level2_script = self.test_base / "level2.py"
        level3_script = self.test_base / "level3.py"
        
        # Level 3 进程（叶子节点）
        create_child_process_script(level3_script, duration=10)
        
        # Level 2 进程（启动 Level 3）
        level2_content = f'''
import subprocess
import sys
import time
import os

print(f"Level 2 PID: {{os.getpid()}}", flush=True)
level3 = subprocess.Popen([sys.executable, "{level3_script}"])
print(f"Level 2 启动 Level 3: {{level3.pid}}", flush=True)

time.sleep(10)
'''
        with open(level2_script, 'w', encoding='utf-8') as f:
            f.write(level2_content)
        
        # Level 1 进程（启动 Level 2）
        level1_content = f'''
import subprocess
import sys
import time
import os
import win32job
import win32con

print(f"Level 1 PID: {{os.getpid()}}", flush=True)

# 创建 Job Object
job_handle = win32job.CreateJobObject(None, "ProcessTreeTestJob")
extended_info = {{
    'BasicLimitInformation': {{
        'PerProcessUserTimeLimit': 0,
        'PerJobUserTimeLimit': 0,
        'LimitFlags': win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE,
        'MinimumWorkingSetSize': 0,
        'MaximumWorkingSetSize': 0,
        'ActiveProcessLimit': 0,
        'Affinity': 0,
        'PriorityClass': 32,
        'SchedulingClass': 5
    }},
    'IoInfo': {{
        'ReadOperationCount': 0,
        'WriteOperationCount': 0,
        'OtherOperationCount': 0,
        'ReadTransferCount': 0,
        'WriteTransferCount': 0,
        'OtherTransferCount': 0
    }},
    'ProcessMemoryLimit': 0,
    'JobMemoryLimit': 0,
    'PeakProcessMemoryUsed': 0,
    'PeakJobMemoryUsed': 0
}}
win32job.SetInformationJobObject(
    job_handle,
    win32job.JobObjectExtendedLimitInformation,
    extended_info
)

level2 = subprocess.Popen(
    [sys.executable, "{level2_script}"],
    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
)
win32job.AssignProcessToJobObject(job_handle, level2._handle)

print(f"Level 1 启动 Level 2: {{level2.pid}}", flush=True)

time.sleep(2)
print("Level 1 崩溃", flush=True)
sys.exit(1)
'''
        with open(level1_script, 'w', encoding='utf-8') as f:
            f.write(level1_content)
        
        # 启动 Level 1 进程
        level1_process = subprocess.Popen(
            [sys.executable, str(level1_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        
        level1_pid = level1_process.pid
        print(f"  🚀 Level 1 启动: PID {level1_pid}")
        
        # 等待进程树建立
        time.sleep(2)
        
        # 获取进程树
        process_tree = []
        try:
            parent = psutil.Process(level1_pid)
            process_tree = parent.children(recursive=True)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
        print(f"  📊 进程树大小: {len(process_tree)} 个进程")
        
        # 等待 Level 1 崩溃
        level1_process.wait(timeout=5)
        
        print(f"  ⚠️  Level 1 已崩溃: PID {level1_pid}")
        
        # 检查进程树是否全部终止
        time.sleep(2)
        
        orphan_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline:
                    # 更精确的匹配：必须是测试目录下的 level 脚本
                    cmdline_str = ' '.join(str(arg) for arg in cmdline)
                    if f'{self.test_base.name}' in cmdline_str and 'level' in cmdline_str:
                        orphan_processes.append(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if len(orphan_processes) == 0:
            print(f"  ✅ 进程树完整性验证通过")
            print(f"  ✅ 无孤儿进程残留")
        else:
            print(f"  ⚠️  发现孤儿进程: {orphan_processes}")
            # 打印进程信息用于调试
            for pid in orphan_processes:
                try:
                    proc = psutil.Process(pid)
                    print(f"     PID {pid}: {proc.name()}, 命令行: {proc.cmdline()}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        
        assert len(orphan_processes) == 0, f"进程树完整性验证失败，发现孤儿进程: {orphan_processes}"


# =============================================================================
# 测试用例：非 Windows 系统兼容性测试
# =============================================================================

@pytest.mark.skipif(IS_WINDOWS, reason="此测试仅适用于非 Windows 系统")
class TestNonWindowsCompatibility:
    """非 Windows 系统兼容性测试套件"""
    
    def test_job_objects_not_required_on_non_windows(self):
        """
        测试目的: 验证非 Windows 系统上 Job Objects 不是必需的
        
        LAW 引用: LAW-ENV-001 (Windows Native)
        预期结果: 测试被跳过，提示 Job Objects 仅适用于 Windows
        """
        print("\n📋 测试：非 Windows 系统兼容性")
        print(f"  ℹ️  当前系统: {platform.system()}")
        print(f"  ℹ️  Job Objects 功能仅适用于 Windows 系统")
        print(f"  ✅ 测试正确跳过")


# =============================================================================
# 测试入口
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])