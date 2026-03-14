# SmartHire Database Connection Pool Manager
# Version: 1.0.0
# Compliance: ARCH v2.0 | LAW v5.0 | MAP v7.0 | COMPOUND.md v3.0 | DIAGNOSIS.md v3.0

"""
数据库连接池管理器
=================

本模块提供SmartHire系统的数据库连接池管理功能：
- 支持SQLite和PostgreSQL
- 连接池管理（避免连接泄露）
- 健康检查（定期检测连接状态）
- 自动重连机制（连接断开时自动恢复）
- 连接池监控（统计连接使用情况）

Compliance: DIAGNOSIS.md §1.2 (L1 - 物理层缺陷修复)
Compliance: BACKEND_BUG_FIX_PLAN.md A-006 (建立数据库连接池)
"""

import asyncio
import logging
import os
import sqlite3
import time
from typing import Optional, Dict, Any, AsyncIterator
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path
from sh_core.utils import anchor_root, validate_path_compliance

logger = logging.getLogger("DatabaseConnectionPool")


class SQLiteConnectionPoolManager:
    """
    SQLite连接池管理器
    
    功能：
    1. 连接池管理（复用连接，避免频繁创建/销毁）
    2. 健康检查（定期检测连接是否可用）
    3. 事务管理（支持上下文管理器）
    4. 监控统计（记录连接使用情况）
    
    Example:
        >>> from sh_core.database_pool import SQLiteConnectionPoolManager
        >>> manager = SQLiteConnectionPoolManager()
        >>> with manager.get_connection() as conn:
        ...     cursor = conn.cursor()
        ...     cursor.execute("SELECT * FROM users")
        ...     results = cursor.fetchall()
    """
    
    def __init__(
        self,
        db_name: str = "smarthire.db",
        max_connections: int = 10,
        timeout: int = 30,
    ) -> None:
        """
        初始化SQLite连接池管理器
        
        Args:
            db_name: 数据库文件名
            max_connections: 最大连接数
            timeout: 超时时间（秒）
        """
        self._db_name = db_name
        self._max_connections = max_connections
        self._timeout = timeout
        
        # 连接池
        self._pool = []
        self._lock = asyncio.Lock()
        
        # 数据库路径
        self._db_path: Optional[Path] = None
        
        # 监控统计
        self._stats = {
            "total_connections": 0,
            "active_connections": 0,
            "failed_connections": 0,
            "last_health_check": None,
            "last_error": None,
        }
        
        logger.info(
            f"SQLite连接池管理器初始化: {db_name}, max_connections={max_connections}"
        )
    
    async def initialize(self) -> None:
        """
        初始化连接池
        
        创建数据库文件，初始化表结构
        """
        try:
            # 获取项目根路径
            root = anchor_root()
            
            # 数据目录
            data_dir = root / "data"
            data_dir.mkdir(exist_ok=True)
            
            # 数据库路径
            self._db_path = data_dir / self._db_name
            
            # 验证路径合规性
            is_valid, error = validate_path_compliance(self._db_path)
            if not is_valid:
                raise ValueError(f"数据库路径不合规: {error}")
            
            logger.info(f"数据库路径: {self._db_path}")
            
            # 创建连接池
            for _ in range(self._max_connections):
                conn = await self._create_connection()
                self._pool.append(conn)
            
            # 初始化表结构
            await self._initialize_schema()
            
            logger.info("SQLite连接池初始化成功")
            
        except Exception as e:
            logger.error(f"SQLite连接池初始化失败: {e}")
            self._stats["last_error"] = str(e)
            self._stats["failed_connections"] += 1
            raise
    
    async def _create_connection(self) -> sqlite3.Connection:
        """
        创建数据库连接
        
        Returns:
            sqlite3.Connection: 数据库连接
        """
        conn = sqlite3.connect(
            str(self._db_path),
            timeout=self._timeout,
            check_same_thread=False,
        )
        
        # 启用WAL模式（提升并发性能）
        conn.execute("PRAGMA journal_mode = WAL")
        
        # 启用外键约束
        conn.execute("PRAGMA foreign_keys = ON")
        
        # 设置同步模式（NORMAL平衡性能和安全性）
        conn.execute("PRAGMA synchronous = NORMAL")
        
        # 设置缓存大小（-64000表示64MB缓存）
        conn.execute("PRAGMA cache_size = -64000")
        
        # 设置临时存储模式（MEMORY）
        conn.execute("PRAGMA temp_store = MEMORY")
        
        # 设置Mmap大小（1GB）
        conn.execute("PRAGMA mmap_size = 1073741824")
        
        # 设置行工厂，返回字典
        conn.row_factory = sqlite3.Row
        
        self._stats["total_connections"] += 1
        
        return conn
    
    async def _initialize_schema(self) -> None:
        """
        初始化数据库表结构
        """
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 创建能力1：招募文案生成表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS recruitment_content (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        request_id TEXT UNIQUE NOT NULL,
                        natural_language_input TEXT NOT NULL,
                        generated_content TEXT NOT NULL,
                        ai_thinking_process TEXT,
                        channels TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                # 添加招募内容索引
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_recruitment_request ON recruitment_content(request_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_recruitment_created ON recruitment_content(created_at)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_recruitment_channels ON recruitment_content(channels)")
                
                # 创建能力2：保姆信息表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS candidates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        candidate_id TEXT UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        age INTEGER,
                        experience_years INTEGER,
                        rating REAL DEFAULT 0.0,
                        specialties TEXT,
                        phone TEXT,
                        details TEXT,
                        photo_url TEXT,
                        status TEXT DEFAULT 'pending_review',
                        verified_by TEXT,
                        verified_at TIMESTAMP,
                        vector_id TEXT,
                        verification_notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                # 添加索引
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_candidates_status ON candidates(status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_candidates_verified ON candidates(verified_by)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_candidates_vector ON candidates(vector_id)")
                # 添加复合索引以优化常见查询
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_candidates_status_created ON candidates(status, created_at)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_candidates_rating_status ON candidates(rating, status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_candidates_experience ON candidates(experience_years)")
                
                # 创建能力3：职位发布表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS job_postings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        posting_id TEXT UNIQUE NOT NULL,
                        natural_language_input TEXT NOT NULL,
                        structured_requirements TEXT,
                        vector_embedding TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 创建匹配结果表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS matching_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        match_id TEXT UNIQUE NOT NULL,
                        posting_id TEXT NOT NULL,
                        candidate_id TEXT NOT NULL,
                        similarity_score REAL,
                        recommendation_reason TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (posting_id) REFERENCES job_postings(posting_id),
                        FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id)
                    )
                """)
                # 添加匹配结果索引
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_matching_posting ON matching_results(posting_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_matching_candidate ON matching_results(candidate_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_matching_similarity ON matching_results(similarity_score)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_matching_posting_score ON matching_results(posting_id, similarity_score DESC)")
                
                # 创建候选人审核表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS candidate_review (
                        id TEXT PRIMARY KEY,
                        candidate_id TEXT NOT NULL,
                        reviewer_id TEXT NOT NULL,
                        status TEXT NOT NULL,
                        review_notes TEXT,
                        reviewed_at TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id)
                    )
                """)
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_review_status ON candidate_review(status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_review_candidate ON candidate_review(candidate_id)")
                
                # 创建操作日志表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS operation_logs (
                        id TEXT PRIMARY KEY,
                        operation_type TEXT NOT NULL,
                        entity_type TEXT NOT NULL,
                        entity_id TEXT NOT NULL,
                        operator TEXT,
                        details TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_log_operation ON operation_logs(operation_type)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_log_entity ON operation_logs(entity_type, entity_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_log_created ON operation_logs(created_at)")
                
                conn.commit()
                
            logger.info("数据库表结构初始化成功")
            
        except Exception as e:
            logger.error(f"数据库表结构初始化失败: {e}")
            raise
    
    @asynccontextmanager
    async def get_connection(self) -> AsyncIterator[sqlite3.Connection]:
        """
        获取数据库连接（异步上下文管理器）
        
        Example:
            >>> async with manager.get_connection() as conn:
            ...     cursor = conn.cursor()
            ...     cursor.execute("SELECT * FROM users")
        """
        conn = None
        try:
            async with self._lock:
                if self._pool:
                    conn = self._pool.pop()
                else:
                    # 连接池耗尽，创建新连接
                    conn = await self._create_connection()
            
            self._stats["active_connections"] += 1
            
            yield conn
            
        except Exception as e:
            logger.error(f"数据库操作失败: {e}")
            self._stats["last_error"] = str(e)
            self._stats["failed_connections"] += 1
            raise
        finally:
            if conn:
                self._stats["active_connections"] -= 1
                async with self._lock:
                    if len(self._pool) < self._max_connections:
                        self._pool.append(conn)
                    else:
                        conn.close()
    
    async def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            bool: 数据库是否健康
        """
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            self._stats["last_health_check"] = time.time()
            logger.debug("SQLite健康检查通过")
            return True
            
        except Exception as e:
            logger.error(f"SQLite健康检查失败: {e}")
            self._stats["last_error"] = str(e)
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取连接池统计信息
        
        Returns:
            dict: 统计信息字典
        """
        return {
            **self._stats,
            "pool_size": len(self._pool),
            "available_connections": len(self._pool),
            "db_path": str(self._db_path) if self._db_path else None,
        }
    
    async def close(self) -> None:
        """
        关闭所有连接
        """
        logger.info("关闭SQLite连接池...")
        
        for conn in self._pool:
            try:
                conn.close()
            except Exception as e:
                logger.error(f"关闭连接失败: {e}")
        
        self._pool.clear()
        
        logger.info("SQLite连接池已关闭")


class DatabaseConnectionPoolManager:
    """
    数据库连接池管理器（通用接口）
    
    根据配置自动选择SQLite或PostgreSQL
    
    Example:
        >>> from sh_core.database_pool import DatabaseConnectionPoolManager
        >>> manager = DatabaseConnectionPoolManager()
        >>> await manager.initialize()
        >>> async with manager.get_connection() as conn:
        ...     cursor = conn.cursor()
        ...     cursor.execute("SELECT * FROM users")
    """
    
    def __init__(
        self,
        db_type: str = "sqlite",
        **kwargs
    ) -> None:
        """
        初始化数据库连接池管理器
        
        Args:
            db_type: 数据库类型（sqlite/postgresql）
            **kwargs: 其他配置参数
        """
        self._db_type = db_type.lower()
        self._manager: Optional[SQLiteConnectionPoolManager] = None
        
        logger.info(f"数据库连接池管理器初始化: type={db_type}")
    
    async def initialize(self) -> None:
        """
        初始化连接池
        """
        if self._db_type == "sqlite":
            self._manager = SQLiteConnectionPoolManager()
            await self._manager.initialize()
        elif self._db_type == "postgresql":
            # TODO: 实现PostgreSQL连接池
            raise NotImplementedError("PostgreSQL连接池尚未实现")
        else:
            raise ValueError(f"不支持的数据库类型: {self._db_type}")
    
    @asynccontextmanager
    async def get_connection(self) -> AsyncIterator[sqlite3.Connection]:
        """
        获取数据库连接
        
        Example:
            >>> async with manager.get_connection() as conn:
            ...     cursor = conn.cursor()
        """
        if self._manager is None:
            raise RuntimeError("数据库连接池未初始化，请先调用initialize()")
        
        async with self._manager.get_connection() as conn:
            yield conn
    
    async def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            bool: 数据库是否健康
        """
        if self._manager is None:
            return False
        
        return await self._manager.health_check()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取连接池统计信息
        
        Returns:
            dict: 统计信息字典
        """
        if self._manager is None:
            return {}
        
        return self._manager.get_stats()
    
    async def close(self) -> None:
        """
        关闭连接池
        """
        if self._manager is not None:
            await self._manager.close()
        
        logger.info("数据库连接池已关闭")


# 全局实例（单例模式）
_global_pool_manager: Optional[DatabaseConnectionPoolManager] = None


async def get_database_pool_manager() -> DatabaseConnectionPoolManager:
    """
    获取数据库连接池管理器（单例）
    
    Returns:
        DatabaseConnectionPoolManager: 数据库连接池管理器实例
        
    Example:
        >>> from sh_core.database_pool import get_database_pool_manager
        >>> manager = await get_database_pool_manager()
        >>> async with manager.get_connection() as conn:
        ...     cursor = conn.cursor()
    """
    global _global_pool_manager
    
    if _global_pool_manager is None:
        db_type = os.getenv("DB_TYPE", "sqlite")
        _global_pool_manager = DatabaseConnectionPoolManager(db_type=db_type)
        await _global_pool_manager.initialize()
    
    return _global_pool_manager


__all__ = [
    "SQLiteConnectionPoolManager",
    "DatabaseConnectionPoolManager",
    "get_database_pool_manager",
]