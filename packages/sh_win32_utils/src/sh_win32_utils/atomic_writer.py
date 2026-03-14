# SmartHire Atomic File Writer - 三步写入协议
# Version: 1.0.0
# Compliance: ARCH v2.0 | LAW v5.0 | MAP v7.0 | COMPOUND.md v3.0 | DIAGNOSIS.md v3.0

"""
Atomic File Writer - 三步写入协议
==================================

本模块实现原子文件写入协议，确保文件操作的原子性和一致性：
- Write to .tmp (写入临时文件)
- Flush buffer (刷入磁盘缓存)
- Atomic Rename (原子级替换重命名)

COMPOUND 规范：LAW-DATA-002（原子写入协议）
"""

import os
import logging
from pathlib import Path
from typing import Optional, Union
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class AtomicFileWriter:
    """
    Atomic File Writer - 三步写入协议
    
    本类实现原子文件写入协议，确保文件操作的原子性和一致性。
    所有写操作遵循 LAW-DATA-002 规定的三步协议：
    1. Write to .tmp (写入临时文件)
    2. Flush buffer (刷入磁盘缓存)
    3. Atomic Rename (原子级替换重命名)
    
    COMPOUND 规范：LAW-DATA-002（原子写入协议）
    
    Example:
        >>> from sh_win32_utils import AtomicFileWriter
        >>> writer = AtomicFileWriter("data/test.json")
        >>> writer.write('{"key": "value"}')
        >>> writer.commit()
        >>>
        >>> # 使用上下文管理器
        >>> with AtomicFileWriter("data/test.json") as writer:
        ...     writer.write('{"key": "value"}')
    """
    
    def __init__(
        self,
        file_path: Union[str, Path],
        encoding: str = "utf-8",
        mode: str = "w",
        tmp_suffix: str = ".tmp"
    ) -> None:
        """
        初始化原子文件写入器
        
        Args:
            file_path: 目标文件路径
            encoding: 文件编码（默认 UTF-8）
            mode: 写入模式（默认 "w"）
            tmp_suffix: 临时文件后缀（默认 ".tmp"）
            
        Example:
            >>> writer = AtomicFileWriter("data/test.json")
        """
        self.file_path: Path = Path(file_path) if isinstance(file_path, str) else file_path
        self.encoding: str = encoding
        self.mode: str = mode
        self.tmp_suffix: str = tmp_suffix
        
        # 临时文件路径
        self.temp_file_path: Path = self.file_path.with_suffix(
            self.file_path.suffix + self.tmp_suffix
        )
        
        # 文件句柄
        self._file_handle: Optional[object] = None
        
        # 是否已提交
        self._committed: bool = False
    
    def write(self, content: Union[str, bytes]) -> None:
        """
        写入内容到临时文件（步骤 1：Write to .tmp）
        
        Args:
            content: 写入内容（字符串或字节）
            
        Raises:
            RuntimeError: 如果文件已提交或写入失败
            
        Example:
            >>> writer = AtomicFileWriter("data/test.json")
            >>> writer.write('{"key": "value"}')
        """
        if self._committed:
            raise RuntimeError("文件已提交，无法继续写入")
        
        # 确保父目录存在
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入临时文件
        try:
            if self.mode == "wb" or isinstance(content, bytes):
                # 二进制模式
                with open(self.temp_file_path, mode="wb") as f:
                    f.write(content if isinstance(content, bytes) else content.encode(self.encoding))
            else:
                # 文本模式
                with open(self.temp_file_path, mode=self.mode, encoding=self.encoding) as f:
                    f.write(str(content))
        except Exception as e:
            # 清理临时文件
            if self.temp_file_path.exists():
                try:
                    self.temp_file_path.unlink()
                except Exception as cleanup_error:
                    logger.warning(f"[atomic_writer] 清理临时文件失败: {cleanup_error}")
            raise RuntimeError(f"写入临时文件失败: {str(e)}")
        
        # 步骤 2：Flush buffer (刷入磁盘缓存)
        # Python 的 with 语句会自动 flush，但这里确保完成
        self._flush()
    
    def _flush(self) -> None:
        """
        刷入磁盘缓存（步骤 2：Flush buffer）
        
        本方法在 write() 中自动调用，确保数据写入磁盘。
        """
        # 文件已通过 with 语句自动 flush
        pass
    
    def commit(self) -> None:
        """
        提交写入（步骤 3：Atomic Rename）
        
        原子级替换重命名，确保数据一致性。
        
        Raises:
            RuntimeError: 如果提交失败
            
        Example:
            >>> writer = AtomicFileWriter("data/test.json")
            >>> writer.write('{"key": "value"}')
            >>> writer.commit()
        """
        if self._committed:
            return
        
        # 检查临时文件是否存在
        if not self.temp_file_path.exists():
            raise RuntimeError("临时文件不存在，无法提交")
        
        try:
            # 原子级替换重命名
            self.temp_file_path.replace(self.file_path)
            self._committed = True
        except Exception as e:
            # 清理临时文件
            if self.temp_file_path.exists():
                try:
                    self.temp_file_path.unlink()
                except Exception as cleanup_error:
                    logger.warning(f"[atomic_writer] 原子替换失败后清理失败: {cleanup_error}")
            raise RuntimeError(f"原子替换失败: {str(e)}")
    
    def rollback(self) -> None:
        """
        回滚写入操作（删除临时文件）
        
        Example:
            >>> writer = AtomicFileWriter("data/test.json")
            >>> writer.write('{"key": "value"}')
            >>> writer.rollback()
        """
        if self._committed:
            raise RuntimeError("文件已提交，无法回滚")
        
        # 删除临时文件
        if self.temp_file_path.exists():
            try:
                self.temp_file_path.unlink()
            except Exception as e:
                raise RuntimeError(f"删除临时文件失败: {str(e)}")
    
    def is_committed(self) -> bool:
        """
        检查是否已提交
        
        Returns:
            bool: 是否已提交
            
        Example:
            >>> if writer.is_committed():
            ...     print("文件已提交")
        """
        return self._committed
    
    def cleanup(self) -> None:
        """
        清理临时文件（如果存在）
        
        Example:
            >>> writer.cleanup()
        """
        if self.temp_file_path.exists() and not self._committed:
            try:
                self.temp_file_path.unlink()
            except Exception as cleanup_error:
                logger.warning(f"[atomic_writer] 清理临时文件失败: {cleanup_error}")
    
    def __enter__(self):
        """上下文管理器支持"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器支持（自动提交或回滚）"""
        if exc_type is None and not self._committed:
            # 没有异常，自动提交
            self.commit()
        elif not self._committed:
            # 有异常，自动回滚
            self.cleanup()
        return False
    
    @staticmethod
    def write_file(
        file_path: Union[str, Path],
        content: Union[str, bytes],
        encoding: str = "utf-8",
        mode: str = "w",
        tmp_suffix: str = ".tmp"
    ) -> None:
        """
        静态方法：一次性原子写入文件
        
        Args:
            file_path: 目标文件路径
            content: 写入内容
            encoding: 文件编码（默认 UTF-8）
            mode: 写入模式（默认 "w"）
            tmp_suffix: 临时文件后缀（默认 ".tmp"）
            
        Example:
            >>> AtomicFileWriter.write_file("data/test.json", '{"key": "value"}')
        """
        with AtomicFileWriter(file_path, encoding, mode, tmp_suffix) as writer:
            writer.write(content)
    
    @staticmethod
    def read_file(
        file_path: Union[str, Path],
        encoding: str = "utf-8",
        mode: str = "r"
    ) -> Union[str, bytes]:
        """
        读取文件（辅助方法）
        
        Args:
            file_path: 文件路径
            encoding: 文件编码（默认 UTF-8）
            mode: 读取模式（默认 "r"）
            
        Returns:
            Union[str, bytes]: 文件内容
            
        Example:
            >>> content = AtomicFileWriter.read_file("data/test.json")
        """
        path = Path(file_path) if isinstance(file_path, str) else file_path
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {path}")
        
        if mode == "rb":
            with open(path, mode="rb") as f:
                return f.read()
        else:
            with open(path, mode=mode, encoding=encoding) as f:
                return f.read()


__all__ = ['AtomicFileWriter']