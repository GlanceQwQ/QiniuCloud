from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager
from database import init_database
from routers import auth, characters, conversations, messages
from ai_service import ai_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化数据库
    init_database()
    yield
    # 关闭时的清理工作（如果需要）

app = FastAPI(
    title="AI角色扮演网站API",
    description="基于FastAPI的AI角色扮演网站后端服务",
    version="1.0.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(characters.router, prefix="/api/characters", tags=["角色管理"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["会话管理"])
app.include_router(messages.router, prefix="/api/messages", tags=["消息管理"])

@app.get("/")
async def root():
    return {"message": "AI角色扮演网站API服务"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "服务运行正常"}

@app.get("/api/ai/test")
async def test_ai_service():
    """测试AI服务连接"""
    if not ai_service.is_available():
        raise HTTPException(status_code=503, detail="AI服务不可用")
    
    try:
        # 测试简单的AI调用
        test_messages = [
            {"role": "user", "content": "Hello, please respond with 'AI service is working!'"}
        ]
        
        response_parts = []
        async for chunk in ai_service.generate_response(test_messages, max_tokens=50):
            response_parts.append(chunk)
        
        full_response = "".join(response_parts)
        
        return {
            "status": "success",
            "message": "AI服务连接正常",
            "provider": "openrouter",
            "test_response": full_response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI服务测试失败: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )