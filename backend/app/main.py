# Application Module
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="文档处理工具API",
    debug=settings.debug,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """根路径"""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


# Include routers
from app.api import conversion, search, annotation, page, batch, merge

# 添加带API前缀的健康检查端点（放在include_router之后）
@app.get("/api/v1/health")
async def health_check_with_prefix():
    """健康检查（带API前缀）"""
    return {"status": "healthy"}

app.include_router(conversion.router, prefix=settings.api_prefix, tags=["conversion"])
app.include_router(search.router, prefix=settings.api_prefix, tags=["search"])
app.include_router(annotation.router, prefix=settings.api_prefix, tags=["annotation"])
app.include_router(page.router, prefix=settings.api_prefix, tags=["page"])
app.include_router(batch.router, prefix=settings.api_prefix, tags=["batch"])
app.include_router(merge.router, prefix=settings.api_prefix, tags=["merge"])
