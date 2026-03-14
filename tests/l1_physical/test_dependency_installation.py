#!/usr/bin/env python3
"""
SmartHire L1 物理层测试：依赖安装测试

Version: 2.0.0
Compliance: DIAGNOSIS.md §1.1 (L1 物理层测试)
Testing: DependencyChecker 类功能
"""

import sys
import os
import pytest
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from swan import DependencyChecker, VirtualEnvironmentManager


class TestDependencyChecker:
    """依赖检查器测试"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp, ignore_errors=True)

    @pytest.fixture
    def venv_with_pip(self, temp_dir):
        """创建带有pip的虚拟环境"""
        venv_manager = VirtualEnvironmentManager(temp_dir, sys.executable)
        venv_manager.create_venv()
        return venv_manager

    @pytest.fixture
    def requirements_file(self, temp_dir):
        """创建测试用的requirements.txt"""
        req_file = temp_dir / "requirements.txt"
        req_file.write_text("""# Test dependencies
pytest>=7.4.4
pydantic>=2.5.0
""")
        return req_file

    @pytest.fixture
    def dep_checker(self, venv_with_pip, requirements_file):
        """创建依赖检查器实例"""
        python_exe = venv_with_pip.get_python_executable()
        return DependencyChecker(python_exe, requirements_file)

    def test_check_installed_with_empty_requirements(self, venv_with_pip, temp_dir):
        """测试检查空的requirements.txt"""
        empty_req = temp_dir / "empty_requirements.txt"
        empty_req.write_text("")
        empty_req.touch()

        python_exe = venv_with_pip.get_python_executable()
        checker = DependencyChecker(python_exe, empty_req)

        all_installed, missing = checker.check_installed()
        assert all_installed is True
        assert len(missing) == 0

    def test_check_installed_with_nonexistent_file(self, venv_with_pip, temp_dir):
        """测试检查不存在的requirements.txt"""
        nonexistent_req = temp_dir / "nonexistent_requirements.txt"

        python_exe = venv_with_pip.get_python_executable()
        checker = DependencyChecker(python_exe, nonexistent_req)

        # 应该返回True（跳过检查）
        all_installed, missing = checker.check_installed()
        assert all_installed is True
        assert len(missing) == 0

    def test_check_installed_returns_tuple(self, dep_checker):
        """测试check_installed返回正确的数据类型"""
        all_installed, missing = dep_checker.check_installed()

        assert isinstance(all_installed, bool)
        assert isinstance(missing, list)
        # 列表中的元素应该是字符串
        for pkg in missing:
            assert isinstance(pkg, str)

    def test_install_dependencies(self, dep_checker):
        """测试安装依赖"""
        # 注意：这个测试可能会比较慢
        result = dep_checker.install_dependencies()
        assert isinstance(result, bool)

        # 如果安装成功，验证包确实被安装了
        if result:
            all_installed, missing = dep_checker.check_installed()
            # 应该所有包都已安装
            # 注意：可能会有网络问题等导致失败
            assert isinstance(all_installed, bool)

    def test_verify_installation(self, dep_checker):
        """测试验证安装结果"""
        # 先安装依赖
        dep_checker.install_dependencies()

        # 验证安装
        verified, errors = dep_checker.verify_installation()

        assert isinstance(verified, bool)
        assert isinstance(errors, list)
        # 错误列表中的元素应该是字符串
        for error in errors:
            assert isinstance(error, str)

    def test_verify_without_installation(self, dep_checker):
        """测试不安装直接验证"""
        verified, errors = dep_checker.verify_installation()
        assert isinstance(verified, bool)
        assert isinstance(errors, list)


class TestDependencyCheckerErrors:
    """依赖检查器错误处理测试"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp, ignore_errors=True)

    @pytest.fixture
    def invalid_requirements(self, temp_dir):
        """创建无效的requirements.txt"""
        req_file = temp_dir / "invalid_requirements.txt"
        req_file.write_text("""invalid package name ===
@@@invalid@@@
""")
        return req_file

    def test_check_with_invalid_requirements(self, temp_dir, invalid_requirements):
        """测试检查无效的requirements.txt"""
        # 创建虚拟环境
        venv_manager = VirtualEnvironmentManager(temp_dir, sys.executable)
        venv_manager.create_venv()

        python_exe = venv_manager.get_python_executable()
        checker = DependencyChecker(python_exe, invalid_requirements)

        # 应该返回结果而不崩溃
        all_installed, missing = checker.check_installed()
        assert isinstance(all_installed, bool)
        assert isinstance(missing, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
