from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core import security
from app.core.config import settings
from app.crud.user import CRUDUser
from app.schemas.user import User, UserCreate, UserInDB, Token
from app.api import deps
from app.db.supabase import supabase

router = APIRouter()

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = supabase.table("users").select("*").eq("email", form_data.username).single().execute()
    if not user.data or not security.verify_password(form_data.password, user.data["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.data["id"], expires_delta=access_token_expires
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
    user = supabase.table("users").select("*").eq("email", user_in.email).single().execute()
    if user.data:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    user_data = user_in.model_dump()
    user_data["hashed_password"] = security.get_password_hash(user_data.pop("password"))
    
    result = supabase.table("users").insert(user_data).execute()
    if not result.data:
        raise HTTPException(
            status_code=500,
            detail="Failed to create user.",
        )
    
    return result.data[0] 