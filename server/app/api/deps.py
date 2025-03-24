from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.core.config import settings
from app.schemas.user import User
from app.db.supabase import supabase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Validate our JWT token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
            
        # Get the user details from the users table
        user_data = supabase.table("users").select("*").eq("email", email).single().execute()
        if not user_data.data:
            raise credentials_exception
            
        return User(**user_data.data)
        
    except JWTError:
        raise credentials_exception
    except Exception as e:
        print(f"Auth error: {str(e)}")  # For debugging
        raise credentials_exception