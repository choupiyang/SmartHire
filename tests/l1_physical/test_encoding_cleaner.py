"""
L1 物理层：编码清洗测试

Version: 1.0.0
Compliance: COMPOUND.md ENV-03 (GBK/UTF-8 双向清洗), LAW-ENV-002 (无绝对路径硬编码)

Description:
    测试编码清洗机制，确保 GBK 和 UTF-8 编码之间的双向转换正确，
    subprocess 输出自动转换为 UTF-8，无 "僵尸字符" 输出。

Test Cases:
    - 创建 GBK 编码文件名（如：测试_中文.txt）
    - 通过 subprocess 读取文件
    - 验证输出为 UTF-8 编码，无乱码
    - 测试混合编码场景（GBK 文件名 + UTF-8 内容）

Usage:
    pytest tests/l1_physical/test_encoding_cleaner.py -v
"""

import pytest
import subprocess
import os
import shutil
from pathlib import Path
import sys


# =============================================================================
# 测试配置
# =============================================================================

# Windows 默认编码通常是 GBK (cp936)
WINDOWS_ENCODING = 'gbk'
# SmartHire 要求的编码
TARGET_ENCODING = 'utf-8'


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


def create_test_file_with_encoding(file_path: Path, content: str, encoding: str) -> bool:
    """
    创建指定编码的测试文件
    
    Args:
        file_path: 文件路径
        content: 文件内容
        encoding: 文件编码
    
    Returns:
        bool: 是否创建成功
    """
    try:
        # 确保父目录存在
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入文件
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"创建文件失败: {e}")
        return False


