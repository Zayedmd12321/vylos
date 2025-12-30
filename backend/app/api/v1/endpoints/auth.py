"""
Authentication Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import httpx

from app.core.dependencies import get_db
from app.core.config import settings
from app.db import schemas
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/signup", response_model=schemas.Token, status_code=status.HTTP_201_CREATED)
def signup(user_data: schemas.UserSignup, db: Session = Depends(get_db)):
    """
    Create new user account
    
    Args:
        user_data: User signup data
        db: Database session
        
    Returns:
        JWT access token
    """
    # Create user
    new_user = AuthService.create_user(db, user_data)
    
    # Generate token
    access_token = AuthService.create_token_for_user(new_user)
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=schemas.Token)
def login(user_data: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Login with email and password
    
    Args:
        user_data: User login credentials
        db: Database session
        
    Returns:
        JWT access token
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Authenticate user
    user = AuthService.authenticate_user(db, user_data.email, user_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials"
        )
    
    # Generate token
    access_token = AuthService.create_token_for_user(user)
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/login/github")
async def login_github():
    """
    Get GitHub OAuth URL
    
    Returns:
        GitHub OAuth authorization URL
    """
    return {
        "url": (
            f"https://github.com/login/oauth/authorize"
            f"?client_id={settings.GITHUB_CLIENT_ID}"
            f"&scope=user:email"
        )
    }


@router.get("/auth/github/callback")
async def auth_github_callback(code: str, db: Session = Depends(get_db)):
    """
    GitHub OAuth callback
    
    Args:
        code: OAuth authorization code
        db: Database session
        
    Returns:
        Redirect to frontend with JWT token
    """
    async with httpx.AsyncClient() as client:
        # Exchange code for token
        token_res = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
            },
        )
        token_data = token_res.json()
        access_token = token_data.get("access_token")

        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid code from GitHub"
            )

        # Fetch user profile
        user_res = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_profile = user_res.json()
        avatar_url = user_profile.get("avatar_url")

        # Fetch emails
        email_res = await client.get(
            "https://api.github.com/user/emails",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        emails = email_res.json()
        primary_email = next((e["email"] for e in emails if e["primary"]), None)

        if not primary_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No primary email found"
            )

    # Create or update user
    user = AuthService.create_or_update_oauth_user(
        db=db,
        email=primary_email,
        provider="github",
        access_token=access_token,
        avatar_url=avatar_url
    )

    # Generate JWT token
    jwt_token = AuthService.create_token_for_user(user)
    
    # Redirect to frontend
    frontend_url = f"http://localhost:3000/auth/callback?token={jwt_token}"
    return RedirectResponse(url=frontend_url)


@router.get("/login/google")
async def login_google():
    """
    Get Google OAuth URL
    
    Returns:
        Google OAuth authorization URL
    """
    return {
        "url": (
            f"https://accounts.google.com/o/oauth2/v2/auth"
            f"?client_id={settings.GOOGLE_CLIENT_ID}"
            f"&response_type=code"
            f"&scope=openid%20email%20profile"
            f"&redirect_uri=http://localhost:8000/auth/google/callback"
            f"&state=random_state_string"
        )
    }


@router.get("/auth/google/callback")
async def auth_google_callback(code: str, db: Session = Depends(get_db)):
    """
    Google OAuth callback
    
    Args:
        code: OAuth authorization code
        db: Database session
        
    Returns:
        Redirect to frontend with JWT token
    """
    async with httpx.AsyncClient() as client:
        # Exchange code for token
        token_res = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": "http://localhost:8000/auth/google/callback",
            },
        )
        token_data = token_res.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Google code"
            )

        # Fetch user info
        user_res = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_data = user_res.json()
        email = user_data.get("email")

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google did not provide an email"
            )

    # Create or update user
    user = AuthService.create_or_update_oauth_user(
        db=db,
        email=email,
        provider="google",
        avatar_url=user_data.get("picture")
    )
    
    # Generate JWT token
    jwt_token = AuthService.create_token_for_user(user)
    
    # Redirect to frontend
    frontend_url = f"http://localhost:3000/auth/callback?token={jwt_token}"
    return RedirectResponse(url=frontend_url)
