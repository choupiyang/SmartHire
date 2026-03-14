"""
文件上传API路由

提供文件上传、下载、删除等功能。
"""

import logging
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from sh_core.file_manager import FileManager
from sh_core.cdn_client import CDNClient, create_cdn_client_from_env
from sh_core.errors import FileOperationError
from sh_core.async_communication import get_communication_layer, Layer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/files", tags=["文件管理"])

# 初始化文件管理器
file_manager = FileManager()

# 初始化CDN客户端
cdn_client: Optional[CDNClient] = None


async def init_cdn_client() -> None:
    """初始化CDN客户端"""
    global cdn_client
    try:
        cdn_client = await create_cdn_client_from_env()
        if cdn_client:
            logger.info("CDN客户端初始化成功")
        else:
            logger.info("CDN客户端未配置")
    except Exception as e:
        logger.error(f"CDN客户端初始化失败: {e}", exc_info=True)


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    upload_to_cdn: bool = Form(False)
):
    """
    上传文件
    
    Args:
        file: 上传的文件
        upload_to_cdn: 是否上传到CDN
        
    Returns:
        上传结果
    """
    try:
        # 保存文件到本地
        local_path = await file_manager.save_uploaded_file(file)
        
        # 如果需要上传到CDN
        cdn_url = None
        if upload_to_cdn and cdn_client:
            # 上传到CDN
            cdn_url = await cdn_client.upload_file(local_path)
            
            # 删除本地文件
            await file_manager.delete_file(local_path)
        
        return {
            "success": True,
            "message": "文件上传成功",
            "data": {
                "local_path": local_path,
                "cdn_url": cdn_url,
                "file_name": file.filename,
                "file_size": await file_manager.get_file_size(local_path)
            }
        }
        
    except FileOperationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error(f"文件上传失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    upload_to_cdn: bool = Form(False)
):
    """
    上传图片
    
    Args:
        file: 上传的图片
        upload_to_cdn: 是否上传到CDN
        
    Returns:
        上传结果
    """
    try:
        # 验证文件类型
        if file.content_type not in file_manager.allowed_image_types:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的图片类型: {file.content_type}"
            )
        
        # 保存文件
        local_path = await file_manager.save_uploaded_file(
            file,
            max_size=5 * 1024 * 1024  # 5MB
        )
        
        # 如果需要上传到CDN
        cdn_url = None
        if upload_to_cdn and cdn_client:
            # 上传到CDN
            cdn_url = await cdn_client.upload_file(local_path)
            
            # 删除本地文件
            await file_manager.delete_file(local_path)
        
        return {
            "success": True,
            "message": "图片上传成功",
            "data": {
                "local_path": local_path,
                "cdn_url": cdn_url,
                "file_name": file.filename,
                "file_size": await file_manager.get_file_size(local_path)
            }
        }
        
    except HTTPException:
        raise
    except FileOperationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error(f"图片上传失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-document")
async def upload_document(
    file: UploadFile = File(...),
    upload_to_cdn: bool = Form(False)
):
    """
    上传文档
    
    Args:
        file: 上传的文档
        upload_to_cdn: 是否上传到CDN
        
    Returns:
        上传结果
    """
    try:
        # 验证文件类型
        if file.content_type not in file_manager.allowed_file_types:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文档类型: {file.content_type}"
            )
        
        # 保存文件
        local_path = await file_manager.save_uploaded_file(
            file,
            max_size=10 * 1024 * 1024  # 10MB
        )
        
        # 如果需要上传到CDN
        cdn_url = None
        if upload_to_cdn and cdn_client:
            # 上传到CDN
            cdn_url = await cdn_client.upload_file(local_path)
            
            # 删除本地文件
            await file_manager.delete_file(local_path)
        
        return {
            "success": True,
            "message": "文档上传成功",
            "data": {
                "local_path": local_path,
                "cdn_url": cdn_url,
                "file_name": file.filename,
                "file_size": await file_manager.get_file_size(local_path)
            }
        }
        
    except HTTPException:
        raise
    except FileOperationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error(f"文档上传失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete")
async def delete_file(
    file_path: str
):
    """
    删除文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        删除结果
    """
    try:
        success = await file_manager.delete_file(file_path)
        
        if not success:
            raise HTTPException(status_code=404, detail="文件不存在或删除失败")
        
        return {
            "success": True,
            "message": "文件删除成功",
            "data": {
                "file_path": file_path
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文件删除失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
async def get_file_info(
    file_path: str
):
    """
    获取文件信息
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件信息
    """
    try:
        file_size = await file_manager.get_file_size(file_path)
        
        return {
            "success": True,
            "data": {
                "file_path": file_path,
                "file_size": file_size
            }
        }
        
    except FileOperationError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        logger.error(f"获取文件信息失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))