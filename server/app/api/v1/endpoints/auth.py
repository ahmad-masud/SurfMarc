from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from app.core import security
from app.core.config import settings
from app.crud.user import user as crud_user
from app.schemas.user import User, UserCreate, UserInDB, Token
from app.api import deps
from app.db.supabase import supabase
from pydantic import BaseModel

router = APIRouter()

class LoginData(BaseModel):
    email: str
    password: str

@router.post("/login", response_model=Token)
def login(
    login_data: LoginData,
) -> Any:
    """
    Login with email and password
    """
    user = crud_user.authenticate(
        email=login_data.email,
        password=login_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user["id"], expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/register", response_model=User)
def register(
    *,
    user_in: UserCreate,
) -> Any:
    """
    Create new user.
    """
    user = crud_user.get_by_email(email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    user = crud_user.create(obj_in=user_in)
    return user 