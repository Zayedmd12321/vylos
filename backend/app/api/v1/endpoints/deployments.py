"""
Deployment Endpoints
"""
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_active_user
from app.db import models, schemas
from app.services.deployment_service import DeploymentService
from app.services.project_service import ProjectService

router = APIRouter()


@router.post("/deploy", response_model=schemas.DeployResponse)
async def deploy_project(
    request: schemas.DeploymentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Deploy a project from a Git repository
    
    Args:
        request: Deployment request data
        background_tasks: FastAPI background tasks
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Deployment status
    """
    # Check if project name is available
    user_id = getattr(current_user, 'id')
    ProjectService.check_project_ownership(
        project_name=request.project_id,
        user_id=user_id,
        db=db
    )
    
    # Start deployment in background
    deployment_service = DeploymentService()
    background_tasks.add_task(
        deployment_service.run_deployment,
        request.git_url,
        request.project_id,
        user_id
    )
    
    return {
        "message": f"Deployment started for {request.project_id}",
        "status": "Queued",
        "project_id": request.project_id,
        "user_email": current_user.email
    }
