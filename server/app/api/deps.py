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
        # Decode JWT and get user ID
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        # Fetch profile info from your DB
        user_data = supabase.table("users").select("*").eq("id", user_id).single().execute()
        if not user_data.data:
            raise credentials_exception

        # Fetch email from Supabase Auth
        auth_user = supabase.auth.get_user()
        if not auth_user or not auth_user.user or not auth_user.user.email:
            raise credentials_exception

        # Inject the email into the user data
        user_data.data["email"] = auth_user.user.email
        return User(**user_data.data)

    except JWTError:
        raise credentials_exception
    except Exception as e:
        print(f"Auth error: {str(e)}")
        raise credentials_exception
