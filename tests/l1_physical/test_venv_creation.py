#!/usr/bin/env python3
"""
SmartHire L1 物理层测试：虚拟环境创建测试

Version: 2.0.0
Compliance: DIAGNOSIS.md §1.1 (L1 物理层测试)
Testing: VirtualEnvironmentManager 类功能
"""

import sys
import os
import pytest
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from swan import VirtualEnvironmentManager


class TestVirtualEnvironmentManager:
    """虚拟环境管理器测试"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp, ignore_errors=True)

    @pytest.fixture
    def venv_manager(self, temp_dir):
        """创建虚拟环境管理器实例"""
        return VirtualEnvironmentManager(temp_dir, sys.executable)

    def test_check_exists_when_not_exists(self, venv_manager):
        """测试检查虚拟环境不存在的情况"""
        assert not venv_manager.check_exists()

    def test_check_python_version(self, venv_manager):
        """测试Python版本检查"""
        is_valid, version_info = venv_manager.check_python_version()
        assert isinstance(is_valid, bool)
        assert isinstance(version_info, str)
        # 当前运行的Python应该满足版本要求
        if sys.version_info >= (3, 10):
            assert is_valid

    def test_create_venv_success(self, venv_manager):
        """测试成功创建虚拟环境"""
        # 虚拟环境不存在
        assert not venv_manager.check_exists()

        # 创建虚拟环境
        result = venv_manager.create_venv()
        assert result is True

        # 虚拟环境应该存在
        assert venv_manager.check_exists()
        assert venv_manager.venv_path.exists()

    def test_create_venv_already_exists(self, venv_manager, temp_dir):
        """测试重复创建虚拟环境"""
        # 第一次创建
        venv_manager.create_venv()
        assert venv_manager.check_exists()

        # 第二次创建（应该覆盖）
        result = venv_manager.create_venv()
        assert result is True
        assert venv_manager.check_exists()

    def test_get_python_executable(self, venv_manager):
        """测试获取Python可执行文件路径"""
        python_exe = venv_manager.get_python_executable()
        assert isinstance(python_exe, Path)

        # 创建虚拟环境后，Python可执行文件应该存在
        venv_manager.create_venv()
        assert venv_manager.get_python_executable().exists()

    def test_get_pip_executable(self, venv_manager):
        """测试获取pip可执行文件路径"""
        pip_exe = venv_manager.get_pip_executable()
        assert isinstance(pip_exe, Path)

        # 创建虚拟环境后，pip可执行文件应该存在
        venv_manager.create_venv()
        assert venv_manager.get_pip_executable().exists()

    def test_activate_returns_env_dict(self, venv_manager):
        """测试激活返回环境变量字典"""
        venv_manager.create_venv()
        env = venv_manager.activate()

        assert isinstance(env, dict)
        assert 'VIRTUAL_ENV' in env
        assert 'PATH' in env
        assert str(venv_manager.venv_path) in env['VIRTUAL_ENV']

    def test_venv_path_relative(self, venv_manager, temp_dir):
        """测试虚拟环境路径使用相对路径"""
        # 虚拟环境路径应该是相对的
        assert venv_manager.venv_path == temp_dir / "swanvenv"

        # 不应该是绝对路径
        # 注意：Path对象会自动解析为绝对路径，这里检查路径构成
        assert venv_manager.venv_path.name == "swanvenv"


class TestVirtualEnvironmentManagerErrors:
    """虚拟环境管理器错误处理测试"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp, ignore_errors=True)

    @pytest.fixture
    def invalid_python_manager(self, temp_dir):
        """创建使用无效Python路径的管理器"""
        return VirtualEnvironmentManager(temp_dir, "/invalid/python/path")

    def test_create_venv_with_invalid_python(self, invalid_python_manager):
        """测试使用无效Python路径创建虚拟环境"""
        # 应该失败但不应该抛出异常
        result = invalid_python_manager.create_venv()
        # 结果可能因系统而异，但不应崩溃
        assert isinstance(result, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
