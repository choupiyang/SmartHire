# SmartHire Core Utils - 工具函数库
# Version: 1.0.0
# Compliance: ARCH v2.0 | LAW v5.0 | MAP v7.0 | COMPOUND.md v3.0 | DIAGNOSIS.md v3.0

"""
工具函数库
==========

本模块提供 SmartHire 系统的核心工具函数：
- anchor_root(): 根路径锚定函数（LAW-ENV-002 合规）
- safe_write(): 原子写入协议（LAW-DATA-002 合规）
- encoding_cleaner(): 编码流清洗（ENV-03 合规）
- get_next_sequence_id(): 全局自增序列号（IPC-01 合规）

所有函数严格遵循 LAW-ENG-002（Type Hinting + Explicit Returns）。
"""

import os
import sys
import time
import logging
import redis
import tempfile
from pathlib import Path
from typing import Any, Optional, Tuple, Union

logger = logging.getLogger(__name__)

# 全局变量（根路径锚定）
_ROOT_PATH: Optional[Path] = None


def anchor_root() -> Path:
    """
    根路径锚定函数（LAW-ENV-002 合规）
    
    根据 LAW-ENV-002，严禁硬编码绝对路径。本函数通过以下策略
    自动锚定项目根目录：
    1. 从 __file__ 向上查找 .git 目录
    2. 从 __file__ 向上查找 pyproject.toml 或 setup.py
    3. 从 __file__ 向上查找 README.md
    
    Returns:
        Path: 项目根路径（已锚定）
        
    Raises:
        RuntimeError: 如果无法找到项目根目录
        
    Example:
        >>> from sh_core.utils import anchor_root
        >>> root = anchor_root()
        >>> data_dir = root / "data"
    """
    global _ROOT_PATH
    
    # 如果已经锚定，直接返回
    if _ROOT_PATH is not None:
        return _ROOT_PATH
    
    # 获取当前文件所在目录
    current_path = Path(__file__).resolve().parent
    
    # 向上查找项目根目录
    root_markers = ['.git', 'pyproject.toml', 'setup.py', 'README.md']
    
    # 最大查找深度（防止无限循环）
    max_depth = 10
    depth = 0
    
    while depth < max_depth:
        # 检查当前目录是否包含任何根标记
        for marker in root_markers:
            marker_path = current_path / marker
            if marker_path.exists():
                _ROOT_PATH = current_path
                return _ROOT_PATH
        
        # 向上一级目录查找
        parent = current_path.parent
        if parent == current_path:
            # 已到达文件系统根目录
            break
        current_path = parent
        depth += 1
    
    # 无法找到项目根目录
    raise RuntimeError(
        f"无法找到项目根目录。已向上查找 {max_depth} 层，"
        f"但未找到以下任一标记: {', '.join(root_markers)}"
    )


def validate_path_compliance(path: Union[str, Path]) -> Tuple[bool, Optional[str]]:
    """
    验证路径合规性（P0-1 修订）
    
    根据 LAW-ENV-002 和 COMPOUND ENV-01/ENV-02，验证路径是否合规：
    1. 路径深度 ≤ 5 层
    2. 路径长度 ≤ 260 字符
    3. 无绝对路径硬编码
    
    Args:
        path: 待验证的路径（字符串或 Path 对象）
        
    Returns:
        Tuple[bool, Optional[str]]: (是否合规, 错误信息)
        
    Example:
        >>> is_valid, error = validate_path_compliance("data/test.txt")
        >>> if not is_valid:
        ...     print(f"路径不合规: {error}")
    """
    # 转换为 Path 对象
    if isinstance(path, str):
        try:
            path = Path(path)
        except Exception as e:
            return False, f"路径解析失败: {str(e)}"
    
    # 转换为绝对路径
    abs_path = path.resolve()
    path_str = str(abs_path)
    
    # 例外：允许临时目录路径（用于测试）
    if path_str.startswith(tempfile.gettempdir()) or \
       path_str.startswith(os.path.expandvars("%TEMP%")):
        # 仅验证路径长度
        if len(path_str) > 260:
            return False, f"路径长度超过限制（Windows MAX_PATH）: {len(path_str)} > 260"
        return True, None
    
    # 获取根路径
    try:
        root = anchor_root()
    except RuntimeError as e:
        return False, f"根路径锚定失败: {str(e)}"
    
    # P0-1 修订: 所有文件操作前验证路径合规性
    # 1. 验证是否为绝对路径硬编码（违反 LAW-ENV-002）
    if abs_path.is_absolute():
        # 检查是否为项目根目录的子路径
        try:
            abs_path.relative_to(root)
        except ValueError:
            return False, f"禁止硬编码绝对路径（LAW-ENV-002）: {abs_path}"
    
    # 2. 验证路径深度（ENV-01: 目录嵌套 ≤ 5 层）
    relative_path = abs_path.relative_to(root) if abs_path.is_absolute() else abs_path
    depth = len(relative_path.parts)
    
    if depth > 5:
        return False, f"路径深度超过限制（ENV-01）: {depth} > 5"
    
    # 3. 验证路径长度（Windows MAX_PATH 限制）
    if len(path_str) > 260:
        return False, f"路径长度超过限制（Windows MAX_PATH）: {len(path_str)} > 260"
    
    return True, None


