# SmartHire Core - 内核空间统一模型与工具库
# Version: 1.0.0
# Compliance: ARCH v2.0 | LAW v5.0 | MAP v7.0 | COMPOUND.md v3.0 | DIAGNOSIS.md v3.0

"""
SmartHire 核心模块
=================

本模块提供系统内核空间的统一数据模型和工具函数：
- FactModel: 统一事实模型（用于存储解析后的结构化数据）
- DecisionReport: 决策报告模型（用于存储系统决策结果）
- anchor_root(): 根路径锚定函数（LAW-ENV-002 合规）
- safe_write(): 原子写入协议（LAW-DATA-002 合规）
- encoding_cleaner(): 编码流清洗（ENV-03 合规）
- get_next_sequence_id(): 全局自增序列号（IPC-01 合规）
"""

import sys
from pathlib import Path
from typing import Optional

# ===== P0-1 修订: 首行调用 anchor_root() =====
# 根据 LAW-ENV-002 和 P0-1 修订要求，所有 __init__.py 首行必须调用 anchor_root()
from sh_core.utils import anchor_root

# 立即调用 anchor_root() 进行根路径锚定
_root_path = anchor_root()

# 导出核心类和函数
from sh_core.models import FactModel, DecisionReport
from sh_core.utils import safe_write, encoding_cleaner, get_next_sequence_id

# 导出向量数据库相关类
from sh_core.vector_pool import VectorDatabaseManager, VectorRecord
from sh_core.vector_cache import VectorSearchCache, CacheEntry

# 导出Redis缓存相关类
from sh_core.redis_cache import RedisCache, CacheConfig

# 导出批量操作相关类
from sh_core.batch_operations import (
    BatchOperationsManager,
    BatchOperationStats,
    BatchInsertResult,
    BatchUpdateResult,
    BatchQueryResult,
)

# 导出监控和告警相关类
from sh_core.metrics import (
    MetricType,
    MetricLabel,
    Metric,
    HistogramMetric,
    MetricsCollector,
    PerformanceTracker,
    track_duration,
    get_metrics_collector,
    get_performance_tracker,
)

from sh_core.alerting import (
    AlertSeverity,
    AlertStatus,
    Alert,
    AlertRule,
    AlertManager,
    AlertNotificationHandler,
    get_alert_manager,
)

__version__ = "1.0.0"
__author__ = "SmartHire Team"
__compliance__ = "ARCH v2.0 | LAW v5.0 | MAP v7.0 | COMPOUND.md v3.0 | DIAGNOSIS.md v3.0"


def get_root_path() -> Path:
    """
    获取项目根路径（已锚定）
    
    Returns:
        Path: 项目根路径
        
    Example:
        >>> from sh_core import get_root_path
        >>> root = get_root_path()
        >>> print(root)
        F:\\path\\to\\smarthire
    """
    return _root_path


__all__ = [
    # 数据模型
    'FactModel',
    'DecisionReport',
    
    # 工具函数
    'anchor_root',
    'safe_write',
    'encoding_cleaner',
    'get_next_sequence_id',
    'get_root_path',
    
    # 向量数据库
    'VectorDatabaseManager',
    'VectorRecord',
    'VectorSearchCache',
    'CacheEntry',
    
    # Redis缓存
    'RedisCache',
    'CacheConfig',
    
    # 批量操作
    'BatchOperationsManager',
    'BatchOperationStats',
    'BatchInsertResult',
    'BatchUpdateResult',
    'BatchQueryResult',
    
    # 监控和告警
    'MetricType',
    'MetricLabel',
    'Metric',
    'HistogramMetric',
    'MetricsCollector',
    'PerformanceTracker',
    'track_duration',
    'get_metrics_collector',
    'get_performance_tracker',
    'AlertSeverity',
    'AlertStatus',
    'Alert',
    'AlertRule',
    'AlertManager',
    'AlertNotificationHandler',
    'get_alert_manager',
    
    # 元数据
    '__version__',
    '__author__',
    '__compliance__',
]