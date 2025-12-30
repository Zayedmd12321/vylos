from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True, nullable=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    
    github_access_token = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)

    projects = relationship("Project", back_populates="owner")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)          
    description = Column(String, nullable=True)
    framework = Column(String)
    status = Column(String, default="Queued")  # Live, Building, Failed, Queued
    
    # GitHub Integration details
    repo_url = Column(String)
    branch = Column(String, default="main")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_deployed_at = Column(DateTime, nullable=True)
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="projects")
    deployments = relationship("Deployment", back_populates="project")

class Deployment(Base):
    __tablename__ = "deployments"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String)  # Success, Failure, In Progress
    commit_message = Column(String, nullable=True)
    commit_hash = Column(String, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project_id = Column(Integer, ForeignKey("projects.id"))
    project = relationship("Project", back_populates="deployments")