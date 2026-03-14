"""
通知模块

提供审核通知、系统通知等功能。
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """通知类型"""
    REVIEW_PENDING = "review_pending"  # 待审核通知
    REVIEW_APPROVED = "review_approved"  # 审核通过通知
    REVIEW_REJECTED = "review_rejected"  # 审核拒绝通知
    SYSTEM = "system"  # 系统通知


class NotificationPriority(Enum):
    """通知优先级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class NotificationChannel(Enum):
    """通知渠道"""
    IN_APP = "in_app"  # 应用内通知
    EMAIL = "email"  # 邮件通知
    SMS = "sms"  # 短信通知
    WECHAT = "wechat"  # 微信通知


class Notification:
    """通知类"""
    
    def __init__(
        self,
        notification_id: str,
        notification_type: NotificationType,
        title: str,
        content: str,
        recipient_id: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        channels: List[NotificationChannel] = None,
        metadata: Dict[str, Any] = None
    ):
        self.notification_id = notification_id
        self.type = notification_type
        self.title = title
        self.content = content
        self.recipient_id = recipient_id
        self.priority = priority
        self.channels = channels or [NotificationChannel.IN_APP]
        self.metadata = metadata or {}
        self.created_at = datetime.now().isoformat()
        self.sent_at = None
        self.read_at = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "notification_id": self.notification_id,
            "type": self.type.value,
            "title": self.title,
            "content": self.content,
            "recipient_id": self.recipient_id,
            "priority": self.priority.value,
            "channels": [c.value for c in self.channels],
            "metadata": self.metadata,
            "created_at": self.created_at,
            "sent_at": self.sent_at,
            "read_at": self.read_at
        }


class NotificationSender:
    """通知发送器"""
    
    def __init__(self, db_pool=None):
        """
        初始化通知发送器
        
        Args:
            db_pool: 数据库连接池
        """
        self.db_pool = db_pool
    
    async def send_notification(
        self,
        notification: Notification
    ) -> bool:
        """
        发送通知
        
        Args:
            notification: 通知对象
            
        Returns:
            是否发送成功
        """
        try:
            # 保存到数据库
            await self._save_notification(notification)
            
            # 根据渠道发送
            for channel in notification.channels:
                if channel == NotificationChannel.IN_APP:
                    await self._send_in_app(notification)
                elif channel == NotificationChannel.EMAIL:
                    await self._send_email(notification)
                elif channel == NotificationChannel.SMS:
                    await self._send_sms(notification)
                elif channel == NotificationChannel.WECHAT:
                    await self._send_wechat(notification)
            
            # 更新发送时间
            notification.sent_at = datetime.now().isoformat()
            await self._update_notification_sent_time(notification.notification_id)
            
            logger.info(f"通知发送成功: {notification.notification_id}")
            return True
            
        except Exception as e:
            logger.error(f"通知发送失败: {e}", exc_info=True)
            return False
    
    async def _save_notification(self, notification: Notification) -> None:
        """保存通知到数据库"""
        if not self.db_pool:
            logger.warning("数据库未初始化，跳过保存通知")
            return
        
        async with self.db_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO notifications (
                    notification_id, type, title, content,
                    recipient_id, priority, channels, metadata,
                    created_at, sent_at, read_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                notification.notification_id,
                notification.type.value,
                notification.title,
                notification.content,
                notification.recipient_id,
                notification.priority.value,
                ",".join([c.value for c in notification.channels]),
                str(notification.metadata),
                notification.created_at,
                notification.sent_at,
                notification.read_at
            ))
            
            conn.commit()
    
    async def _update_notification_sent_time(self, notification_id: str) -> None:
        """更新通知发送时间"""
        if not self.db_pool:
            return
        
        async with self.db_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE notifications
                SET sent_at = ?
                WHERE notification_id = ?
            """, (datetime.now().isoformat(), notification_id))
            
            conn.commit()
    
    async def _send_in_app(self, notification: Notification) -> None:
        """发送应用内通知"""
        # 应用内通知不需要实际发送，只需要保存到数据库
        # 前端会轮询获取通知
        logger.info(f"应用内通知: {notification.notification_id}")
    
    async def _send_email(self, notification: Notification) -> None:
        """发送邮件通知"""
        # TODO: 实现邮件发送
        # 可以使用 SMTP 或邮件服务API（如阿里云邮件推送、腾讯云邮件）
        logger.info(f"邮件通知: {notification.notification_id}")
        logger.warning("邮件发送功能尚未实现")
    
    async def _send_sms(self, notification: Notification) -> None:
        """发送短信通知"""
        # TODO: 实现短信发送
        # 可以使用短信服务API（如阿里云短信、腾讯云短信）
        logger.info(f"短信通知: {notification.notification_id}")
        logger.warning("短信发送功能尚未实现")
    
    async def _send_wechat(self, notification: Notification) -> None:
        """发送微信通知"""
        # TODO: 实现微信通知
        # 可以使用企业微信API或微信公众号API
        logger.info(f"微信通知: {notification.notification_id}")
        logger.warning("微信通知功能尚未实现")
    
    async def get_notifications(
        self,
        recipient_id: str,
        limit: int = 20,
        offset: int = 0,
        unread_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        获取用户通知列表
        
        Args:
            recipient_id: 接收人ID
            limit: 每页数量
            offset: 偏移量
            unread_only: 是否只获取未读通知
            
        Returns:
            通知列表
        """
        if not self.db_pool:
            return []
        
        try:
            async with self.db_pool.get_connection() as conn:
                cursor = conn.cursor()
                
                # 构建查询条件
                conditions = ["recipient_id = ?"]
                params = [recipient_id]
                
                if unread_only:
                    conditions.append("read_at IS NULL")
                
                where_clause = " AND ".join(conditions)
                params.extend([limit, offset])
                
                cursor.execute(f"""
                    SELECT notification_id, type, title, content,
                           recipient_id, priority, channels, metadata,
                           created_at, sent_at, read_at
                    FROM notifications
                    WHERE {where_clause}
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """, params)
                
                records = cursor.fetchall()
                
                return [
                    {
                        "notification_id": r[0],
                        "type": r[1],
                        "title": r[2],
                        "content": r[3],
                        "recipient_id": r[4],
                        "priority": r[5],
                        "channels": r[6].split(",") if r[6] else [],
                        "metadata": r[7],
                        "created_at": r[8],
                        "sent_at": r[9],
                        "read_at": r[10]
                    }
                    for r in records
                ]
                
        except Exception as e:
            logger.error(f"获取通知列表失败: {e}", exc_info=True)
            return []
    
    async def mark_as_read(self, notification_id: str) -> bool:
        """
        标记通知为已读
        
        Args:
            notification_id: 通知ID
            
        Returns:
            是否标记成功
        """
        if not self.db_pool:
            return False
        
        try:
            async with self.db_pool.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE notifications
                    SET read_at = ?
                    WHERE notification_id = ?
                """, (datetime.now().isoformat(), notification_id))
                
                conn.commit()
                
                logger.info(f"通知标记为已读: {notification_id}")
                return True
                
        except Exception as e:
            logger.error(f"标记通知为已读失败: {e}", exc_info=True)
            return False
    
    async def mark_all_as_read(self, recipient_id: str) -> bool:
        """
        标记所有通知为已读
        
        Args:
            recipient_id: 接收人ID
            
        Returns:
            是否标记成功
        """
        if not self.db_pool:
            return False
        
        try:
            async with self.db_pool.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE notifications
                    SET read_at = ?
                    WHERE recipient_id = ? AND read_at IS NULL
                """, (datetime.now().isoformat(), recipient_id))
                
                conn.commit()
                
                logger.info(f"标记所有通知为已读: {recipient_id}")
                return True
                
        except Exception as e:
            logger.error(f"标记所有通知为已读失败: {e}", exc_info=True)
            return False


class ReviewNotificationFactory:
    """审核通知工厂"""
    
    @staticmethod
    def create_pending_review_notification(
        candidate_id: str,
        candidate_name: str,
        reviewer_id: str
    ) -> Notification:
        """
        创建待审核通知
        
        Args:
            candidate_id: 候选人ID
            candidate_name: 候选人姓名
            reviewer_id: 审核人ID
            
        Returns:
            通知对象
        """
        import uuid
        
        return Notification(
            notification_id=str(uuid.uuid4()),
            notification_type=NotificationType.REVIEW_PENDING,
            title="新的待审核候选人",
            content=f"候选人 {candidate_name} 提交了信息，请及时审核。",
            recipient_id=reviewer_id,
            priority=NotificationPriority.HIGH,
            channels=[NotificationChannel.IN_APP, NotificationChannel.EMAIL],
            metadata={
                "candidate_id": candidate_id,
                "candidate_name": candidate_name,
                "action_url": f"/candidates/{candidate_id}/review"
            }
        )
    
    @staticmethod
    def create_approved_notification(
        candidate_id: str,
        candidate_name: str,
        submitter_id: str
    ) -> Notification:
        """
        创建审核通过通知
        
        Args:
            candidate_id: 候选人ID
            candidate_name: 候选人姓名
            submitter_id: 提交人ID
            
        Returns:
            通知对象
        """
        import uuid
        
        return Notification(
            notification_id=str(uuid.uuid4()),
            notification_type=NotificationType.REVIEW_APPROVED,
            title="审核通过",
            content=f"候选人 {candidate_name} 的信息已审核通过，已进入数据库。",
            recipient_id=submitter_id,
            priority=NotificationPriority.MEDIUM,
            channels=[NotificationChannel.IN_APP, NotificationChannel.SMS],
            metadata={
                "candidate_id": candidate_id,
                "candidate_name": candidate_name
            }
        )
    
    @staticmethod
    def create_rejected_notification(
        candidate_id: str,
        candidate_name: str,
        reviewer_comments: str,
        submitter_id: str
    ) -> Notification:
        """
        创建审核拒绝通知
        
        Args:
            candidate_id: 候选人ID
            candidate_name: 候选人姓名
            reviewer_comments: 审核意见
            submitter_id: 提交人ID
            
        Returns:
            通知对象
        """
        import uuid
        
        return Notification(
            notification_id=str(uuid.uuid4()),
            notification_type=NotificationType.REVIEW_REJECTED,
            title="审核未通过",
            content=f"候选人 {candidate_name} 的信息未通过审核。\n原因: {reviewer_comments}",
            recipient_id=submitter_id,
            priority=NotificationPriority.HIGH,
            channels=[NotificationChannel.IN_APP, NotificationChannel.EMAIL],
            metadata={
                "candidate_id": candidate_id,
                "candidate_name": candidate_name,
                "reviewer_comments": reviewer_comments
            }
        )