from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from . import models, schemas
from .database import get_db
import os
from .database import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    # In production, this should always be set. 
    # For local development, we can print a warning but we shouldn't hardcode a production-level secret here.
    print("WARNING: SECRET_KEY not found in environment variables. JWT tokens will not be secure.")
    SECRET_KEY = "development_secret_do_not_use_in_production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 # 1 hour

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

from fastapi import Request

def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception

    # Try Dual-Decoding approach
    payload = None
    username = None
    email = None
    
    # 1. Try decoding with local secret (Classic Auth)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except JWTError:
        pass
        
    # 2. If local decryption failed, try decoding with Supabase JWT Secret (Dashboard SSO)
    if not payload:
        try:
            # Safely extract Project URL from environment
            supabase_url = os.environ.get("VITE_SUPABASE_URL")
            anon_key = os.environ.get("VITE_SUPABASE_ANON_KEY")
            
            if not supabase_url or not anon_key:
                raise credentials_exception
            
            # Use httpx to securely ask Supabase to validate the token natively
            import httpx
            resp = httpx.get(
                f"{supabase_url}/auth/v1/user",
                headers={"Authorization": f"Bearer {token}", "apikey": anon_key}
            )
            
            if resp.status_code == 200:
                user_data = resp.json()
                email = user_data.get("email")
            else:
                raise credentials_exception
        except Exception as e:
            print(f"DEBUG: Supabase API validation failed: {str(e)}")
            raise credentials_exception

    if username is None and email is None:
        raise credentials_exception
        
    # Query database
    if username:
        user = db.query(models.User).filter(models.User.username == username).first()
    elif email:
        user = db.query(models.User).filter(models.User.email == email).first()
        
    # Just-in-Time (JIT) Provisioning for Dashboard users
    if (not user or user is None) and email:
        import uuid
        generated_username = f"sso_{email.split('@')[0]}_{str(uuid.uuid4())[:8]}"
        new_user = models.User(
            username=generated_username,
            email=email,
            hashed_password="--sso-user-no-pwd--",
            role=models.Role.User
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        user = new_user
        
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: Annotated[models.User, Depends(get_current_user)]):
    return current_user
