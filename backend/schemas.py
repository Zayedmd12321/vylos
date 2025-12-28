from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --- Project Schemas ---
class ProjectBase(BaseModel):
    name: str
    git_url: str

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    domain: Optional[str] = None
    status: str
    created_at: datetime
    owner_id: int

    class Config:
        from_attributes = True

# --- User Schemas ---
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    projects: List[Project] = []

    class Config:
        from_attributes = True