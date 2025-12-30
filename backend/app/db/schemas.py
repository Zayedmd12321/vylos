"""
Pydantic Schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime


# --- User Schemas ---
class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr


class UserSignup(BaseModel):
    """User signup schema"""
    full_name: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """User response schema"""
    id: int
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool
    avatar_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class UserWithProjects(UserResponse):
    """User with projects response schema"""
    projects: List["ProjectResponse"] = []


# --- Auth Schemas ---
class Token(BaseModel):
    """JWT Token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data"""
    user_id: Optional[int] = None
    email: Optional[str] = None


# --- Project Schemas ---
class ProjectBase(BaseModel):
    """Base project schema"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class ProjectCreate(ProjectBase):
    """Project creation schema"""
    git_url: str = Field(..., min_length=1)
    branch: str = Field(default="main", max_length=100)


class ProjectUpdate(BaseModel):
    """Project update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    branch: Optional[str] = Field(None, max_length=100)


class ProjectResponse(ProjectBase):
    """Project response schema"""
    id: int
    framework: Optional[str] = None
    status: str
    repo_url: str
    branch: str
    domain: Optional[str] = None
    build_logs: Optional[str] = None
    created_at: datetime
    last_deployed_at: Optional[datetime] = None
    owner_id: int
    
    class Config:
        from_attributes = True


# --- Deployment Schemas ---
class DeploymentBase(BaseModel):
    """Base deployment schema"""
    status: str


class DeploymentCreate(BaseModel):
    """Deployment creation schema"""
    git_url: str
    project_id: str


class DeploymentResponse(DeploymentBase):
    """Deployment response schema"""
    id: int
    commit_message: Optional[str] = None
    commit_hash: Optional[str] = None
    duration_seconds: Optional[int] = None
    created_at: datetime
    project_id: int

    class Config:
        from_attributes = True


# --- API Response Schemas ---
class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    status: str = "success"


class DeployResponse(MessageResponse):
    """Deploy endpoint response"""
    project_id: str
    user_email: str
