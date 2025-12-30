from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import RedirectResponse
import httpx
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

# Import your local modules
from database import SessionLocal
import models
import schemas
from config import settings
from security import create_access_token, get_password_hash, verify_password

router = APIRouter()
security = HTTPBearer()

# --- DATABASE DEPENDENCY ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- THE BOUNCER (Protect Routes) ---
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

# ==========================================
# 👇 NEW: EMAIL / PASSWORD AUTH ROUTES
# ==========================================

@router.post("/signup", response_model=schemas.Token)
def signup(user_data: schemas.UserSignup, db: Session = Depends(get_db)):
    # 1. Check if email already exists
    if db.query(models.User).filter(models.User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 2. Check if username already exists
    if db.query(models.User).filter(models.User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    # 3. Create new user
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

    # 4. Generate Token
    access_token = create_access_token(data={"sub": str(new_user.id), "email": new_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=schemas.Token)
def login(user_data: schemas.UserLogin, db: Session = Depends(get_db)):
    # 1. Find user
    user = db.query(models.User).filter(models.User.email == user_data.email).first()
    
    # 2. Validate user exists
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    # 3. Handle OAuth-only users (who have no password set)
    if user.hashed_password in ["oauth", "google_oauth"]:
        raise HTTPException(status_code=400, detail="Please login with Google/GitHub")

    # 4. Validate Password
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # 5. Generate Token
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# ==========================================
# 👆 EXISTING OAUTH ROUTES
# ==========================================

@router.get("/login/github")
async def login_github():
    return {
        "url": f"https://github.com/login/oauth/authorize?client_id={settings.GITHUB_CLIENT_ID}&scope=user:email"
    }

@router.get("/auth/github/callback")
async def auth_callback(code: str, db: Session = Depends(get_db)):
    async with httpx.AsyncClient() as client:
        # 1. Exchange Code for Token
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
            raise HTTPException(status_code=400, detail="Invalid code from GitHub")

        # 2. Fetch User Profile (New: Get Avatar)
        user_res = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_profile = user_res.json()
        avatar_url = user_profile.get("avatar_url")

        # 3. Fetch Emails
        email_res = await client.get(
            "https://api.github.com/user/emails",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        emails = email_res.json()
        primary_email = next((e["email"] for e in emails if e["primary"]), None)

        if not primary_email:
            raise HTTPException(status_code=400, detail="No primary email found")

    # 4. Find or Create User (AND SAVE TOKEN)
    user = db.query(models.User).filter(models.User.email == primary_email).first()
    
    if not user:
        user = models.User(
            email=primary_email, 
            hashed_password="oauth", 
            is_active=True,
            avatar_url=avatar_url,          # Save Avatar
            github_access_token=access_token # Save Token
        )
        db.add(user)
    else:
        # Update token if user exists (it rotates)
        user.github_access_token = access_token
        user.avatar_url = avatar_url
            
    db.commit()
    db.refresh(user)

    # 5. Redirect to Dashboard
    jwt_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    # Make sure this matches your frontend port (3000)
    frontend_url = f"http://localhost:3000/auth/callback?token={jwt_token}"
    return RedirectResponse(url=frontend_url)

@router.get("/login/google")
async def login_google():
    return {
        "url": f"https://accounts.google.com/o/oauth2/v2/auth?client_id={settings.GOOGLE_CLIENT_ID}&response_type=code&scope=openid%20email%20profile&redirect_uri=http://localhost:8000/auth/google/callback&state=random_state_string"
    }

@router.get("/auth/google/callback")
async def auth_google_callback(code: str, db: Session = Depends(get_db)):
    async with httpx.AsyncClient() as client:
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
            raise HTTPException(status_code=400, detail="Invalid Google code")

        user_res = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_data = user_res.json()
        email = user_data.get("email")

        if not email:
            raise HTTPException(status_code=400, detail="Google did not provide an email")

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        user = models.User(email=email, hashed_password="google_oauth", is_active=True)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    frontend_url = f"http://localhost:3000/auth/callback?token={access_token}"
    return RedirectResponse(url=frontend_url)