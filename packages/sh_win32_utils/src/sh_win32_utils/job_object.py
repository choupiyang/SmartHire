# SmartHire Win32 Job Object - 进程生命周期管理
# Version: 1.0.0
# Compliance: ARCH v2.0 | LAW v5.0 | MAP v7.0 | COMPOUND.md v3.0 | DIAGNOSIS.md v3.0

"""
Win32 Job Object - 进程生命周期管理
=====================================

本模块实现 Windows Job Object API，用于进程组的生命周期管理：
- 创建 Job Object
- 将进程加入 Job Object
- 设置资源限制（CPU、内存等）
- 终止 Job Object（优雅关闭）

P0-1 修订：初始计划缺失的 Win32 Job Objects 实现
"""

import ctypes
import logging
import subprocess
import time
from typing import List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Windows API 常量
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x2000
JOB_OBJECT_LIMIT_DIE_ON_UNHANDLED_EXCEPTION = 0x400
JOB_OBJECT_LIMIT_BREAKAWAY_OK = 0x800
JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK = 0x1000

JOBOBJECT_BASIC_LIMIT_INFORMATION = 2

class JOBOBJECT_BASIC_LIMIT_INFORMATION_CLASS(ctypes.Structure):
    """
    Job Object 基本限制信息结构
    """
    _fields_ = [
        ("PerProcessUserTimeLimit", ctypes.c_int64),
        ("PerJobUserTimeLimit", ctypes.c_int64),
        ("LimitFlags", ctypes.c_ulong),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", ctypes.c_ulong),
        ("Affinity", ctypes.c_size_t),
        ("PriorityClass", ctypes.c_ulong),
        ("SchedulingClass", ctypes.c_ulong)
    ]


@dataclass
class ProcessInfo:
    """进程信息"""
    pid: int
    name: str
    start_time: float


class Win32JobObject:
    """
    Win32 Job Object - 进程生命周期管理
    
    P0-1 修订：初始计划缺失的 Win32 Job Objects 实现
    
    本类提供进程组的生命周期管理功能：
    - 创建 Job Object
    - 将进程加入 Job Object
    - 设置资源限制
    - 终止 Job Object（优雅关闭）
    
    Example:
        >>> from sh_win32_utils import Win32JobObject
        >>> job = Win32JobObject("SmartHire-Job")
        >>> proc = subprocess.Popen(["python", "script.py"])
        >>> job.add_process(proc)
        >>> # ... work ...
        >>> job.terminate()
    """
    
    def __init__(self, job_name: str, kill_on_close: bool = True) -> None:
        """
        初始化 Win32 Job Object
        
        Args:
            job_name: Job Object 名称
            kill_on_close: 关闭时是否终止所有进程
        """
        self.job_name: str = job_name
        self.kill_on_close: bool = kill_on_close
        self.handle: Optional[ctypes.HANDLE] = None
        self.processes: List[ProcessInfo] = []
        
        # 加载 Windows API
        self.kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        
        # 设置函数原型
        self.kernel32.CreateJobObjectW.restype = ctypes.HANDLE
        self.kernel32.CreateJobObjectW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p]
        
        self.kernel32.AssignProcessToJobObject.restype = ctypes.c_bool
        self.kernel32.AssignProcessToJobObject.argtypes = [ctypes.HANDLE, ctypes.HANDLE]
        
        self.kernel32.CloseHandle.restype = ctypes.c_bool
        self.kernel32.CloseHandle.argtypes = [ctypes.HANDLE]
        
        self.kernel32.TerminateJobObject.restype = ctypes.c_bool
        self.kernel32.TerminateJobObject.argtypes = [ctypes.HANDLE, ctypes.c_uint]
        
        self.kernel32.SetInformationJobObject.restype = ctypes.c_bool
        self.kernel32.SetInformationJobObject.argtypes = [
            ctypes.HANDLE,
            ctypes.c_int,
            ctypes.c_void_p,
            ctypes.c_uint
        ]
        
        # 创建 Job Object
        self.handle = self.kernel32.CreateJobObjectW(None, job_name)
        if not self.handle:
            error_code = ctypes.get_last_error()
            raise RuntimeError(f"无法创建 Job Object: 错误代码 {error_code}")
        
        # 设置关闭时终止所有进程
        if kill_on_close:
            self._set_kill_on_close()
    
    def _set_kill_on_close(self) -> None:
        """
        设置 Job Object 关闭时终止所有进程
        
        Raises:
            RuntimeError: 如果设置失败
        """
        limit_info = JOBOBJECT_BASIC_LIMIT_INFORMATION_CLASS()
        limit_info.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        
        result = self.kernel32.SetInformationJobObject(
            self.handle,
            JOBOBJECT_BASIC_LIMIT_INFORMATION,
            ctypes.byref(limit_info),
            ctypes.sizeof(limit_info)
        )
        
        if not result:
            error_code = ctypes.get_last_error()
            raise RuntimeError(f"无法设置 Job Object 限制: 错误代码 {error_code}")
    
    def add_process(self, process: subprocess.Popen) -> bool:
        """
        将进程加入 Job Object
        
        Args:
            process: 进程对象（subprocess.Popen）
            
        Returns:
            bool: 是否成功加入
            
        Example:
            >>> proc = subprocess.Popen(["python", "script.py"])
            >>> job.add_process(proc)
        """
        if not process or not process.pid:
            return False
        
        try:
            process_handle = ctypes.windll.kernel32.OpenProcess(
                0x1F0FFF,  # PROCESS_ALL_ACCESS
                False,
                process.pid
            )
            
            if not process_handle:
                return False
            
            result = self.kernel32.AssignProcessToJobObject(
                self.handle,
                process_handle
            )
            
            self.kernel32.CloseHandle(process_handle)
            
            if result:
                # 记录进程信息
                try:
                    name = process.args[0] if process.args else "unknown"
                except Exception as e:
                    logger.debug(f"[job_object] 获取进程名称失败: {e}")
                    name = "unknown"
                
                self.processes.append(ProcessInfo(
                    pid=process.pid,
                    name=name,
                    start_time=time.time()
                ))
            
            return result
            
        except Exception as e:
            return False
    
    def terminate(self, exit_code: int = 1) -> bool:
        """
        终止 Job Object（优雅关闭所有进程）
        
        Args:
            exit_code: 退出代码
            
        Returns:
            bool: 是否成功终止
            
        Example:
            >>> job.terminate()
        """
        if not self.handle:
            return False
        
        result = self.kernel32.TerminateJobObject(
            self.handle,
            exit_code
        )
        
        # 清空进程列表
        self.processes.clear()
        
        return result
    
    def close(self) -> None:
        """
        关闭 Job Object 句柄
        
        如果设置了 kill_on_close，所有进程将被终止。
        """
        if self.handle:
            self.kernel32.CloseHandle(self.handle)
            self.handle = None
            self.processes.clear()
    
    def get_process_count(self) -> int:
        """
        获取 Job Object 中的进程数量
        
        Returns:
            int: 进程数量
        """
        return len(self.processes)
    
    def __enter__(self):
        """上下文管理器支持"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器支持"""
        self.close()
        return False
    
    def __del__(self):
        """析构函数"""
        self.close()


__all__ = ['Win32JobObject', 'ProcessInfo']