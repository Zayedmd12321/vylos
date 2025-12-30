from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import get_db
from auth import get_current_user

router = APIRouter(
    prefix="/projects",
    tags=["projects"]
)

# GET /projects - List all projects for the dashboard
@router.get("/", response_model=List[schemas.Project])
def read_projects(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.Project).filter(
        models.Project.owner_id == current_user.id
    ).all()

# POST /projects - Create a new project (Import)
@router.post("/", response_model=schemas.Project)
def create_project(
    project_in: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check if project name exists for this user
    existing = db.query(models.Project).filter(
        models.Project.owner_id == current_user.id,
        models.Project.name == project_in.name
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Project name already exists")

    # Create the DB entry
    new_project = models.Project(
        name=project_in.name,
        repo_url=project_in.git_url, # Mapping git_url to repo_url
        framework="React",           # Default or detect later
        status="Queued",
        owner_id=current_user.id
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project