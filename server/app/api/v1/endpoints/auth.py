from datetime import datetime, timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from app.core.config import settings
from app.schemas.user import User, UserCreate, Token, LoginRequest
from app.db.supabase import supabase

router = APIRouter()

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

@router.post("/login", response_model=Token)
async def login(request: LoginRequest) -> Any:
    """
    Login endpoint that accepts JSON data
    """
    try:
        # Authenticate with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password,
        })
        
        if not auth_response or not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Get user from our database
        user_data = supabase.table("users").select("*").eq("id", auth_response.user.id).single().execute()
        if not user_data.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Create our own JWT token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_data.data["email"]}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/register", response_model=Token)
async def register(user_in: UserCreate) -> Any:
    """
    Register new user.
    """
    try:
        print(f"Starting registration for email: {user_in.email}")  # Debug log
        
        # First check if user exists in our database
        print("Checking if user exists in database...")  # Debug log
        existing_user = supabase.table("users").select("*").eq("email", user_in.email).execute()
        if existing_user.data:
            print(f"User exists in database with email: {user_in.email}")  # Debug log
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        
        print("Creating user in Supabase Auth...")  # Debug log
        # Create user in Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": user_in.email,
            "password": user_in.password,
        })
        
        if not auth_response or not auth_response.user:
            print("Failed to create user in Supabase Auth")  # Debug log
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user",
            )
            
        print(f"User created in Supabase Auth with ID: {auth_response.user.id}")  # Debug log
        
        # Create user in our database
        print("Creating user in database...")  # Debug log
        user_data = {
            "id": auth_response.user.id,
            "email": user_in.email,
            "full_name": user_in.full_name,
            "is_active": user_in.is_active,
        }
        
        try:
            db_response = supabase.table("users").insert(user_data).execute()
            print(f"Database response: {db_response}")  # Debug log
            
            if not db_response.data:
                print("Failed to create user in database")  # Debug log
                # If database insert fails, we should clean up the auth user
                try:
                    supabase.auth.admin.delete_user(auth_response.user.id)
                    print("Cleaned up auth user after database failure")  # Debug log
                except Exception as cleanup_error:
                    print(f"Failed to clean up auth user: {str(cleanup_error)}")  # Debug log
                
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create user in database",
                )
        except Exception as db_error:
            print(f"Database error: {str(db_error)}")  # Debug log
            # If database insert fails, we should clean up the auth user
            try:
                supabase.auth.admin.delete_user(auth_response.user.id)
                print("Cleaned up auth user after database error")  # Debug log
            except Exception as cleanup_error:
                print(f"Failed to clean up auth user: {str(cleanup_error)}")  # Debug log
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database error: {str(db_error)}",
            )
            
        print("Creating access token...")  # Debug log
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_in.email}, expires_delta=access_token_expires
        )
        
        print("Registration successful")  # Debug log
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Registration error: {str(e)}")  # Debug log
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) 