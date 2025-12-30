"""
API v1 Router
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, projects, deployments, logs

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    auth.router,
    tags=["authentication"]
)

api_router.include_router(
    projects.router,
    prefix="/projects",
    tags=["projects"]
)

api_router.include_router(
    deployments.router,
    tags=["deployments"]
)

api_router.include_router(
    logs.router,
    prefix="/logs",
    tags=["logs"]
)
