"""
Database Models
"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base


class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # OAuth fields
    github_access_token = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)

    # Relationships
    projects = relationship("Project", back_populates="owner")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class Project(Base):
    """Project model for deployed applications"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    framework = Column(String, nullable=True)
    status = Column(String, default="Queued")  # Queued, Building, Live, Failed
    
    # Repository details
    repo_url = Column(String, nullable=False)
    branch = Column(String, default="main")
    
    # Domain
    domain = Column(String, nullable=True)
    
    # Build logs
    build_logs = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_deployed_at = Column(DateTime, nullable=True)
    
    # Foreign keys
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="projects")

    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name}, status={self.status})>"
