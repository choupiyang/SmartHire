"""
权限控制模块

提供基于角色的访问控制（RBAC）。
"""

import logging
from typing import Dict, List, Optional, Set
from enum import Enum
from functools import wraps

logger = logging.getLogger(__name__)


class Role(Enum):
    """角色"""
    ADMIN = "admin"  # 管理员
    REVIEWER = "reviewer"  # 审核人
    USER = "user"  # 普通用户


class Permission(Enum):
    """权限"""
    # 候选人相关
    CANDIDATE_CREATE = "candidate:create"  # 创建候选人
    CANDIDATE_READ = "candidate:read"  # 查看候选人
    CANDIDATE_UPDATE = "candidate:update"  # 更新候选人
    CANDIDATE_DELETE = "candidate:delete"  # 删除候选人
    
    # 审核相关
    REVIEW_SUBMIT = "review:submit"  # 提交审核
    REVIEW_APPROVE = "review:approve"  # 审核通过
    REVIEW_REJECT = "review:reject"  # 审核拒绝
    REVIEW_QUERY = "review:query"  # 查询审核
    
    # 招募相关
    RECRUITMENT_GENERATE = "recruitment:generate"  # 生成招募内容
    
    # 匹配相关
    MATCHING_QUERY = "matching:query"  # 查询匹配结果
    
    # 文件相关
    FILE_UPLOAD = "file:upload"  # 上传文件
    FILE_DELETE = "file:delete"  # 删除文件
    
    # 用户相关
    USER_MANAGE = "user:manage"  # 管理用户


# 角色权限映射
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.ADMIN: {
        # 管理员拥有所有权限
        Permission.CANDIDATE_CREATE,
        Permission.CANDIDATE_READ,
        Permission.CANDIDATE_UPDATE,
        Permission.CANDIDATE_DELETE,
        Permission.REVIEW_SUBMIT,
        Permission.REVIEW_APPROVE,
        Permission.REVIEW_REJECT,
        Permission.REVIEW_QUERY,
        Permission.RECRUITMENT_GENERATE,
        Permission.MATCHING_QUERY,
        Permission.FILE_UPLOAD,
        Permission.FILE_DELETE,
        Permission.USER_MANAGE,
    },
    Role.REVIEWER: {
        # 审核人拥有审核和查询权限
        Permission.CANDIDATE_READ,
        Permission.REVIEW_SUBMIT,
        Permission.REVIEW_APPROVE,
        Permission.REVIEW_REJECT,
        Permission.REVIEW_QUERY,
        Permission.RECRUITMENT_GENERATE,
        Permission.MATCHING_QUERY,
        Permission.FILE_UPLOAD,
    },
    Role.USER: {
        # 普通用户拥有基础权限
        Permission.CANDIDATE_CREATE,
        Permission.CANDIDATE_READ,
        Permission.RECRUITMENT_GENERATE,
        Permission.MATCHING_QUERY,
        Permission.FILE_UPLOAD,
    }
}


class User:
    """用户类"""
    
    def __init__(
        self,
        user_id: str,
        username: str,
        role: Role,
        metadata: Dict = None
    ):
        self.user_id = user_id
        self.username = username
        self.role = role
        self.metadata = metadata or {}
    
    def has_permission(self, permission: Permission) -> bool:
        """
        检查用户是否有权限
        
        Args:
            permission: 权限
            
        Returns:
            是否有权限
        """
        return permission in ROLE_PERMISSIONS[self.role]
    
    def has_any_permission(self, permissions: List[Permission]) -> bool:
        """
        检查用户是否有任意权限
        
        Args:
            permissions: 权限列表
            
        Returns:
            是否有任意权限
        """
        return any(p in ROLE_PERMISSIONS[self.role] for p in permissions)
    
    def has_all_permissions(self, permissions: List[Permission]) -> bool:
        """
        检查用户是否有所有权限
        
        Args:
            permissions: 权限列表
            
        Returns:
            是否有所有权限
        """
        return all(p in ROLE_PERMISSIONS[self.role] for p in permissions)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "role": self.role.value,
            "permissions": [p.value for p in ROLE_PERMISSIONS[self.role]],
            "metadata": self.metadata
        }