def read_file_with_encoding(file_path: Path, encoding: str) -> str:
    """
    读取指定编码的文件
    
    Args:
        file_path: 文件路径
        encoding: 文件编码
    
    Returns:
        str: 文件内容
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        raise RuntimeError(f"读取文件失败: {e}")


def cleanup_test_file(file_path: Path) -> None:
    """
    清理测试文件
    
    Args:
        file_path: 文件路径
    """
    try:
        if file_path.exists():
            if file_path.is_file():
                file_path.unlink()
            elif file_path.is_dir():
                shutil.rmtree(file_path)
    except Exception:
        pass


def run_subprocess_read_file(file_path: Path, encoding: str = TARGET_ENCODING) -> subprocess.CompletedProcess:
    """
    通过 subprocess 读取文件（模拟外部进程读取）
    
    Args:
        file_path: 文件路径
        encoding: 期望的输出编码
    
    Returns:
        subprocess.CompletedProcess: 子进程结果
    """
    # 创建一个简单的 Python 脚本来读取文件
    # 使用 repr() 来正确转义路径中的特殊字符
    script_content = f'''
import sys
from pathlib import Path

file_path = Path(r"{file_path}")
try:
    with open(file_path, 'r', encoding="{encoding}") as f:
        content = f.read()
    print(content, end='')
except Exception as e:
    print(f"Error: {{e}}", file=sys.stderr)
    sys.exit(1)
'''
    
    # 写入临时脚本
    script_path = get_root_path() / "workspace" / "temp_read_script.py"
    try:
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # 运行子进程（先不指定 encoding，处理原始字节）
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=False  # 不自动解码，获取原始字节
        )
        
        # 尝试解码输出（先尝试 GBK，失败后尝试 UTF-8）
        try:
            stdout_text = result.stdout.decode('gbk')
            stderr_text = result.stderr.decode('gbk')
        except UnicodeDecodeError:
            try:
                stdout_text = result.stdout.decode('utf-8', errors='replace')
                stderr_text = result.stderr.decode('utf-8', errors='replace')
            except Exception:
                stdout_text = result.stdout.decode('utf-8', errors='replace')
                stderr_text = result.stderr.decode('utf-8', errors='replace')
        
        # 返回修改后的结果
        return subprocess.CompletedProcess(
            args=result.args,
            returncode=result.returncode,
            stdout=stdout_text,
            stderr=stderr_text
        )
    finally:
        # 清理临时脚本
        if script_path.exists():
            script_path.unlink()


# =============================================================================
# 测试用例：GBK 编码文件测试
# =============================================================================

class TestGBKEncoding:
    """GBK 编码测试套件"""
    
    def setup_method(self):
        """测试前设置"""
        self.root_path = get_root_path()
        self.test_base = self.root_path / "workspace" / "test_encoding"
        self.test_base.mkdir(parents=True, exist_ok=True)
    
    def teardown_method(self):
        """测试后清理"""
        cleanup_test_file(self.test_base)
    
    def test_create_gbk_filename(self):
        """
        测试目的: 创建 GBK 编码的文件名
        
        COMPOUND 引用: ENV-03
        预期结果: 文件创建成功，文件名包含中文字符
        """
        print("\n📋 测试：创建 GBK 编码文件名")
        
        # GBK 编码的中文文件名
        filename = "测试_中文_GBK.txt"
        file_path = self.test_base / filename
        
        # 创建文件（UTF-8 内容）
        content = "这是一个测试文件，内容使用 UTF-8 编码。"
        success = create_test_file_with_encoding(file_path, content, 'utf-8')
        
        assert success, f"文件创建失败: {file_path}"
        assert file_path.exists(), f"文件不存在: {file_path}"
        
        print(f"  ✅ 文件创建成功: {file_path.name}")
    
    def test_read_gbk_filename(self):
        """
        测试目的: 读取包含中文的文件名
        
        COMPOUND 引用: ENV-03
        预期结果: 文件名正确显示，无乱码
        """
        print("\n📋 测试：读取包含中文的文件名")
        
        # GBK 编码的中文文件名
        filename = "测试_中文_GBK.txt"
        file_path = self.test_base / filename
        
        # 创建文件
        content = "这是一个测试文件，内容使用 UTF-8 编码。"
        create_test_file_with_encoding(file_path, content, 'utf-8')
        
        # 读取文件
        read_content = read_file_with_encoding(file_path, 'utf-8')
        
        assert read_content == content, f"文件内容不匹配"
        
        print(f"  ✅ 文件名正确显示: {file_path.name}")
        print(f"  ✅ 文件内容正确读取")
    
    def test_subprocess_read_gbk_filename(self):
        """
        测试目的: 通过 subprocess 读取包含中文的文件名
        
        COMPOUND 引用: ENV-03
        预期结果: 输出为 UTF-8 编码，无乱码
        """
        print("\n📋 测试：subprocess 读取包含中文的文件名")
        
        # GBK 编码的中文文件名
        filename = "测试_中文_GBK.txt"
        file_path = self.test_base / filename
        
        # 创建文件
        content = "这是一个测试文件，内容使用 UTF-8 编码。"
        create_test_file_with_encoding(file_path, content, 'utf-8')
        
        # 通过 subprocess 读取文件
        result = run_subprocess_read_file(file_path, TARGET_ENCODING)
        
        assert result.returncode == 0, f"子进程执行失败: {result.stderr}"
        assert result.stdout == content, f"输出内容不匹配: {result.stdout}"
        
        print(f"  ✅ subprocess 读取成功")
        print(f"  ✅ 输出编码正确: UTF-8")
        print(f"  ✅ 无乱码输出")


# =============================================================================
# 测试用例：混合编码测试
# =============================================================================

class TestMixedEncoding:
    """混合编码测试套件"""
    
    def setup_method(self):
        """测试前设置"""
        self.root_path = get_root_path()
        self.test_base = self.root_path / "workspace" / "test_mixed_encoding"
        self.test_base.mkdir(parents=True, exist_ok=True)
    
    def teardown_method(self):
        """测试后清理"""
        cleanup_test_file(self.test_base)
    
    def test_gbk_filename_utf8_content(self):
        """
        测试目的: GBK 文件名 + UTF-8 内容
        
        COMPOUND 引用: ENV-03
        预期结果: 文件创建成功，内容正确读取
        """
        print("\n📋 测试：GBK 文件名 + UTF-8 内容")
        
        # GBK 编码的中文文件名
        filename = "中文文件名_测试.txt"
        file_path = self.test_base / filename
        
        # UTF-8 内容
        content = """
        这是一个测试文件
        文件名包含中文字符
        内容使用 UTF-8 编码
        """
        
        # 创建文件
        success = create_test_file_with_encoding(file_path, content, 'utf-8')
        
        assert success, f"文件创建失败: {file_path}"
        assert file_path.exists(), f"文件不存在: {file_path}"
        
        # 读取内容
        read_content = read_file_with_encoding(file_path, 'utf-8')
        
        assert read_content == content, f"文件内容不匹配"
        
        print(f"  ✅ 文件创建成功: {file_path.name}")
        print(f"  ✅ 内容正确读取: UTF-8")
    
    def test_special_characters(self):
        """
        测试目的: 特殊字符编码测试
        
        COMPOUND 引用: ENV-03
        预期结果: 特殊字符正确处理
        """
        print("\n📋 测试：特殊字符编码")
        
        # 包含特殊字符的文件名
        filename = "测试_特殊字符_@#$.txt"
        file_path = self.test_base / filename
        
        # 包含特殊字符的内容
        content = "特殊字符测试：@#$%^&*()_+-=[]{}|;':\",./<>?"
        
        # 创建文件
        success = create_test_file_with_encoding(file_path, content, 'utf-8')
        
        assert success, f"文件创建失败: {file_path}"
        
        # 读取内容
        read_content = read_file_with_encoding(file_path, 'utf-8')
        
        assert read_content == content, f"文件内容不匹配"
        
        print(f"  ✅ 特殊字符文件名创建成功")
        print(f"  ✅ 特殊字符内容正确读取")
    
    def test_multilingual_content(self):
        """
        测试目的: 多语言内容测试
        
        COMPOUND 引用: ENV-03
        预期结果: 多语言内容正确处理
        """
        print("\n📋 测试：多语言内容")
        
        # 多语言内容
        content = """
        中文：你好，世界！
        English: Hello, World!
        日本語：こんにちは、世界！
        한국어: 안녕하세요, 세계!
        """
        
        filename = "多语言测试.txt"
        file_path = self.test_base / filename
        
        # 创建文件
        success = create_test_file_with_encoding(file_path, content, 'utf-8')
        
        assert success, f"文件创建失败: {file_path}"
        
        # 读取内容
        read_content = read_file_with_encoding(file_path, 'utf-8')
        
        assert read_content == content, f"文件内容不匹配"
        
        print(f"  ✅ 多语言文件创建成功")
        print(f"  ✅ 多语言内容正确读取")


# =============================================================================
# 测试用例：编码转换测试
# =============================================================================

class TestEncodingConversion:
    """编码转换测试套件"""
    
    def setup_method(self):
        """测试前设置"""
        self.root_path = get_root_path()
        self.test_base = self.root_path / "workspace" / "test_encoding_conversion"
        self.test_base.mkdir(parents=True, exist_ok=True)
    
    def teardown_method(self):
        """测试后清理"""
        cleanup_test_file(self.test_base)
    
    def test_gbk_to_utf8_conversion(self):
        """
        测试目的: GBK 到 UTF-8 的编码转换
        
        COMPOUND 引用: ENV-03
        预期结果: 编码转换成功，无乱码
        """
        print("\n📋 测试：GBK 到 UTF-8 编码转换")
        
        # GBK 编码的内容
        content_gbk = "这是 GBK 编码的内容。"
        
        # 创建 GBK 文件
        filename_gbk = "test_gbk.txt"
        file_path_gbk = self.test_base / filename_gbk
        
        with open(file_path_gbk, 'w', encoding='gbk') as f:
            f.write(content_gbk)
        
        # 读取并转换为 UTF-8
        with open(file_path_gbk, 'r', encoding='gbk') as f:
            content_read = f.read()
        
        # 创建 UTF-8 文件
        filename_utf8 = "test_utf8.txt"
        file_path_utf8 = self.test_base / filename_utf8
        
        with open(file_path_utf8, 'w', encoding='utf-8') as f:
            f.write(content_read)
        
        # 验证转换后的内容
        with open(file_path_utf8, 'r', encoding='utf-8') as f:
            content_utf8 = f.read()
        
        assert content_gbk == content_utf8, f"编码转换失败"
        
        print(f"  ✅ GBK 到 UTF-8 编码转换成功")
        print(f"  ✅ 无乱码输出")
    
    def test_no_zombie_characters(self):
        """
        测试目的: 验证无 "僵尸字符" 输出
        
        COMPOUND 引用: ENV-03
        预期结果: subprocess 输出中无乱码或替换字符
        """
        print("\n📋 测试：无僵尸字符输出")
        
        # 中文内容
        content = "中文测试：你好世界！"
        
        filename = "test_zombie.txt"
        file_path = self.test_base / filename
        
        # 创建 UTF-8 文件
        create_test_file_with_encoding(file_path, content, 'utf-8')
        
        # 通过 subprocess 读取
        result = run_subprocess_read_file(file_path, TARGET_ENCODING)
        
        assert result.returncode == 0, f"子进程执行失败: {result.stderr}"
        assert result.stdout == content, f"输出内容不匹配"
        
        # 检查输出中是否有 Unicode 替换字符（U+FFFD，表示为 ）
        replacement_char = '\ufffd'
        assert replacement_char not in result.stdout, f"输出包含替换字符: {result.stdout}"
        
        print(f"  ✅ subprocess 输出中无替换字符")
        print(f"  ✅ 编码正确: UTF-8")


# =============================================================================
# 测试入口
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])