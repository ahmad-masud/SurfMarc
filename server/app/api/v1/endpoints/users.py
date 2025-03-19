from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import User
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current user information.
    """
    return current_user 