class PermissionChecker:
    """权限检查器"""
    
    def __init__(self):
        self._users: Dict[str, User] = {}
    
    def add_user(self, user: User) -> None:
        """
        添加用户
        
        Args:
            user: 用户对象
        """
        self._users[user.user_id] = user
        logger.info(f"添加用户: {user.username} ({user.role.value})")
    
    def get_user(self, user_id: str) -> Optional[User]:
        """
        获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户对象
        """
        return self._users.get(user_id)
    
    def check_permission(
        self,
        user_id: str,
        permission: Permission
    ) -> bool:
        """
        检查用户权限
        
        Args:
            user_id: 用户ID
            permission: 权限
            
        Returns:
            是否有权限
        """
        user = self.get_user(user_id)
        if not user:
            logger.warning(f"用户不存在: {user_id}")
            return False
        
        return user.has_permission(permission)
    
    def check_any_permission(
        self,
        user_id: str,
        permissions: List[Permission]
    ) -> bool:
        """
        检查用户是否有任意权限
        
        Args:
            user_id: 用户ID
            permissions: 权限列表
            
        Returns:
            是否有任意权限
        """
        user = self.get_user(user_id)
        if not user:
            logger.warning(f"用户不存在: {user_id}")
            return False
        
        return user.has_any_permission(permissions)
    
    def check_all_permissions(
        self,
        user_id: str,
        permissions: List[Permission]
    ) -> bool:
        """
        检查用户是否有所有权限
        
        Args:
            user_id: 用户ID
            permissions: 权限列表
            
        Returns:
            是否有所有权限
        """
        user = self.get_user(user_id)
        if not user:
            logger.warning(f"用户不存在: {user_id}")
            return False
        
        return user.has_all_permissions(permissions)


# 全局权限检查器实例
_permission_checker: Optional[PermissionChecker] = None


def init_permission_checker() -> PermissionChecker:
    """
    初始化权限检查器
    
    Returns:
        权限检查器实例
    """
    global _permission_checker
    _permission_checker = PermissionChecker()
    
    # 添加默认管理员
    admin_user = User(
        user_id="admin",
        username="admin",
        role=Role.ADMIN
    )
    _permission_checker.add_user(admin_user)
    
    logger.info("权限检查器初始化完成")
    return _permission_checker


def get_permission_checker() -> PermissionChecker:
    """
    获取权限检查器
    
    Returns:
        权限检查器实例
        
    Raises:
        RuntimeError: 权限检查器未初始化
    """
    if _permission_checker is None:
        raise RuntimeError("权限检查器未初始化")
    return _permission_checker


# 便捷函数
def check_permission(user_id: str, permission: Permission) -> bool:
    """
    检查用户权限（便捷函数）
    
    Args:
        user_id: 用户ID
        permission: 权限
        
    Returns:
        是否有权限
    """
    checker = get_permission_checker()
    return checker.check_permission(user_id, permission)


def check_any_permission(user_id: str, permissions: List[Permission]) -> bool:
    """
    检查用户是否有任意权限（便捷函数）
    
    Args:
        user_id: 用户ID
        permissions: 权限列表
        
    Returns:
        是否有任意权限
    """
    checker = get_permission_checker()
    return checker.check_any_permission(user_id, permissions)


def check_all_permissions(user_id: str, permissions: List[Permission]) -> bool:
    """
    检查用户是否有所有权限（便捷函数）
    
    Args:
        user_id: 用户ID
        permissions: 权限列表
        
    Returns:
        是否有所有权限
    """
    checker = get_permission_checker()
    return checker.check_all_permissions(user_id, permissions)