"""
Authentication Service - Business logic for user authentication
"""
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db import models
from app.db import schemas
from app.core.security import verify_password, get_password_hash, create_access_token


class AuthService:
    """Authentication service for user management"""
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
        """
        Authenticate user with email and password
        
        Args:
            db: Database session
            email: User email
            password: User password
            
        Returns:
            User model if authentication successful, None otherwise
        """
        user = db.query(models.User).filter(models.User.email == email).first()
        
        if not user:
            return None
        
        # Check if user is OAuth-only
        if user.hashed_password in ["oauth", "google_oauth"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please login with Google/GitHub"
            )
        
        # Verify password
        if not verify_password(password, str(user.hashed_password)):
            return None
        
        return user
    
    @staticmethod
    def create_user(db: Session, user_data: schemas.UserSignup) -> models.User:
        """
        Create a new user
        
        Args:
            db: Database session
            user_data: User signup data
            
        Returns:
            Created user model
            
        Raises:
            HTTPException: If email or username already exists
        """
        # Check if email exists
        if db.query(models.User).filter(models.User.email == user_data.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username exists
        if db.query(models.User).filter(models.User.username == user_data.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create user
        hashed_pwd = get_password_hash(user_data.password)
        new_user = models.User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_pwd,
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user
    
    @staticmethod
    def create_or_update_oauth_user(
        db: Session,
        email: str,
        provider: str,
        access_token: Optional[str] = None,
        avatar_url: Optional[str] = None
    ) -> models.User:
        """
        Create or update OAuth user
        
        Args:
            db: Database session
            email: User email
            provider: OAuth provider (github, google)
            access_token: OAuth access token
            avatar_url: User avatar URL
            
        Returns:
            User model
        """
        user = db.query(models.User).filter(models.User.email == email).first()
        
        if not user:
            # Create new OAuth user
            user = models.User(
                email=email,
                hashed_password=f"{provider}_oauth",
                is_active=True,
                avatar_url=avatar_url,
                github_access_token=access_token if provider == "github" else None
            )
            db.add(user)
        else:
            # Update existing user
            if provider == "github" and access_token:
                setattr(user, 'github_access_token', access_token)
            if avatar_url:
                setattr(user, 'avatar_url', avatar_url)
        
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def create_token_for_user(user: models.User) -> str:
        """
        Create JWT access token for user
        
        Args:
            user: User model
            
        Returns:
            JWT access token
        """
        return create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