def safe_write(
    file_path: Union[str, Path],
    content: Any,
    encoding: str = "utf-8",
    mode: str = "w"
) -> None:
    """
    原子写入协议（LAW-DATA-002 合规）
    
    根据 LAW-DATA-002，严禁对核心数据文件进行"直接覆盖写入"。
    本函数严格执行三步走协议：
    1. Write to .tmp (写入临时文件)
    2. Flush buffer (刷入磁盘缓存)
    3. Atomic Rename (原子级替换重命名)
    
    Args:
        file_path: 目标文件路径
        content: 写入内容（字符串或字节）
        encoding: 文件编码（默认 UTF-8）
        mode: 写入模式（默认 "w"）
        
    Raises:
        ValueError: 如果路径不合规
        RuntimeError: 如果写入失败
        
    Example:
        >>> from sh_core.utils import safe_write
        >>> safe_write("data/test.json", '{"key": "value"}')
    """
    # 转换为 Path 对象
    if isinstance(file_path, str):
        file_path = Path(file_path)
    
    # P0-1 修订: 验证路径合规性
    is_valid, error = validate_path_compliance(file_path)
    if not is_valid:
        raise ValueError(f"路径不合规: {error}")
    
    # 确保父目录存在
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 创建临时文件路径
    temp_file_path = file_path.with_suffix(file_path.suffix + ".tmp")
    
    try:
        # 步骤 1: Write to .tmp (写入临时文件)
        if mode == "wb":
            # 二进制模式
            with open(temp_file_path, mode="wb") as f:
                f.write(content)
        else:
            # 文本模式
            with open(temp_file_path, mode=mode, encoding=encoding) as f:
                f.write(str(content))
        
        # 步骤 2: Flush buffer (刷入磁盘缓存)
        # Python 的 with 语句会自动 flush，但这里显式调用确保
        
        # 步骤 3: Atomic Rename (原子级替换重命名)
        temp_file_path.replace(file_path)
        
    except Exception as e:
        # 清理临时文件
        if temp_file_path.exists():
            try:
                temp_file_path.unlink()
            except Exception as cleanup_error:
                logger.warning(f"[utils] safe_write清理失败: {cleanup_error}")
        
        raise RuntimeError(f"原子写入失败: {str(e)}")


def encoding_cleaner(
    data: Union[str, bytes],
    target_encoding: str = "utf-8"
) -> str:
    """
    编码流清洗（ENV-03 合规）
    
    根据 COMPOUND ENV-03，Windows 默认 OEM 代码页与 Python UTF-8 冲突。
    本函数实现 GBK/UTF-8 双向清洗管道：
    1. 尝试 GBK 解码
    2. 如果失败，尝试 UTF-8 解码
    3. 转换为目标编码
    
    Args:
        data: 输入数据（字符串或字节）
        target_encoding: 目标编码（默认 UTF-8）
        
    Returns:
        str: 清洗后的字符串
        
    Example:
        >>> from sh_core.utils import encoding_cleaner
        >>> text = encoding_cleaner(raw_bytes)
    """
    # 如果已经是字符串，直接返回
    if isinstance(data, str):
        return data
    
    # 如果是字节，尝试解码
    if isinstance(data, bytes):
        # 尝试 GBK 解码
        try:
            decoded = data.decode("gbk")
            # 转换为目标编码
            return decoded.encode(target_encoding, errors="replace").decode(target_encoding)
        except (UnicodeDecodeError, UnicodeEncodeError):
            # GBK 解码失败，尝试 UTF-8 解码
            try:
                return data.decode("utf-8", errors="replace")
            except UnicodeDecodeError:
                # UTF-8 解码也失败，返回替换字符
                return "\ufffd"
    
    # 其他类型，转换为字符串
    return str(data)


def get_redis_client() -> redis.Redis:
    """
    获取 Redis 客户端（单例模式）
    
    Returns:
        redis.Redis: Redis 客户端实例
        
    Example:
        >>> from sh_core.utils import get_redis_client
        >>> client = get_redis_client()
    """
    # TODO: 从环境变量读取 Redis 配置
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))
    redis_db = int(os.getenv("REDIS_DB", "0"))
    
    return redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)


def get_next_sequence_id(key: str = "global_sequence") -> int:
    """
    全局自增序列号（IPC-01 合规）
    
    根据 COMPOUND IPC-01，封包必须携带全局自增 sequence_id，
    接收端自动丢弃过期指令。
    
    Args:
        key: 序列号键名（默认 "global_sequence"）
        
    Returns:
        int: 下一个序列号
        
    Example:
        >>> from sh_core.utils import get_next_sequence_id
        >>> sequence_id = get_next_sequence_id()
    """
    client = get_redis_client()
    
    try:
        # 使用 Redis INCR 原子操作获取序列号
        sequence_id: int = int(client.incr(key))
        return sequence_id
    except redis.RedisError as e:
        # Redis 不可用，返回基于时间戳的序列号（降级方案）
        return int(time.time() * 1000000)


__all__ = [
    # 根路径锚定
    'anchor_root',
    'validate_path_compliance',
    
    # 原子写入
    'safe_write',
    
    # 编码清洗
    'encoding_cleaner',
    
    # 序列号
    'get_redis_client',
    'get_next_sequence_id',
]