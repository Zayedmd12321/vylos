"""
Vylos - Main Application Entry Point
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.db.session import engine
from app.db import models
from app.api.v1.api import api_router
from app.middleware.cors import setup_cors
from app.utils.logging import setup_logging
from app.utils.exceptions import setup_exception_handlers


# Setup logging
logger = setup_logging()

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Web Application Deployment Platform",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Setup middleware
setup_cors(app)

# Setup exception handlers
setup_exception_handlers(app)

# Include API routers
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return JSONResponse(
        content={
            "message": "Welcome to Vylos API",
            "version": settings.VERSION,
            "docs": "/docs" if settings.DEBUG else "Documentation disabled in production"
        }
    )


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        content={
            "status": "healthy",
            "version": settings.VERSION
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )