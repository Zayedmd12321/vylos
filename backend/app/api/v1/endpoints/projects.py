"""
Project Management Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.dependencies import get_db, get_current_active_user
from app.db import models, schemas
from app.services.project_service import ProjectService

router = APIRouter()


@router.get("/", response_model=List[schemas.ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get all projects for the current user
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of user's projects
    """
    return ProjectService.get_user_projects(db, getattr(current_user, 'id'))


@router.post("/", response_model=schemas.ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Create a new project
    
    Args:
        project_in: Project creation data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Created project
    """
    return ProjectService.create_project(db, project_in, getattr(current_user, 'id'))


@router.get("/{project_id}", response_model=schemas.ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get a specific project by ID
    
    Args:
        project_id: Project ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Project details
        
    Raises:
        HTTPException: If project not found
    """
    project = ProjectService.get_project_by_id(db, project_id, getattr(current_user, 'id'))
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project


@router.get("/{project_id}/logs")
def get_project_logs(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get build logs for a specific project
    
    Args:
        project_id: Project ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Build logs as plain text
        
    Raises:
        HTTPException: If project not found
    """
    project = ProjectService.get_project_by_id(db, project_id, getattr(current_user, 'id'))
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    logs = getattr(project, 'build_logs', '')
    return {"logs": logs or "No logs available yet."}
