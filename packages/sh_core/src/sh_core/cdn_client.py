"""
CDN客户端模块

提供文件上传到CDN的功能，支持多个CDN提供商。
"""

import os
import logging
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

from sh_core.errors import FileOperationError, ErrorCode

logger = logging.getLogger(__name__)


class CDNProvider(ABC):
    """CDN提供商抽象基类"""
    
    @abstractmethod
    async def upload_file(
        self,
        file_path: str,
        object_name: str
    ) -> str:
        """
        上传文件到CDN
        
        Args:
            file_path: 本地文件路径
            object_name: CDN对象名称
            
        Returns:
            CDN URL
        """
        pass
    
    @abstractmethod
    async def delete_file(self, object_name: str) -> bool:
        """
        删除CDN文件
        
        Args:
            object_name: CDN对象名称
            
        Returns:
            是否成功删除
        """
        pass
    
    @abstractmethod
    def get_file_url(self, object_name: str) -> str:
        """
        获取文件URL
        
        Args:
            object_name: CDN对象名称
            
        Returns:
            文件URL
        """
        pass


class AliyunOSSProvider(CDNProvider):
    """阿里云OSS提供商"""
    
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        bucket: str,
        endpoint: str = "oss-cn-hangzhou.aliyuncs.com",
        cdn_domain: Optional[str] = None
    ) -> None:
        """
        初始化阿里云OSS提供商
        
        Args:
            access_key: 访问密钥
            secret_key: 密钥
            bucket: 存储桶名称
            endpoint: 端点
            cdn_domain: CDN域名（可选）
        """
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket = bucket
        self.endpoint = endpoint
        self.cdn_domain = cdn_domain
        
        # 延迟导入oss2（因为可能未安装）
        self._oss2 = None
        self._auth = None
        self._bucket = None
        
        logger.info("阿里云OSS提供商初始化完成")
    
    def _init_sdk(self) -> None:
        """初始化SDK"""
        if self._oss2 is None:
            try:
                import oss2
                self._oss2 = oss2
                
                # 创建认证
                self._auth = oss2.Auth(self.access_key, self.secret_key)
                
                # 创建Bucket对象
                self._bucket = self._oss2.Bucket(
                    self._auth,
                    f"https://{self.bucket}.{self.endpoint}"
                )
                
                logger.info("阿里云OSS SDK初始化成功")
                
            except ImportError:
                logger.warning("oss2未安装，阿里云OSS功能将不可用")
            except Exception as e:
                logger.error(f"阿里云OSS SDK初始化失败: {e}", exc_info=True)
    
    async def upload_file(
        self,
        file_path: str,
        object_name: str
    ) -> str:
        """
        上传文件到阿里云OSS
        
        Args:
            file_path: 本地文件路径
            object_name: OSS对象名称
            
        Returns:
            OSS URL
        """
        self._init_sdk()
        
        if self._bucket is None:
            raise FileOperationError(
                error_code=ErrorCode.SH_CDN_INIT_001,
                message="阿里云OSS SDK未初始化"
            )
        
        try:
            # 上传文件
            self._bucket.put_object_from_file(object_name, file_path)
            
            # 生成URL
            url = self.get_file_url(object_name)
            
            logger.info(f"文件上传成功: {object_name} -> {url}")
            
            return url
            
        except Exception as e:
            logger.error(f"文件上传失败: {e}", exc_info=True)
            raise FileOperationError(
                error_code=ErrorCode.SH_CDN_UPLOAD_001,
                message=f"文件上传失败: {str(e)}"
            )
    
    async def delete_file(self, object_name: str) -> bool:
        """
        删除OSS文件
        
        Args:
            object_name: OSS对象名称
            
        Returns:
            是否成功删除
        """
        self._init_sdk()
        
        if self._bucket is None:
            return False
        
        try:
            self._bucket.delete_object(object_name)
            
            logger.info(f"文件删除成功: {object_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"文件删除失败: {e}", exc_info=True)
            return False
    
    def get_file_url(self, object_name: str) -> str:
        """
        获取文件URL
        
        Args:
            object_name: OSS对象名称
            
        Returns:
            文件URL
        """
        if self.cdn_domain:
            # 使用CDN域名
            return f"https://{self.cdn_domain}/{object_name}"
        else:
            # 使用OSS域名
            return f"https://{self.bucket}.{self.endpoint}/{object_name}"


class TencentCOSProvider(CDNProvider):
    """腾讯云COS提供商"""
    
    def __init__(
        self,
        secret_id: str,
        secret_key: str,
        bucket: str,
        region: str = "ap-guangzhou",
        cdn_domain: Optional[str] = None
    ) -> None:
        """
        初始化腾讯云COS提供商
        
        Args:
            secret_id: 密钥ID
            secret_key: 密钥
            bucket: 存储桶名称（格式：bucket-name-appid）
            region: 区域
            cdn_domain: CDN域名（可选）
        """
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.bucket = bucket
        self.region = region
        self.cdn_domain = cdn_domain
        
        # 延迟导入cos-python-sdk-v5
        self._cos = None
        self._client = None
        
        logger.info("腾讯云COS提供商初始化完成")
    
    def _init_sdk(self) -> None:
        """初始化SDK"""
        if self._cos is None:
            try:
                from qcloud_cos import CosConfig, CosS3Client
                self._cos = (CosConfig, CosS3Client)
                
                # 创建配置
                config = CosConfig(
                    Region=self.region,
                    SecretId=self.secret_id,
                    SecretKey=self.secret_key
                )
                
                # 创建客户端
                self._client = CosS3Client(config)
                
                logger.info("腾讯云COS SDK初始化成功")
                
            except ImportError:
                logger.warning("cos-python-sdk-v5未安装，腾讯云COS功能将不可用")
            except Exception as e:
                logger.error(f"腾讯云COS SDK初始化失败: {e}", exc_info=True)
    
    async def upload_file(
        self,
        file_path: str,
        object_name: str
    ) -> str:
        """
        上传文件到腾讯云COS
        
        Args:
            file_path: 本地文件路径
            object_name: COS对象名称
            
        Returns:
            COS URL
        """
        self._init_sdk()
        
        if self._client is None:
            raise FileOperationError(
                error_code=ErrorCode.SH_CDN_INIT_001,
                message="腾讯云COS SDK未初始化"
            )
        
        try:
            # 上传文件
            with open(file_path, 'rb') as f:
                self._client.put_object(
                    Bucket=self.bucket,
                    Body=f,
                    Key=object_name
                )
            
            # 生成URL
            url = self.get_file_url(object_name)
            
            logger.info(f"文件上传成功: {object_name} -> {url}")
            
            return url
            
        except Exception as e:
            logger.error(f"文件上传失败: {e}", exc_info=True)
            raise FileOperationError(
                error_code=ErrorCode.SH_CDN_UPLOAD_001,
                message=f"文件上传失败: {str(e)}"
            )
    
    async def delete_file(self, object_name: str) -> bool:
        """
        删除COS文件
        
        Args:
            object_name: COS对象名称
            
        Returns:
            是否成功删除
        """
        self._init_sdk()
        
        if self._client is None:
            return False
        
        try:
            self._client.delete_object(
                Bucket=self.bucket,
                Key=object_name
            )
            
            logger.info(f"文件删除成功: {object_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"文件删除失败: {e}", exc_info=True)
            return False
    
    def get_file_url(self, object_name: str) -> str:
        """
        获取文件URL
        
        Args:
            object_name: COS对象名称
            
        Returns:
            文件URL
        """
        if self.cdn_domain:
            # 使用CDN域名
            return f"https://{self.cdn_domain}/{object_name}"
        else:
            # 使用COS域名
            return f"https://{self.bucket}.cos.{self.region}.myqcloud.com/{object_name}"


class CDNClient:
    """
    CDN客户端
    
    支持多个CDN提供商的统一接口
    """
    
    def __init__(
        self,
        provider: str = "aliyun",
        **kwargs
    ) -> None:
        """
        初始化CDN客户端
        
        Args:
            provider: CDN提供商（aliyun/tencent/qiniu）
            **kwargs: CDN提供商特定参数
        """
        self.provider = provider
        self._provider_impl: Optional[CDNProvider] = None
        
        # 初始化提供商实现
        if provider == "aliyun":
            self._provider_impl = AliyunOSSProvider(
                access_key=kwargs.get("access_key", ""),
                secret_key=kwargs.get("secret_key", ""),
                bucket=kwargs.get("bucket", ""),
                endpoint=kwargs.get("endpoint", "oss-cn-hangzhou.aliyuncs.com"),
                cdn_domain=kwargs.get("cdn_domain")
            )
        elif provider == "tencent":
            self._provider_impl = TencentCOSProvider(
                secret_id=kwargs.get("secret_id", ""),
                secret_key=kwargs.get("secret_key", ""),
                bucket=kwargs.get("bucket", ""),
                region=kwargs.get("region", "ap-guangzhou"),
                cdn_domain=kwargs.get("cdn_domain")
            )
        else:
            raise ValueError(f"不支持的CDN提供商: {provider}")
        
        logger.info(f"CDN客户端初始化完成: provider={provider}")
    
    async def upload_file(
        self,
        file_path: str,
        object_name: Optional[str] = None
    ) -> str:
        """
        上传文件到CDN
        
        Args:
            file_path: 本地文件路径
            object_name: CDN对象名称（可选，默认使用文件名）
            
        Returns:
            CDN URL
        """
        if object_name is None:
            # 使用文件名作为对象名
            import os
            object_name = os.path.basename(file_path)
        
        return await self._provider_impl.upload_file(file_path, object_name)
    
    async def delete_file(self, object_name: str) -> bool:
        """
        删除CDN文件
        
        Args:
            object_name: CDN对象名称
            
        Returns:
            是否成功删除
        """
        return await self._provider_impl.delete_file(object_name)
    
    def get_file_url(self, object_name: str) -> str:
        """
        获取文件URL
        
        Args:
            object_name: CDN对象名称
            
        Returns:
            文件URL
        """
        return self._provider_impl.get_file_url(object_name)


async def create_cdn_client_from_env() -> Optional[CDNClient]:
    """
    从环境变量创建CDN客户端
    
    Returns:
        CDN客户端（如果配置了环境变量）
    """
    provider = os.getenv("CDN_PROVIDER", "")
    
    if not provider:
        return None
    
    kwargs = {}
    
    if provider == "aliyun":
        kwargs["access_key"] = os.getenv("ALIYUN_ACCESS_KEY", "")
        kwargs["secret_key"] = os.getenv("ALIYUN_SECRET_KEY", "")
        kwargs["bucket"] = os.getenv("ALIYUN_BUCKET", "")
        kwargs["endpoint"] = os.getenv("ALIYUN_ENDPOINT", "oss-cn-hangzhou.aliyuncs.com")
        kwargs["cdn_domain"] = os.getenv("ALIYUN_CDN_DOMAIN")
    elif provider == "tencent":
        kwargs["secret_id"] = os.getenv("TENCENT_SECRET_ID", "")
        kwargs["secret_key"] = os.getenv("TENCENT_SECRET_KEY", "")
        kwargs["bucket"] = os.getenv("TENCENT_BUCKET", "")
        kwargs["region"] = os.getenv("TENCENT_REGION", "ap-guangzhou")
        kwargs["cdn_domain"] = os.getenv("TENCENT_CDN_DOMAIN")
    else:
        logger.warning(f"不支持的CDN提供商: {provider}")
        return None
    
    return CDNClient(provider=provider, **kwargs)