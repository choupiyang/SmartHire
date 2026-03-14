"""
向量搜索缓存模块

提供向量搜索结果的缓存功能，减少重复查询的计算开销。
"""

import json
import hashlib
import asyncio
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from functools import wraps
import logging

from sh_core.errors import DatabaseError, ErrorCode

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    results: List[Dict[str, Any]]
    created_at: str
    expires_at: str
    hit_count: int = 0


class VectorSearchCache:
    """
    向量搜索缓存
    
    使用内存缓存存储搜索结果，支持TTL过期和LRU淘汰策略
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: int = 3600  # 默认1小时
    ) -> None:
        """
        初始化缓存
        
        Args:
            max_size: 最大缓存条目数
            default_ttl: 默认缓存有效期（秒）
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
        self._hit_count = 0
        self._miss_count = 0
        
        logger.info(f"向量搜索缓存初始化完成: max_size={max_size}, default_ttl={default_ttl}")
    
    def _generate_cache_key(
        self,
        query_vector: List[float],
        entity_type: str,
        top_k: int,
        min_similarity: float,
        filters: Optional[Dict[str, Any]]
    ) -> str:
        """
        生成缓存键
        
        Args:
            query_vector: 查询向量
            entity_type: 实体类型
            top_k: 返回结果数
            min_similarity: 最小相似度
            filters: 过滤条件
            
        Returns:
            缓存键
        """
        # 创建缓存参数字典
        cache_params = {
            "query_vector": query_vector[:10],  # 只取前10个维度作为键的一部分
            "entity_type": entity_type,
            "top_k": top_k,
            "min_similarity": min_similarity,
            "filters": sorted(filters.items()) if filters else None
        }
        
        # 序列化并生成哈希
        cache_str = json.dumps(cache_params, sort_keys=True)
        cache_key = hashlib.md5(cache_str.encode()).hexdigest()
        
        return cache_key
    
    async def get(
        self,
        query_vector: List[float],
        entity_type: str,
        top_k: int = 10,
        min_similarity: float = 0.0,
        filters: Optional[Dict[str, Any]] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        获取缓存结果
        
        Args:
            query_vector: 查询向量
            entity_type: 实体类型
            top_k: 返回结果数
            min_similarity: 最小相似度
            filters: 过滤条件
            
        Returns:
            缓存结果，如果未命中返回None
        """
        async with self._lock:
            cache_key = self._generate_cache_key(
                query_vector, entity_type, top_k, min_similarity, filters
            )
            
            entry = self._cache.get(cache_key)
            
            if entry is None:
                self._miss_count += 1
                return None
            
            # 检查是否过期
            expires_at = datetime.fromisoformat(entry.expires_at)
            if datetime.utcnow() > expires_at:
                # 删除过期条目
                del self._cache[cache_key]
                self._miss_count += 1
                return None
            
            # 更新命中计数
            entry.hit_count += 1
            self._hit_count += 1
            
            logger.debug(f"缓存命中: key={cache_key[:8]}, hit_count={entry.hit_count}")
            
            return entry.results
    
    async def set(
        self,
        query_vector: List[float],
        entity_type: str,
        results: List[Dict[str, Any]],
        top_k: int = 10,
        min_similarity: float = 0.0,
        filters: Optional[Dict[str, Any]] = None,
        ttl: Optional[int] = None
    ) -> bool:
        """
        设置缓存
        
        Args:
            query_vector: 查询向量
            entity_type: 实体类型
            results: 搜索结果
            top_k: 返回结果数
            min_similarity: 最小相似度
            filters: 过滤条件
            ttl: 缓存有效期（秒），None表示使用默认值
            
        Returns:
            是否成功设置
        """
        async with self._lock:
            # 如果缓存已满，执行LRU淘汰
            if len(self._cache) >= self.max_size:
                await self._evict_lru()
            
            cache_key = self._generate_cache_key(
                query_vector, entity_type, top_k, min_similarity, filters
            )
            
            # 计算过期时间
            ttl = ttl if ttl is not None else self.default_ttl
            expires_at = datetime.utcnow() + timedelta(seconds=ttl)
            
            # 创建缓存条目
            entry = CacheEntry(
                key=cache_key,
                results=results,
                created_at=datetime.utcnow().isoformat(),
                expires_at=expires_at.isoformat()
            )
            
            self._cache[cache_key] = entry
            
            logger.debug(f"缓存设置: key={cache_key[:8]}, ttl={ttl}")
            
            return True
    
    async def _evict_lru(self) -> None:
        """
        淘汰最少使用的缓存条目（LRU策略）
        """
        # 按命中计数排序，淘汰最少的
        sorted_entries = sorted(
            self._cache.items(),
            key=lambda x: x[1].hit_count
        )
        
        # 淘汰10%的条目
        evict_count = max(1, len(self._cache) // 10)
        for cache_key, _ in sorted_entries[:evict_count]:
            del self._cache[cache_key]
        
        logger.info(f"LRU淘汰: count={evict_count}")
    
    async def invalidate(
        self,
        entity_type: Optional[str] = None
    ) -> int:
        """
        使缓存失效
        
        Args:
            entity_type: 实体类型，None表示清除所有缓存
            
        Returns:
            清除的缓存条目数
        """
        async with self._lock:
            if entity_type is None:
                count = len(self._cache)
                self._cache.clear()
                logger.info(f"缓存清除: count={count}")
                return count
            
            # 只清除指定实体类型的缓存
            keys_to_delete = []
            for cache_key, entry in self._cache.items():
                # 通过键推断实体类型（键中包含entity_type）
                if entity_type in cache_key:
                    keys_to_delete.append(cache_key)
            
            for cache_key in keys_to_delete:
                del self._cache[cache_key]
            
            logger.info(f"缓存清除（按类型）: entity_type={entity_type}, count={len(keys_to_delete)}")
            
            return len(keys_to_delete)
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            统计信息
        """
        async with self._lock:
            total_entries = len(self._cache)
            total_hits = self._hit_count
            total_misses = self._miss_count
            total_requests = total_hits + total_misses
            
            hit_rate = total_hits / total_requests if total_requests > 0 else 0.0
            
            # 统计过期条目
            expired_count = 0
            now = datetime.utcnow()
            for entry in self._cache.values():
                expires_at = datetime.fromisoformat(entry.expires_at)
                if now > expires_at:
                    expired_count += 1
            
            # 统计命中次数分布
            hit_distribution = {}
            for entry in self._cache.values():
                hit_range = entry.hit_count
                hit_distribution[hit_range] = hit_distribution.get(hit_range, 0) + 1
            
            return {
                "max_size": self.max_size,
                "current_size": total_entries,
                "default_ttl": self.default_ttl,
                "hit_count": total_hits,
                "miss_count": total_misses,
                "total_requests": total_requests,
                "hit_rate": hit_rate,
                "expired_entries": expired_count,
                "hit_distribution": hit_distribution
            }
    
    async def clear_expired(self) -> int:
        """
        清除所有过期缓存条目
        
        Returns:
            清除的条目数
        """
        async with self._lock:
            now = datetime.utcnow()
            keys_to_delete = []
            
            for cache_key, entry in self._cache.items():
                expires_at = datetime.fromisoformat(entry.expires_at)
                if now > expires_at:
                    keys_to_delete.append(cache_key)
            
            for cache_key in keys_to_delete:
                del self._cache[cache_key]
            
            if keys_to_delete:
                logger.info(f"清除过期缓存: count={len(keys_to_delete)}")
            
            return len(keys_to_delete)


def cached_search(cache: VectorSearchCache) -> Callable:
    """
    向量搜索缓存装饰器
    
    Args:
        cache: 缓存实例
        
    Returns:
        装饰器函数
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(
            query_vector: List[float],
            entity_type: str,
            top_k: int = 10,
            min_similarity: float = 0.0,
            filters: Optional[Dict[str, Any]] = None
        ) -> List[Dict[str, Any]]:
            # 尝试从缓存获取
            cached_results = await cache.get(
                query_vector, entity_type, top_k, min_similarity, filters
            )
            
            if cached_results is not None:
                return cached_results
            
            # 缓存未命中，执行实际搜索
            results = await func(query_vector, entity_type, top_k, min_similarity, filters)
            
            # 将结果存入缓存
            if results:
                await cache.set(
                    query_vector, entity_type, results, top_k, min_similarity, filters
                )
            
            return results
        
        return wrapper
    return decorator