#!/usr/bin/env python3
"""
SmartHire L1 物理层测试：进程清理测试

Version: 2.0.0
Compliance: DIAGNOSIS.md §1.1 (L1 物理层测试)
Testing: ProcessCleaner 类功能
"""

import sys
import os
import pytest
import subprocess
import time
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from swan import ProcessCleaner


class TestProcessCleaner:
    """进程清理器测试"""

    @pytest.fixture
    def process_cleaner(self):
        """创建进程清理器实例"""
        return ProcessCleaner()

    def test_init(self, process_cleaner):
        """测试初始化"""
        assert process_cleaner is not None
        assert hasattr(process_cleaner, 'process_name')
        assert hasattr(process_cleaner, 'keywords')

    def test_find_processes_returns_list(self, process_cleaner):
        """测试查找进程返回列表"""
        processes = process_cleaner.find_processes()
        assert isinstance(processes, list)

    def test_find_processes_empty(self, process_cleaner):
        """测试在没有SmartHire进程时查找"""
        processes = process_cleaner.find_processes()
        # 应该返回空列表或只包含测试进程
        assert isinstance(processes, list)

    def test_cleanup_returns_tuple(self, process_cleaner):
        """测试cleanup返回正确的数据类型"""
        success_count, fail_count = process_cleaner.cleanup()

        assert isinstance(success_count, int)
        assert isinstance(fail_count, int)
        assert success_count >= 0
        assert fail_count >= 0

    def test_kill_processes_with_empty_list(self, process_cleaner):
        """测试终止空进程列表"""
        success_count, fail_count = process_cleaner.kill_processes([])

        assert success_count == 0
        assert fail_count == 0


class TestProcessCleanerWithMockProcess:
    """进程清理器测试（使用模拟进程）"""

    @pytest.fixture
    def process_cleaner(self):
        """创建进程清理器实例"""
        return ProcessCleaner()

    @pytest.fixture
    def mock_python_process(self):
        """创建一个模拟的Python进程"""
        # 创建一个长时间运行的Python进程
        proc = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(10)"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        yield proc
        # 清理：确保进程被终止
        try:
            proc.terminate()
            proc.wait(timeout=2)
        except Exception:
            proc.kill()

    def test_process_lifecycle(self, mock_python_process):
        """测试进程生命周期"""
        # 进程应该正在运行
        assert mock_python_process.poll() is None

    def test_find_python_processes(self, process_cleaner):
        """测试查找Python进程"""
        # 注意：这个测试可能会找到系统中所有的Python进程
        # 包括当前测试进程本身
        processes = process_cleaner.find_processes()

        # 至少应该找到当前测试进程（如果包含"swan"或"smarthire"关键词）
        # 或者返回空列表
        assert isinstance(processes, list)


class TestProcessCleanerErrorHandling:
    """进程清理器错误处理测试"""

    @pytest.fixture
    def process_cleaner(self):
        """创建进程清理器实例"""
        return ProcessCleaner()

    def test_kill_processes_with_invalid_pids(self, process_cleaner):
        """测试终止无效PID"""
        # 创建一个模拟的进程对象（实际上不存在）
        class MockProcess:
            def __init__(self):
                self.pid = 999999  # 不存在的PID
                self.name = "python"

            def terminate(self):
                raise Exception("No such process")

            def kill(self):
                raise Exception("No such process")

        mock_proc = MockProcess()

        # 应该捕获异常并继续
        success_count, fail_count = process_cleaner.kill_processes([mock_proc])

        assert success_count == 0
        assert fail_count == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
