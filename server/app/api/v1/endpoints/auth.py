from datetime import datetime, timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from app.core.config import settings
from app.core.security import create_access_token
from app.schemas.user import User, UserCreate, Token, LoginRequest, PasswordResetRequest, UpdatePasswordRequest
from app.db.supabase import supabase

router = APIRouter()

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
            data={"sub": user_data.data["id"]}, expires_delta=access_token_expires
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

@router.post("/register", response_model=dict)
async def register(user_in: UserCreate) -> Any:
    """
    Register a new user using Supabase Auth only.
    Does not store email in the local database.
    """
    try:
        print("Attempting to register user with Supabase Auth...")
        auth_response = supabase.auth.sign_up({
            "email": user_in.email,
            "password": user_in.password,
        })
        print(f"Supabase Auth sign_up response: {auth_response}")

        if not auth_response or not auth_response.user:
            print("Supabase did not return a user object.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user",
            )

        # Prepare user data for local DB (no email)
        user_data = {
            "id": auth_response.user.id,
            "full_name": user_in.full_name,
            "is_active": user_in.is_active,
        }
        print(f"Prepared user_data for DB insert: {user_data}")

        try:
            db_response = supabase.table("users").insert(user_data).execute()
            print(f"DB insert response: {db_response}")

            if not db_response.data:
                print("DB insert failed. Deleting user from Supabase Auth...")
                try:
                    supabase.auth.admin.delete_user(auth_response.user.id)
                    print("User deleted from Supabase Auth after DB failure.")
                except Exception as e:
                    print("Failed to clean up user from Supabase Auth:", str(e))
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to create user in database",
                    )
        except Exception as db_error:
            print("Exception during DB insert:", str(db_error))
            try:
                supabase.auth.admin.delete_user(auth_response.user.id)
                print("Rolled back user in Supabase Auth.")
            except Exception as e:
                print("Failed to clean up user from Supabase Auth after DB error:", str(e))
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Database error: {str(db_error)}",
                )

        print("User successfully registered.")
        return {"message": "User registered successfully"}

    except HTTPException:
        raise
    except Exception as e:
        print("Unexpected exception during registration:", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.post("/reset-password")
async def reset_password(request: PasswordResetRequest):
    """
    Request a password reset email.
    """
    try:
        reset_redirect_url = "http://localhost:3000/reset-password"

        response = supabase.auth.reset_password_email(request.email, {"redirect_to": reset_redirect_url})

        if hasattr(response, "error") and response.error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to send password reset email",
            )

        return {"message": "Password reset email sent successfully"}

    except HTTPException as http_error:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.post("/update-password")
async def update_password(request: UpdatePasswordRequest):
    """
    Authenticate user with the access token and update their password.
    """
    try:

        # Authenticate the user using the access token
        user_response = supabase.auth.get_user(request.access_token)

        if not hasattr(user_response, "user") or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired access token.",
            )

        user_id = user_response.user.id  # Extract user ID

        # Update password for authenticated user
        update_response = supabase.auth.admin.update_user_by_id(
            user_id,  # Use the authenticated user ID
            {"password": request.new_password}
        )

        if hasattr(update_response, "error") and update_response.error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update password.",
            )

        return {"message": "Password has been successfully updated."}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )