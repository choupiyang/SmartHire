"""
审核API路由

提供候选人审核相关的API。
"""

import logging
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from sh_core.database_pool import SQLiteConnectionPoolManager
from sh_core.async_communication import get_communication_layer, Layer
from sh_core.errors import ValidationError, DatabaseError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reviews", tags=["审核管理"])

# 数据库连接池
db_pool: Optional[SQLiteConnectionPoolManager] = None


def init_db_pool(pool: SQLiteConnectionPoolManager) -> None:
    """初始化数据库连接池"""
    global db_pool
    db_pool = pool


# Pydantic模型
class ReviewSubmit(BaseModel):
    """审核提交请求"""
    candidate_id: str = Field(..., description="候选人ID")
    reviewer_id: str = Field(..., description="审核人ID")
    decision: str = Field(..., description="审核决定: approved/rejected")
    comments: Optional[str] = Field(None, description="审核意见")
    alerts: Optional[List[str]] = Field(None, description="风险预警")


class ReviewQuery(BaseModel):
    """审核查询请求"""
    review_id: str = Field(..., description="审核记录ID")


class ReviewListQuery(BaseModel):
    """审核列表查询请求"""
    candidate_id: Optional[str] = Field(None, description="候选人ID")
    reviewer_id: Optional[str] = Field(None, description="审核人ID")
    status: Optional[str] = Field(None, description="状态: pending/approved/rejected")
    limit: int = Field(20, description="每页数量")
    offset: int = Field(0, description="偏移量")


class ReviewResponse(BaseModel):
    """审核响应"""
    review_id: str
    candidate_id: str
    reviewer_id: str
    status: str
    decision: Optional[str] = None
    comments: Optional[str] = None
    alerts: Optional[List[str]] = None
    created_at: str
    reviewed_at: Optional[str] = None


class ReviewListResponse(BaseModel):
    """审核列表响应"""
    total: int
    reviews: List[ReviewResponse]


@router.post("/submit", response_model=dict)
async def submit_review(request: ReviewSubmit) -> dict:
    """
    提交审核
    
    Args:
        request: 审核提交请求
        
    Returns:
        审核结果
    """
    if not db_pool:
        raise HTTPException(status_code=500, detail="数据库未初始化")
    
    try:
        # 验证审核决定
        if request.decision not in ["approved", "rejected"]:
            raise ValidationError(
                error_code="WEB-VALIDATION-001",
                message="审核决定必须是approved或rejected"
            )
        
        # 获取数据库连接
        async with db_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # 查询候选人信息
            cursor.execute(
                "SELECT name, phone, status FROM candidates WHERE candidate_id = ?",
                (request.candidate_id,)
            )
            candidate = cursor.fetchone()
            
            if not candidate:
                raise HTTPException(status_code=404, detail="候选人不存在")
            
            candidate_name, candidate_phone, candidate_status = candidate
            
            # 检查候选人状态
            if candidate_status != "pending_review":
                raise HTTPException(
                    status_code=400,
                    detail=f"候选人状态不允许审核: {candidate_status}"
                )
            
            # 生成审核记录ID
            import uuid
            review_id = str(uuid.uuid4())
            created_at = datetime.now().isoformat()
            reviewed_at = datetime.now().isoformat()
            
            # 插入审核记录
            cursor.execute("""
                INSERT INTO candidate_review (
                    review_id, candidate_id, reviewer_id, status,
                    decision, comments, alerts, created_at, reviewed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                review_id,
                request.candidate_id,
                request.reviewer_id,
                "completed",
                request.decision,
                request.comments,
                ",".join(request.alerts) if request.alerts else None,
                created_at,
                reviewed_at
            ))
            
            # 更新候选人状态
            new_status = "approved" if request.decision == "approved" else "rejected"
            cursor.execute(
                "UPDATE candidates SET status = ?, updated_at = ? WHERE candidate_id = ?",
                (new_status, reviewed_at, request.candidate_id)
            )
            
            # 记录操作日志
            cursor.execute("""
                INSERT INTO operation_logs (
                    log_id, entity_type, entity_id, action,
                    user_id, details, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                "candidate",
                request.candidate_id,
                "review",
                request.reviewer_id,
                f"审核决定: {request.decision}, 意见: {request.comments}",
                reviewed_at
            ))
            
            conn.commit()
            
            return {
                "success": True,
                "message": "审核提交成功",
                "data": {
                    "review_id": review_id,
                    "candidate_id": request.candidate_id,
                    "candidate_name": candidate_name,
                    "candidate_phone": candidate_phone,
                    "status": new_status,
                    "decision": request.decision,
                    "reviewed_at": reviewed_at
                }
            }
            
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"审核提交失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/query", response_model=ReviewResponse)
async def query_review(review_id: str = Query(..., description="审核记录ID")) -> ReviewResponse:
    """
    查询审核记录
    
    Args:
        review_id: 审核记录ID
        
    Returns:
        审核记录
    """
    if not db_pool:
        raise HTTPException(status_code=500, detail="数据库未初始化")
    
    try:
        async with db_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT review_id, candidate_id, reviewer_id, status,
                       decision, comments, alerts, created_at, reviewed_at
                FROM candidate_review
                WHERE review_id = ?
            """, (review_id,))
            
            record = cursor.fetchone()
            
            if not record:
                raise HTTPException(status_code=404, detail="审核记录不存在")
            
            review_id, candidate_id, reviewer_id, status, decision, comments, alerts, created_at, reviewed_at = record
            
            return ReviewResponse(
                review_id=review_id,
                candidate_id=candidate_id,
                reviewer_id=reviewer_id,
                status=status,
                decision=decision,
                comments=comments,
                alerts=alerts.split(",") if alerts else None,
                created_at=created_at,
                reviewed_at=reviewed_at
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询审核记录失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=ReviewListResponse)
async def list_reviews(
    candidate_id: Optional[str] = Query(None, description="候选人ID"),
    reviewer_id: Optional[str] = Query(None, description="审核人ID"),
    status: Optional[str] = Query(None, description="状态"),
    limit: int = Query(20, description="每页数量"),
    offset: int = Query(0, description="偏移量")
):
    """
    查询审核列表
    
    Args:
        candidate_id: 候选人ID
        reviewer_id: 审核人ID
        status: 状态
        limit: 每页数量
        offset: 偏移量
        
    Returns:
        审核列表
    """
    if not db_pool:
        raise HTTPException(status_code=500, detail="数据库未初始化")
    
    try:
        # 构建查询条件
        conditions = []
        params = []
        
        if candidate_id:
            conditions.append("candidate_id = ?")
            params.append(candidate_id)
        
        if reviewer_id:
            conditions.append("reviewer_id = ?")
            params.append(reviewer_id)
        
        if status:
            conditions.append("status = ?")
            params.append(status)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        async with db_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # 查询总数
            cursor.execute(f"""
                SELECT COUNT(*) FROM candidate_review
                WHERE {where_clause}
            """, params)
            total = cursor.fetchone()[0]
            
            # 查询列表
            params.append(limit)
            params.append(offset)
            
            cursor.execute(f"""
                SELECT review_id, candidate_id, reviewer_id, status,
                       decision, comments, alerts, created_at, reviewed_at
                FROM candidate_review
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, params)
            
            records = cursor.fetchall()
            
            reviews = [
                ReviewResponse(
                    review_id=r[0],
                    candidate_id=r[1],
                    reviewer_id=r[2],
                    status=r[3],
                    decision=r[4],
                    comments=r[5],
                    alerts=r[6].split(",") if r[6] else None,
                    created_at=r[7],
                    reviewed_at=r[8]
                )
                for r in records
            ]
            
            return ReviewListResponse(
                total=total,
                reviews=reviews
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询审核列表失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_review_history(
    candidate_id: str = Query(..., description="候选人ID")
):
    """
    获取候选人审核历史
    
    Args:
        candidate_id: 候选人ID
        
    Returns:
        审核历史
    """
    if not db_pool:
        raise HTTPException(status_code=500, detail="数据库未初始化")
    
    try:
        async with db_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # 查询审核记录
            cursor.execute("""
                SELECT review_id, candidate_id, reviewer_id, status,
                       decision, comments, alerts, created_at, reviewed_at
                FROM candidate_review
                WHERE candidate_id = ?
                ORDER BY created_at DESC
            """, (candidate_id,))
            
            records = cursor.fetchall()
            
            # 查询操作日志
            cursor.execute("""
                SELECT log_id, action, user_id, details, created_at
                FROM operation_logs
                WHERE entity_type = 'candidate' AND entity_id = ?
                ORDER BY created_at DESC
            """, (candidate_id,))
            
            logs = cursor.fetchall()
            
            return {
                "success": True,
                "data": {
                    "reviews": [
                        {
                            "review_id": r[0],
                            "candidate_id": r[1],
                            "reviewer_id": r[2],
                            "status": r[3],
                            "decision": r[4],
                            "comments": r[5],
                            "alerts": r[6].split(",") if r[6] else None,
                            "created_at": r[7],
                            "reviewed_at": r[8]
                        }
                        for r in records
                    ],
                    "logs": [
                        {
                            "log_id": log[0],
                            "action": log[1],
                            "user_id": log[2],
                            "details": log[3],
                            "created_at": log[4]
                        }
                        for log in logs
                    ]
                }
            }
            
    except Exception as e:
        logger.error(f"获取审核历史失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_review_stats() -> dict:
    """
    获取审核统计信息
    
    Returns:
        审核统计
    """
    if not db_pool:
        raise HTTPException(status_code=500, detail="数据库未初始化")
    
    try:
        async with db_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # 统计待审核数量
            cursor.execute("""
                SELECT COUNT(*) FROM candidates
                WHERE status = 'pending_review'
            """)
            pending_count = cursor.fetchone()[0]
            
            # 统计今日审核数量
            today = datetime.now().strftime("%Y-%m-%d")
            cursor.execute("""
                SELECT COUNT(*) FROM candidate_review
                WHERE reviewed_at >= ?
            """, (today,))
            today_reviewed_count = cursor.fetchone()[0]
            
            # 统计审核通过率
            cursor.execute("""
                SELECT
                    SUM(CASE WHEN decision = 'approved' THEN 1 ELSE 0 END) as approved,
                    SUM(CASE WHEN decision = 'rejected' THEN 1 ELSE 0 END) as rejected
                FROM candidate_review
                WHERE status = 'completed'
            """)
            approved, rejected = cursor.fetchone()
            
            approval_rate = (
                approved / (approved + rejected) * 100
                if (approved + rejected) > 0 else 0
            )
            
            return {
                "success": True,
                "data": {
                    "pending_count": pending_count,
                    "today_reviewed_count": today_reviewed_count,
                    "approved_count": approved or 0,
                    "rejected_count": rejected or 0,
                    "approval_rate": round(approval_rate, 2)
                }
            }
            
    except Exception as e:
        logger.error(f"获取审核统计失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))