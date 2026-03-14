"""
向量数据库管理器模块

提供向量存储、搜索和相似度计算功能，支持多维匹配推荐。
"""

import sqlite3
import logging
import pickle
import json
import uuid
import math
from typing import Dict, Any, List, Optional, Tuple, AsyncIterator
from dataclasses import dataclass, asdict
from datetime import datetime
from contextlib import asynccontextmanager
import asyncio

from sh_core.errors import DatabaseError, ErrorCode
from sh_core.vector_cache import VectorSearchCache

logger = logging.getLogger(__name__)


@dataclass
class VectorRecord:
    """向量记录"""
    id: str
    entity_type: str  # candidate, requirement, job_posting
    entity_id: str
    vector: List[float]
    metadata: Dict[str, Any]
    created_at: str
    updated_at: str


class VectorDatabaseManager:
    """
    向量数据库管理器
    
    基于SQLite实现的向量数据库，支持向量存储和余弦相似度搜索
    """
    
    def __init__(
        self,
        db_path: str,
        dimension: int = 1536,  # OpenAI embedding维度
        enable_cache: bool = True,
        cache_max_size: int = 1000,
        cache_ttl: int = 3600
    ) -> None:
        """
        初始化向量数据库管理器
        
        Args:
            db_path: 数据库文件路径
            dimension: 向量维度
            enable_cache: 是否启用缓存
            cache_max_size: 缓存最大条目数
            cache_ttl: 缓存有效期（秒）
        """
        self.db_path = db_path
        self.dimension = dimension
        self._connection = None
        self._lock = asyncio.Lock()
        
        # 初始化缓存
        self.enable_cache = enable_cache
        self._cache = VectorSearchCache(
            max_size=cache_max_size,
            default_ttl=cache_ttl
        ) if enable_cache else None
        
        # 初始化数据库
        self._init_database()
        
        logger.info(f"向量数据库管理器初始化完成: db_path={db_path}, dimension={dimension}, cache={'enabled' if enable_cache else 'disabled'}")
    
    def _init_database(self) -> None:
        """初始化数据库表结构"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建向量表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vectors (
                    id TEXT PRIMARY KEY,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    vector BLOB NOT NULL,
                    dimension INTEGER NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_entity_type ON vectors(entity_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_entity_id ON vectors(entity_id)")
            
            # 创建向量归一化表（用于加速搜索）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vector_norms (
                    vector_id TEXT PRIMARY KEY,
                    norm REAL NOT NULL,
                    FOREIGN KEY (vector_id) REFERENCES vectors(id)
                )
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("向量数据库表结构初始化完成")
            
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}", exc_info=True)
            raise DatabaseError(
                error_code=ErrorCode.SH_DB_INIT_001,
                message=f"向量数据库初始化失败: {str(e)}"
            )
    
    @asynccontextmanager
    async def _get_connection(self) -> AsyncIterator[sqlite3.Connection]:
        """
        获取数据库连接（异步上下文管理器）
        
        Yields:
            数据库连接
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"数据库连接错误: {e}", exc_info=True)
            raise DatabaseError(
                error_code=ErrorCode.SH_DB_CONN_001,
                message=f"数据库连接失败: {str(e)}"
            )
        finally:
            if conn:
                conn.close()
    
    async def insert_vector(
        self,
        entity_type: str,
        entity_id: str,
        vector: List[float],
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        插入向量
        
        Args:
            entity_type: 实体类型（candidate/requirement/job_posting）
            entity_id: 实体ID
            vector: 向量数据
            metadata: 元数据
            
        Returns:
            是否成功插入
        """
        async with self._lock:
            try:
                # 验证向量维度
                if len(vector) != self.dimension:
                    raise DatabaseError(
                        error_code=ErrorCode.SH_DB_VAL_001,
                        message=f"向量维度不匹配: 期望{self.dimension}, 实际{len(vector)}"
                    )
                
                # 检查是否已存在
                async with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        SELECT id FROM vectors
                        WHERE entity_type = ? AND entity_id = ?
                        """,
                        (entity_type, entity_id)
                    )
                    existing = cursor.fetchone()
                    
                    if existing:
                        # 更新现有记录
                        vector_id = existing["id"]
                        cursor.execute(
                            """
                            UPDATE vectors
                            SET vector = ?, dimension = ?, metadata = ?, updated_at = CURRENT_TIMESTAMP
                            WHERE id = ?
                            """,
                            (pickle.dumps(vector), len(vector), json.dumps(metadata), vector_id)
                        )
                    else:
                        # 插入新记录
                        vector_id = str(uuid.uuid4())
                        cursor.execute(
                            """
                            INSERT INTO vectors (id, entity_type, entity_id, vector, dimension, metadata)
                            VALUES (?, ?, ?, ?, ?, ?)
                            """,
                            (
                                vector_id,
                                entity_type,
                                entity_id,
                                pickle.dumps(vector),
                                len(vector),
                                json.dumps(metadata) if metadata else None
                            )
                        )
                    
                    # 更新向量归一化值
                    norm = self._calculate_norm(vector)
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO vector_norms (vector_id, norm)
                        VALUES (?, ?)
                        """,
                        (vector_id, norm)
                    )
                    
                    conn.commit()
                    
                    logger.info(f"向量{'更新' if existing else '插入'}成功: entity_type={entity_type}, entity_id={entity_id}")
                    
                    return True
                    
            except Exception as e:
                logger.error(f"向量插入失败: {e}", exc_info=True)
                return False
    
    async def search_vectors(
        self,
        query_vector: List[float],
        entity_type: str,
        top_k: int = 10,
        min_similarity: float = 0.0,
        filters: Dict[str, Any] = None,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        搜索最相似的向量
        
        Args:
            query_vector: 查询向量
            entity_type: 实体类型
            top_k: 返回前k个结果
            min_similarity: 最小相似度阈值
            filters: 过滤条件
            use_cache: 是否使用缓存
            
        Returns:
            相似结果列表
        """
        # 尝试从缓存获取
        if self.enable_cache and use_cache and self._cache:
            cached_results = await self._cache.get(
                query_vector, entity_type, top_k, min_similarity, filters
            )
            if cached_results is not None:
                logger.debug(f"向量搜索缓存命中: entity_type={entity_type}")
                return cached_results
        
        try:
            # 验证查询向量维度
            if len(query_vector) != self.dimension:
                raise DatabaseError(
                    error_code=ErrorCode.SH_DB_VAL_001,
                    message=f"查询向量维度不匹配: 期望{self.dimension}, 实际{len(query_vector)}"
                )
            
            # 计算查询向量归一化
            query_norm = self._calculate_norm(query_vector)
            
            # 查询所有向量
            async with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT v.id, v.entity_id, v.vector, v.metadata, vn.norm
                    FROM vectors v
                    JOIN vector_norms vn ON v.id = vn.vector_id
                    WHERE v.entity_type = ?
                    """,
                    (entity_type,)
                )
                
                results = cursor.fetchall()
                
                # 计算相似度
                similarities = []
                for row in results:
                    vector_id = row["id"]
                    entity_id = row["entity_id"]
                    vector_blob = row["vector"]
                    metadata_blob = row["metadata"]
                    vector_norm = row["norm"]
                    
                    # 反序列化向量
                    vector = pickle.loads(vector_blob)
                    metadata = json.loads(metadata_blob) if metadata_blob else {}
                    
                    # 应用过滤器
                    if filters and not self._apply_filters(metadata, filters):
                        continue
                    
                    # 计算余弦相似度
                    similarity = self._cosine_similarity(query_vector, query_norm, vector, vector_norm)
                    
                    # 过滤低相似度结果
                    if similarity < min_similarity:
                        continue
                    
                    similarities.append({
                        "vector_id": vector_id,
                        "entity_id": entity_id,
                        "similarity": similarity,
                        "metadata": metadata
                    })
                
                # 按相似度排序
                similarities.sort(key=lambda x: x["similarity"], reverse=True)
                
                # 返回前k个结果
                results = similarities[:top_k]
                
                # 将结果存入缓存
                if self.enable_cache and use_cache and self._cache:
                    await self._cache.set(
                        query_vector, entity_type, results, top_k, min_similarity, filters
                    )
                
                return results
                
        except Exception as e:
            logger.error(f"向量搜索失败: {e}", exc_info=True)
            return []
    
    async def get_vector(
        self,
        entity_type: str,
        entity_id: str
    ) -> Optional[VectorRecord]:
        """
        获取向量记录
        
        Args:
            entity_type: 实体类型
            entity_id: 实体ID
            
        Returns:
            向量记录
        """
        try:
            async with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, entity_type, entity_id, vector, metadata, created_at, updated_at
                    FROM vectors
                    WHERE entity_type = ? AND entity_id = ?
                    """,
                    (entity_type, entity_id)
                )
                
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                return VectorRecord(
                    id=row["id"],
                    entity_type=row["entity_type"],
                    entity_id=row["entity_id"],
                    vector=pickle.loads(row["vector"]),
                    metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                    created_at=row["created_at"],
                    updated_at=row["updated_at"]
                )
                
        except Exception as e:
            logger.error(f"获取向量失败: {e}", exc_info=True)
            return None
    
    async def delete_vector(
        self,
        entity_type: str,
        entity_id: str
    ) -> bool:
        """
        删除向量
        
        Args:
            entity_type: 实体类型
            entity_id: 实体ID
            
        Returns:
            是否成功删除
        """
        try:
            async with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    DELETE FROM vectors
                    WHERE entity_type = ? AND entity_id = ?
                    """,
                    (entity_type, entity_id)
                )
                
                conn.commit()
                
                logger.info(f"向量删除成功: entity_type={entity_type}, entity_id={entity_id}")
                
                return True
                
        except Exception as e:
            logger.error(f"向量删除失败: {e}", exc_info=True)
            return False
    
    async def batch_insert_vectors(
        self,
        vectors: List[Dict[str, Any]]
    ) -> int:
        """
        批量插入向量
        
        Args:
            vectors: 向量列表
            
        Returns:
            成功插入/更新的向量数量
        """
        async with self._lock:
            try:
                async with self._get_connection() as conn:
                    cursor = conn.cursor()
                    
                    for vec_data in vectors:
                        entity_type = vec_data["entity_type"]
                        entity_id = vec_data["entity_id"]
                        vector = vec_data["vector"]
                        metadata = vec_data.get("metadata", {})
                        
                        # 检查是否已存在
                        cursor.execute(
                            """
                            SELECT id FROM vectors
                            WHERE entity_type = ? AND entity_id = ?
                            """,
                            (entity_type, entity_id)
                        )
                        existing = cursor.fetchone()
                        
                        if existing:
                            # 更新现有记录
                            vector_id = existing["id"]
                            cursor.execute(
                                """
                                UPDATE vectors
                                SET vector = ?, dimension = ?, metadata = ?, updated_at = CURRENT_TIMESTAMP
                                WHERE id = ?
                                """,
                                (pickle.dumps(vector), len(vector), json.dumps(metadata), vector_id)
                            )
                        else:
                            # 插入新记录
                            vector_id = str(uuid.uuid4())
                            cursor.execute(
                                """
                                INSERT INTO vectors (id, entity_type, entity_id, vector, dimension, metadata)
                                VALUES (?, ?, ?, ?, ?, ?)
                                """,
                                (
                                    vector_id,
                                    entity_type,
                                    entity_id,
                                    pickle.dumps(vector),
                                    len(vector),
                                    json.dumps(metadata)
                                )
                            )
                        
                        # 更新向量归一化值
                        norm = self._calculate_norm(vector)
                        cursor.execute(
                            """
                            INSERT OR REPLACE INTO vector_norms (vector_id, norm)
                            VALUES (?, ?)
                            """,
                            (vector_id, norm)
                        )
                    
                    conn.commit()
                    
                    success_count = len(vectors)
                    logger.info(f"批量向量插入成功: count={success_count}")
                    
                    return success_count
                    
            except Exception as e:
                logger.error(f"批量向量插入失败: {e}", exc_info=True)
                return 0
    
    def _calculate_norm(self, vector: List[float]) -> float:
        """
        计算向量范数（L2范数）
        
        Args:
            vector: 向量
            
        Returns:
            范数值
        """
        return math.sqrt(sum(x * x for x in vector))
    
    def _cosine_similarity(
        self,
        vec_a: List[float],
        norm_a: float,
        vec_b: List[float],
        norm_b: float
    ) -> float:
        """
        计算余弦相似度
        
        Args:
            vec_a: 向量a
            norm_a: 向量a的范数
            vec_b: 向量b
            norm_b: 向量b的范数
            
        Returns:
            余弦相似度
        """
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    def _apply_filters(
        self,
        metadata: Dict[str, Any],
        filters: Dict[str, Any]
    ) -> bool:
        """
        应用过滤条件
        
        Args:
            metadata: 元数据
            filters: 过滤条件
            
        Returns:
            是否通过过滤
        """
        for key, value in filters.items():
            if key not in metadata:
                return False
            
            if isinstance(value, list):
                # 列表包含检查
                if metadata[key] not in value:
                    return False
            elif isinstance(value, dict):
                # 范围检查
                if "min" in value and metadata[key] < value["min"]:
                    return False
                if "max" in value and metadata[key] > value["max"]:
                    return False
            else:
                # 精确匹配
                if metadata[key] != value:
                    return False
        
        return True
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            缓存统计信息
        """
        if not self.enable_cache or not self._cache:
            return {
                "enabled": False,
                "stats": None
            }
        
        stats = await self._cache.get_stats()
        return {
            "enabled": True,
            "stats": stats
        }
    
    async def clear_cache(self, entity_type: Optional[str] = None) -> int:
        """
        清除缓存
        
        Args:
            entity_type: 实体类型，None表示清除所有缓存
            
        Returns:
            清除的缓存条目数
        """
        if not self.enable_cache or not self._cache:
            return 0
        
        return await self._cache.invalidate(entity_type)
    
    async def clear_expired_cache(self) -> int:
        """
        清除过期缓存
        
        Returns:
            清除的条目数
        """
        if not self.enable_cache or not self._cache:
            return 0
        
        return await self._cache.clear_expired()
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        获取数据库统计信息
        
        Returns:
            统计信息
        """
        try:
            async with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # 总向量数
                cursor.execute("SELECT COUNT(*) as total FROM vectors")
                total = cursor.fetchone()["total"]
                
                # 按类型分组统计
                cursor.execute("""
                    SELECT entity_type, COUNT(*) as count
                    FROM vectors
                    GROUP BY entity_type
                """)
                by_type = {row["entity_type"]: row["count"] for row in cursor.fetchall()}
                
                # 获取缓存统计
                cache_stats = await self.get_cache_stats()
                
                return {
                    "total_vectors": total,
                    "by_type": by_type,
                    "dimension": self.dimension,
                    "cache": cache_stats
                }
                
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}", exc_info=True)
            return {
                "total_vectors": 0,
                "by_type": {},
                "dimension": self.dimension,
                "cache": {"enabled": False, "stats": None}
            }
    
    async def batch_search_vectors(
        self,
        query_vectors: List[List[float]],
        entity_type: str,
        top_k: int = 10,
        min_similarity: float = 0.0,
        filters: Dict[str, Any] = None,
        use_cache: bool = True
    ) -> List[List[Dict[str, Any]]]:
        """
        批量向量搜索
        
        Args:
            query_vectors: 查询向量列表
            entity_type: 实体类型
            top_k: 每个查询返回前k个结果
            min_similarity: 最小相似度阈值
            filters: 过滤条件
            use_cache: 是否使用缓存
            
        Returns:
            相似结果列表的列表
        """
        try:
            # 验证所有查询向量维度
            for idx, query_vector in enumerate(query_vectors):
                if len(query_vector) != self.dimension:
                    raise DatabaseError(
                        error_code=ErrorCode.SH_DB_VAL_001,
                        message=f"查询向量{idx}维度不匹配: 期望{self.dimension}, 实际{len(query_vector)}"
                    )
            
            # 计算所有查询向量的归一化值
            query_norms = [self._calculate_norm(qv) for qv in query_vectors]
            
            # 查询所有向量
            async with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT v.id, v.entity_id, v.vector, v.metadata, vn.norm
                    FROM vectors v
                    JOIN vector_norms vn ON v.id = vn.vector_id
                    WHERE v.entity_type = ?
                    """,
                    (entity_type,)
                )
                
                all_vectors = cursor.fetchall()
                
                # 批量计算相似度
                batch_results = []
                for query_vector, query_norm in zip(query_vectors, query_norms):
                    similarities = []
                    
                    for row in all_vectors:
                        vector_id = row["id"]
                        entity_id = row["entity_id"]
                        vector_blob = row["vector"]
                        metadata_blob = row["metadata"]
                        vector_norm = row["norm"]
                        
                        # 反序列化向量
                        vector = pickle.loads(vector_blob)
                        metadata = json.loads(metadata_blob) if metadata_blob else {}
                        
                        # 应用过滤器
                        if filters and not self._apply_filters(metadata, filters):
                            continue
                        
                        # 计算余弦相似度
                        similarity = self._cosine_similarity(query_vector, query_norm, vector, vector_norm)
                        
                        # 过滤低相似度结果
                        if similarity < min_similarity:
                            continue
                        
                        similarities.append({
                            "vector_id": vector_id,
                            "entity_id": entity_id,
                            "similarity": similarity,
                            "metadata": metadata
                        })
                    
                    # 按相似度排序并返回前k个结果
                    similarities.sort(key=lambda x: x["similarity"], reverse=True)
                    batch_results.append(similarities[:top_k])
                
                return batch_results
                
        except Exception as e:
            logger.error(f"批量向量搜索失败: {e}", exc_info=True)
            return [[] for _ in query_vectors]
    
    async def rebuild_index(self) -> bool:
        """
        重建向量索引
        
        SQLite向量数据库使用归一化值缓存表作为索引优化
        重建索引会重新计算所有向量的归一化值
        
        Returns:
            是否成功重建
        """
        async with self._lock:
            try:
                async with self._get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # 获取所有向量
                    cursor.execute("SELECT id, vector FROM vectors")
                    vectors = cursor.fetchall()
                    
                    # 清空归一化表
                    cursor.execute("DELETE FROM vector_norms")
                    
                    # 重新计算归一化值
                    for row in vectors:
                        vector_id = row["id"]
                        vector_blob = row["vector"]
                        vector = pickle.loads(vector_blob)
                        norm = self._calculate_norm(vector)
                        
                        cursor.execute(
                            """
                            INSERT INTO vector_norms (vector_id, norm)
                            VALUES (?, ?)
                            """,
                            (vector_id, norm)
                        )
                    
                    conn.commit()
                    
                    logger.info(f"向量索引重建成功: count={len(vectors)}")
                    
                    return True
                    
            except Exception as e:
                logger.error(f"向量索引重建失败: {e}", exc_info=True)
                return False
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """
        获取索引统计信息
        
        Returns:
            索引统计信息
        """
        try:
            async with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # 向量表统计
                cursor.execute("SELECT COUNT(*) as total FROM vectors")
                total_vectors = cursor.fetchone()["total"]
                
                # 归一化表统计
                cursor.execute("SELECT COUNT(*) as total FROM vector_norms")
                total_norms = cursor.fetchone()["total"]
                
                # 归一化值分布
                cursor.execute("""
                    SELECT
                        MIN(norm) as min_norm,
                        MAX(norm) as max_norm,
                        AVG(norm) as avg_norm,
                        COUNT(*) as count
                    FROM vector_norms
                """)
                norm_stats = cursor.fetchone()
                
                # 按类型分组统计
                cursor.execute("""
                    SELECT entity_type, COUNT(*) as count
                    FROM vectors
                    GROUP BY entity_type
                """)
                by_type = {row["entity_type"]: row["count"] for row in cursor.fetchall()}
                
                # 最近更新统计
                cursor.execute("""
                    SELECT
                        MAX(updated_at) as last_updated,
                        MIN(created_at) as first_created
                    FROM vectors
                """)
                time_stats = cursor.fetchone()
                
                return {
                    "total_vectors": total_vectors,
                    "indexed_vectors": total_norms,
                    "index_coverage": total_norms / total_vectors if total_vectors > 0 else 0.0,
                    "norm_statistics": {
                        "min": float(norm_stats["min_norm"]) if norm_stats["count"] > 0 else 0.0,
                        "max": float(norm_stats["max_norm"]) if norm_stats["count"] > 0 else 0.0,
                        "avg": float(norm_stats["avg_norm"]) if norm_stats["count"] > 0 else 0.0
                    },
                    "by_type": by_type,
                    "time_range": {
                        "first_created": time_stats["first_created"],
                        "last_updated": time_stats["last_updated"]
                    },
                    "dimension": self.dimension
                }
                
        except Exception as e:
            logger.error(f"获取索引统计信息失败: {e}", exc_info=True)
            return {
                "total_vectors": 0,
                "indexed_vectors": 0,
                "index_coverage": 0.0,
                "norm_statistics": {
                    "min": 0.0,
                    "max": 0.0,
                    "avg": 0.0
                },
                "by_type": {},
                "time_range": {
                    "first_created": None,
                    "last_updated": None
                },
                "dimension": self.dimension
            }
    
    async def close(self) -> None:
        """关闭数据库连接"""
        if self._connection:
            self._connection.close()
            self._connection = None
        logger.info("向量数据库管理器已关闭")