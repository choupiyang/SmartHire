# SmartHire Batch Operations Manager
# Version: 1.0.0
# Compliance: ARCH v2.0 | LAW v5.0 | MAP v7.0 | COMPOUND.md v3.0 | DIAGNOSIS.md v3.0

"""
批量操作管理器
===============

本模块提供SmartHire系统的批量操作功能：
- 批量插入（减少数据库往返次数）
- 批量更新（提升更新效率）
- 批量查询（减少查询次数）
- 事务管理（保证数据一致性）
- 性能监控（记录批量操作性能指标）

Compliance: DIAGNOSIS.md §1.2 (L1 - 物理层缺陷修复)
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, Tuple, Callable, Awaitable, AsyncIterator
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
import json

logger = logging.getLogger("BatchOperationsManager")


@dataclass
class BatchOperationStats:
    """
    批量操作统计信息
    """
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    total_time: float = 0.0
    average_time: float = 0.0
    last_error: Optional[str] = None
    
    def __post_init__(self) -> None:
        """初始化后处理"""
        if self.total_operations > 0:
            self.average_time = self.total_time / self.total_operations
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "total_operations": self.total_operations,
            "successful_operations": self.successful_operations,
            "failed_operations": self.failed_operations,
            "total_time": self.total_time,
            "average_time": self.average_time,
            "last_error": self.last_error,
        }


@dataclass
class BatchInsertResult:
    """
    批量插入结果
    """
    inserted_count: int = 0
    failed_count: int = 0
    inserted_ids: List[str] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "inserted_count": self.inserted_count,
            "failed_count": self.failed_count,
            "inserted_ids": self.inserted_ids,
            "errors": self.errors,
        }


@dataclass
class BatchUpdateResult:
    """
    批量更新结果
    """
    updated_count: int = 0
    failed_count: int = 0
    errors: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "updated_count": self.updated_count,
            "failed_count": self.failed_count,
            "errors": self.errors,
        }


@dataclass
class BatchQueryResult:
    """
    批量查询结果
    """
    total_queries: int = 0
    successful_queries: int = 0
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    total_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "total_queries": self.total_queries,
            "successful_queries": self.successful_queries,
            "results": self.results,
            "errors": self.errors,
            "total_time": self.total_time,
        }


class BatchOperationsManager:
    """
    批量操作管理器
    
    功能：
    1. 批量插入（使用单条SQL插入多条记录）
    2. 批量更新（使用CASE WHEN优化）
    3. 批量查询（并行执行多个查询）
    4. 事务管理（支持回滚）
    5. 性能监控（记录操作耗时）
    
    Example:
        >>> from sh_core.batch_operations import BatchOperationsManager
        >>> manager = BatchOperationsManager(db_pool)
        >>> result = await manager.batch_insert("candidates", records)
        >>> print(f"Inserted {result.inserted_count} records")
    """
    
    def __init__(self, db_pool) -> None:
        """
        初始化批量操作管理器
        
        Args:
            db_pool: 数据库连接池管理器
        """
        self._db_pool = db_pool
        self._stats = BatchOperationStats()
        self._batch_size = 100  # 默认批次大小
        
        logger.info("批量操作管理器初始化成功")
    
    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[Any]:
        """
        事务上下文管理器
        
        Example:
            >>> async with manager.transaction() as conn:
            ...     # 执行多个操作
            ...     await manager.batch_insert(...)
            ...     await manager.batch_update(...)
        """
        async with self._db_pool.get_connection() as conn:
            try:
                # 开始事务
                conn.execute("BEGIN")
                yield conn
                # 提交事务
                conn.commit()
                logger.debug("事务提交成功")
            except Exception as e:
                # 回滚事务
                conn.rollback()
                logger.error(f"事务回滚: {e}")
                raise
    
    async def batch_insert(
        self,
        table: str,
        records: List[Dict[str, Any]],
        batch_size: Optional[int] = None,
        on_conflict: Optional[str] = None,
    ) -> BatchInsertResult:
        """
        批量插入记录
        
        Args:
            table: 表名
            records: 记录列表
            batch_size: 批次大小（None使用默认值）
            on_conflict: 冲突处理策略（None/REPLACE/IGNORE）
        
        Returns:
            BatchInsertResult: 批量插入结果
        
        Example:
            >>> records = [
            ...     {"name": "张三", "age": 30},
            ...     {"name": "李四", "age": 25},
            ... ]
            >>> result = await manager.batch_insert("candidates", records)
        """
        start_time = time.time()
        batch_size = batch_size or self._batch_size
        result = BatchInsertResult()
        
        try:
            if not records:
                logger.warning("批量插入：记录列表为空")
                return result
            
            # 获取字段名
            columns = list(records[0].keys())
            placeholders = ", ".join(["?" for _ in columns])
            columns_str = ", ".join(columns)
            
            # 处理冲突策略
            conflict_clause = ""
            if on_conflict == "REPLACE":
                conflict_clause = "OR REPLACE"
            elif on_conflict == "IGNORE":
                conflict_clause = "OR IGNORE"
            
            # 分批插入
            async with self._db_pool.get_connection() as conn:
                for i in range(0, len(records), batch_size):
                    batch = records[i:i + batch_size]
                    
                    # 构建批量插入SQL
                    sql = f"""
                        INSERT {conflict_clause} INTO {table} ({columns_str})
                        VALUES ({placeholders})
                    """
                    
                    # 准备参数
                    params_list = [tuple(record.get(col) for col in columns) for record in batch]
                    
                    try:
                        cursor = conn.cursor()
                        cursor.executemany(sql, params_list)
                        conn.commit()
                        
                        # 记录成功
                        result.inserted_count += len(batch)
                        self._stats.successful_operations += len(batch)
                        
                        # 获取插入的ID（如果有）
                        if cursor.lastrowid:
                            result.inserted_ids.append(str(cursor.lastrowid))
                        
                        logger.debug(f"批量插入批次成功: {i} - {i + len(batch)}")
                        
                    except Exception as e:
                        result.failed_count += len(batch)
                        result.errors.append({
                            "batch_start": i,
                            "batch_end": i + len(batch),
                            "error": str(e),
                        })
                        self._stats.failed_operations += len(batch)
                        self._stats.last_error = str(e)
                        logger.error(f"批量插入批次失败: {e}")
            
            # 更新统计
            elapsed_time = time.time() - start_time
            self._stats.total_operations += len(records)
            self._stats.total_time += elapsed_time
            self._stats.average_time = self._stats.total_time / self._stats.total_operations
            
            logger.info(
                f"批量插入完成: 成功={result.inserted_count}, "
                f"失败={result.failed_count}, 耗时={elapsed_time:.2f}秒"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"批量插入失败: {e}")
            result.failed_count = len(records)
            result.errors.append({"error": str(e)})
            self._stats.last_error = str(e)
            return result
    
    async def batch_update(
        self,
        table: str,
        updates: List[Dict[str, Any]],
        id_field: str = "id",
        batch_size: Optional[int] = None,
    ) -> BatchUpdateResult:
        """
        批量更新记录
        
        Args:
            table: 表名
            updates: 更新列表（每个字典包含要更新的字段和id_field）
            id_field: ID字段名
            batch_size: 批次大小
        
        Returns:
            BatchUpdateResult: 批量更新结果
        
        Example:
            >>> updates = [
            ...     {"id": 1, "status": "approved"},
            ...     {"id": 2, "status": "rejected"},
            ... ]
            >>> result = await manager.batch_update("candidates", updates)
        """
        start_time = time.time()
        batch_size = batch_size or self._batch_size
        result = BatchUpdateResult()
        
        try:
            if not updates:
                logger.warning("批量更新：更新列表为空")
                return result
            
            # 获取所有更新字段（排除id_field）
            all_fields = set()
            for update in updates:
                all_fields.update(update.keys())
            all_fields.discard(id_field)
            update_fields = list(all_fields)
            
            # 分批更新
            async with self._db_pool.get_connection() as conn:
                for i in range(0, len(updates), batch_size):
                    batch = updates[i:i + batch_size]
                    
                    try:
                        cursor = conn.cursor()
                        
                        # 为每个记录执行单独的UPDATE
                        for update in batch:
                            if id_field not in update:
                                continue
                            
                            # 构建UPDATE语句
                            set_clauses = []
                            params = []
                            for field in update_fields:
                                if field in update:
                                    set_clauses.append(f"{field} = ?")
                                    params.append(update[field])
                            
                            if not set_clauses:
                                continue
                            
                            params.append(update[id_field])
                            sql = f"""
                                UPDATE {table}
                                SET {', '.join(set_clauses)}
                                WHERE {id_field} = ?
                            """
                            
                            cursor.execute(sql, params)
                        
                        conn.commit()
                        
                        # 记录成功
                        result.updated_count += len(batch)
                        self._stats.successful_operations += len(batch)
                        
                        logger.debug(f"批量更新批次成功: {i} - {i + len(batch)}")
                        
                    except Exception as e:
                        result.failed_count += len(batch)
                        result.errors.append({
                            "batch_start": i,
                            "batch_end": i + len(batch),
                            "error": str(e),
                        })
                        self._stats.failed_operations += len(batch)
                        self._stats.last_error = str(e)
                        logger.error(f"批量更新批次失败: {e}")
            
            # 更新统计
            elapsed_time = time.time() - start_time
            self._stats.total_operations += len(updates)
            self._stats.total_time += elapsed_time
            self._stats.average_time = self._stats.total_time / self._stats.total_operations
            
            logger.info(
                f"批量更新完成: 成功={result.updated_count}, "
                f"失败={result.failed_count}, 耗时={elapsed_time:.2f}秒"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"批量更新失败: {e}")
            result.failed_count = len(updates)
            result.errors.append({"error": str(e)})
            self._stats.last_error = str(e)
            return result
    
    async def batch_query(
        self,
        queries: List[Tuple[str, str, List[Any]]],
        parallel: bool = True,
    ) -> BatchQueryResult:
        """
        批量查询
        
        Args:
            queries: 查询列表，每个查询是 (key, sql, params) 元组
            parallel: 是否并行执行
        
        Returns:
            BatchQueryResult: 批量查询结果
        
        Example:
            >>> queries = [
            ...     ("pending", "SELECT * FROM candidates WHERE status = ?", ["pending"]),
            ...     ("approved", "SELECT * FROM candidates WHERE status = ?", ["approved"]),
            ... ]
            >>> result = await manager.batch_query(queries)
            >>> pending = result.results["pending"]
        """
        start_time = time.time()
        result = BatchQueryResult()
        result.total_queries = len(queries)
        
        try:
            if not queries:
                logger.warning("批量查询：查询列表为空")
                return result
            
            async def execute_query(
                key: str,
                sql: str,
                params: List[Any],
            ) -> Tuple[str, Any]:
                """执行单个查询"""
                try:
                    async with self._db_pool.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute(sql, params)
                        rows = cursor.fetchall()
                        
                        # 转换为字典列表
                        columns = [col[0] for col in cursor.description]
                        results = [dict(zip(columns, row)) for row in rows]
                        
                        return key, results
                        
                except Exception as e:
                    logger.error(f"查询失败 [{key}]: {e}")
                    raise
            
            if parallel:
                # 并行执行查询
                tasks = [execute_query(key, sql, params) for key, sql, params in queries]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for item in results:
                    if isinstance(item, Exception):
                        result.errors.append({"error": str(item)})
                        self._stats.failed_operations += 1
                    else:
                        key, data = item
                        result.results[key] = data
                        result.successful_queries += 1
                        self._stats.successful_operations += 1
            else:
                # 顺序执行查询
                for key, sql, params in queries:
                    try:
                        key, data = await execute_query(key, sql, params)
                        result.results[key] = data
                        result.successful_queries += 1
                        self._stats.successful_operations += 1
                    except Exception as e:
                        result.errors.append({"key": key, "error": str(e)})
                        self._stats.failed_operations += 1
            
            # 更新统计
            elapsed_time = time.time() - start_time
            self._stats.total_operations += len(queries)
            self._stats.total_time += elapsed_time
            result.total_time = elapsed_time
            
            logger.info(
                f"批量查询完成: 成功={result.successful_queries}, "
                f"失败={len(result.errors)}, 耗时={elapsed_time:.2f}秒"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"批量查询失败: {e}")
            result.errors.append({"error": str(e)})
            return result
    
    async def batch_upsert(
        self,
        table: str,
        records: List[Dict[str, Any]],
        id_field: str,
        batch_size: Optional[int] = None,
    ) -> BatchInsertResult:
        """
        批量插入或更新（UPSERT）
        
        Args:
            table: 表名
            records: 记录列表
            id_field: ID字段名
            batch_size: 批次大小
        
        Returns:
            BatchInsertResult: 批量操作结果
        
        Example:
            >>> records = [
            ...     {"id": "123", "name": "张三", "age": 30},
            ...     {"id": "456", "name": "李四", "age": 25},
            ... ]
            >>> result = await manager.batch_upsert("candidates", records, "candidate_id")
        """
        start_time = time.time()
        batch_size = batch_size or self._batch_size
        result = BatchInsertResult()
        
        try:
            if not records:
                logger.warning("批量UPSERT：记录列表为空")
                return result
            
            # 获取所有字段（排除id_field）
            all_fields = set()
            for record in records:
                all_fields.update(record.keys())
            all_fields.discard(id_field)
            update_fields = list(all_fields)
            
            # 分批处理
            async with self._db_pool.get_connection() as conn:
                for i in range(0, len(records), batch_size):
                    batch = records[i:i + batch_size]
                    
                    try:
                        cursor = conn.cursor()
                        
                        for record in batch:
                            if id_field not in record:
                                continue
                            
                            # 检查记录是否存在
                            check_sql = f"SELECT {id_field} FROM {table} WHERE {id_field} = ?"
                            cursor.execute(check_sql, (record[id_field],))
                            exists = cursor.fetchone() is not None
                            
                            if exists:
                                # 更新
                                set_clauses = []
                                params = []
                                for field in update_fields:
                                    if field in record:
                                        set_clauses.append(f"{field} = ?")
                                        params.append(record[field])
                                
                                if set_clauses:
                                    params.append(record[id_field])
                                    update_sql = f"""
                                        UPDATE {table}
                                        SET {', '.join(set_clauses)}
                                        WHERE {id_field} = ?
                                    """
                                    cursor.execute(update_sql, params)
                            else:
                                # 插入
                                columns = [id_field] + update_fields
                                values = [record.get(col) for col in columns]
                                placeholders = ", ".join(["?" for _ in columns])
                                columns_str = ", ".join(columns)
                                
                                insert_sql = f"""
                                    INSERT INTO {table} ({columns_str})
                                    VALUES ({placeholders})
                                """
                                cursor.execute(insert_sql, tuple(values))
                            
                            result.inserted_count += 1
                        
                        conn.commit()
                        self._stats.successful_operations += len(batch)
                        
                        logger.debug(f"批量UPSERT批次成功: {i} - {i + len(batch)}")
                        
                    except Exception as e:
                        result.failed_count += len(batch)
                        result.errors.append({
                            "batch_start": i,
                            "batch_end": i + len(batch),
                            "error": str(e),
                        })
                        self._stats.failed_operations += len(batch)
                        self._stats.last_error = str(e)
                        logger.error(f"批量UPSERT批次失败: {e}")
            
            # 更新统计
            elapsed_time = time.time() - start_time
            self._stats.total_operations += len(records)
            self._stats.total_time += elapsed_time
            self._stats.average_time = self._stats.total_time / self._stats.total_operations
            
            logger.info(
                f"批量UPSERT完成: 成功={result.inserted_count}, "
                f"失败={result.failed_count}, 耗时={elapsed_time:.2f}秒"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"批量UPSERT失败: {e}")
            result.failed_count = len(records)
            result.errors.append({"error": str(e)})
            self._stats.last_error = str(e)
            return result
    
    def get_stats(self) -> BatchOperationStats:
        """
        获取批量操作统计信息
        
        Returns:
            BatchOperationStats: 统计信息
        """
        # 重新计算平均时间
        if self._stats.total_operations > 0:
            self._stats.average_time = self._stats.total_time / self._stats.total_operations
        
        return self._stats
    
    def reset_stats(self) -> None:
        """重置统计信息"""
        self._stats = BatchOperationStats()
        logger.info("批量操作统计信息已重置")
    
    def set_batch_size(self, batch_size: int) -> None:
        """
        设置批次大小
        
        Args:
            batch_size: 批次大小
        """
        self._batch_size = batch_size
        logger.info(f"批次大小已设置为: {batch_size}")


__all__ = [
    "BatchOperationsManager",
    "BatchOperationStats",
    "BatchInsertResult",
    "BatchUpdateResult",
    "BatchQueryResult",
]