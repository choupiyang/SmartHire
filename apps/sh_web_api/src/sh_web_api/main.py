"""
SmartHire Web API - Main Application

Compliance: LAW-ENV-001 (无容器化), LAW-DEF-001 (防御性防御)

Description:
    FastAPI应用入口，提供RESTful API和WebSocket接口
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from typing import Dict, Any

from sh_web_api.routes import recruitment, candidates, matching
from sh_web_api.schemas.api_models import create_error_response
from sh_web_api.error_handlers import register_error_handlers


# =============================================================================
# 日志配置
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# 应用生命周期管理
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("SmartHire Web API启动中...")
    # TODO: 初始化Redis连接
    # TODO: 验证与后端三层架构的连接
    yield
    logger.info("SmartHire Web API关闭中...")


# =============================================================================
# FastAPI应用创建
# =============================================================================

def create_app() -> FastAPI:
    """创建FastAPI应用"""

    app = FastAPI(
        title="SmartHire Web API",
        description="智雇家前后端通信桥梁",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )

    # CORS中间件配置（单租户本地访问）
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(recruitment.router, prefix="/api/v1/recruitment", tags=["招募"])
    app.include_router(candidates.router, prefix="/api/v1/candidates", tags=["候选人"])
    app.include_router(matching.router, prefix="/api/v1/matching", tags=["匹配"])

    # 注册全局错误处理器
    register_error_handlers(app)
    
    # 健康检查端点
    @app.get("/health")
    async def health_check():
        """健康检查"""
        return {
            "status": "healthy",
            "service": "smarthire-web-api",
            "version": "1.0.0"
        }

    return app


# 创建应用实例
app = create_app()


# =============================================================================
# WebSocket连接管理
# =============================================================================

class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        """接受连接"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"WebSocket客户端已连接: {client_id}")

    def disconnect(self, client_id: str) -> None:
        """断开连接"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"WebSocket客户端已断开: {client_id}")

    async def send_message(self, client_id: str, message: dict):
        """发送消息"""
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

    async def broadcast(self, message: dict):
        """广播消息"""
        for connection in self.active_connections.values():
            await connection.send_json(message)


manager = ConnectionManager()


# =============================================================================
# WebSocket端点
# =============================================================================

@app.websocket("/ws/generate")
async def websocket_generate(websocket: WebSocket):
    """招募文案生成的WebSocket端点（实时推送AI思考过程）"""
    client_id = websocket.query_params.get("client_id", "unknown")

    try:
        await manager.connect(client_id, websocket)

        while True:
            # 接收客户端消息
            data = await websocket.receive_json()

            if data.get("type") == "start_generation":
                # TODO: 调用PLAN进程进行生成
                # 模拟实时推送AI思考过程
                await manager.send_message(client_id, {
                    "type": "thinking_step",
                    "step": 1,
                    "description": "正在理解您的需求...",
                    "progress": 20
                })

                await manager.send_message(client_id, {
                    "type": "thinking_step",
                    "step": 2,
                    "description": "正在分析职位要求...",
                    "progress": 50
                })

                await manager.send_message(client_id, {
                    "type": "thinking_step",
                    "step": 3,
                    "description": "正在生成招募文案...",
                    "progress": 80
                })

                await manager.send_message(client_id, {
                    "type": "complete",
                    "result": {
                        "job_posting": {
                            "job_title": "周末双休育儿嫂",
                            "responsibilities": [
                                "负责婴幼儿日常看护",
                                "科学喂养及辅食制作"
                            ],
                            "requirements": [
                                "3年以上育儿经验",
                                "持有育婴师证"
                            ],
                            "salary_range": "3500-4500元/月"
                        }
                    }
                })

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        manager.disconnect(client_id)


# =============================================================================
# 开发模式启动
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "sh_web_api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,  # 开发模式自动重载
        log_level="info"
    )
