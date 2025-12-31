"""
Project Service - Business logic for project management
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db import models
from app.db import schemas


class ProjectService:
    """Project management service"""
    
    @staticmethod
    def get_user_projects(db: Session, user_id: int) -> List[models.Project]:
        """
        Get all projects for a user
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of user's projects
        """
        return db.query(models.Project).filter(
            models.Project.owner_id == user_id
        ).all()
    
    @staticmethod
    def get_project_by_id(
        db: Session, 
        project_id: int, 
        user_id: int
    ) -> Optional[models.Project]:
        """
        Get project by ID
        
        Args:
            db: Database session
            project_id: Project ID
            user_id: User ID for ownership verification
            
        Returns:
            Project model if found and owned by user, None otherwise
        """
        project = db.query(models.Project).filter(
            models.Project.id == project_id,
            models.Project.owner_id == user_id
        ).first()
        
        return project
    
    @staticmethod
    def create_project(
        db: Session,
        project_data: schemas.ProjectCreate,
        user_id: int
    ) -> models.Project:
        """
        Create a new project
        
        Args:
            db: Database session
            project_data: Project creation data
            user_id: Owner user ID
            
        Returns:
            Created project model
            
        Raises:
            HTTPException: If project name already exists for user
        """
        # Check if project name exists for this user
        existing = db.query(models.Project).filter(
            models.Project.owner_id == user_id,
            models.Project.name == project_data.name
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project name already exists"
            )
        
        # Create project
        new_project = models.Project(
            name=project_data.name,
            description=project_data.description,
            repo_url=project_data.git_url,
            branch=project_data.branch,
            framework="React",  # Default, can be auto-detected
            status="Queued",
            owner_id=user_id
        )
        
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        
        return new_project
    
    @staticmethod
    def update_project_status(
        db: Session,
        project: models.Project,
        status: str,
        domain: Optional[str] = None,
        build_logs: Optional[str] = None,
        commit: bool = True
    ) -> models.Project:
        """
        Update project status
        
        Args:
            db: Database session
            project: Project model
            status: New status
            domain: Optional domain
            build_logs: Optional build logs
            commit: Whether to commit immediately (default True)
            
        Returns:
            Updated project model
        """
        setattr(project, 'status', status)
        if domain:
            setattr(project, 'domain', domain)
        if build_logs:
            setattr(project, 'build_logs', build_logs)
        
        if commit:
            db.commit()
            db.refresh(project)
        
        return project
    
    @staticmethod
    def check_project_ownership(
        project_name: str,
        user_id: int,
        db: Session
    ) -> bool:
        """
        Check if a project name is already taken by another user
        
        Args:
            project_name: Project name to check
            user_id: Current user ID
            db: Database session
            
        Returns:
            True if name is available or owned by user, False if taken by another user
            
        Raises:
            HTTPException: If project name is taken by another user
        """
        existing = db.query(models.Project).filter(
            models.Project.name == project_name
        ).first()
        
        if existing and getattr(existing, 'owner_id') != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project name already taken by another user"
            )
        
        return True
