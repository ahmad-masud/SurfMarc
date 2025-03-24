from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import User, UserUpdate, PasswordChange
from app.api.deps import get_current_user
from app.db.supabase import supabase
from pydantic import BaseModel

router = APIRouter()

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current user information.
    """
    return current_user

@router.patch("/me", response_model=User)
async def update_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update current user information.
    """
    try:
        # Update user in database
        update_data = user_update.dict(exclude_unset=True)
        response = supabase.table("users").update(update_data).eq("id", current_user.id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if "email" in update_data:
            email_update_response = supabase.auth.admin.update_user_by_id(
                current_user.id,
                {"email": update_data["email"]}
            )
            
            if "error" in email_update_response:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to update email in authentication system"
                )
            
        return User(**response.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/change-password")
async def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_user)
):
    """
    Change user password.
    """
    try:     
        # Verify current password
        auth_response = supabase.auth.sign_in_with_password({
            "email": current_user.email,
            "password": password_change.current_password,
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )
            
        # Update password in Supabase Auth
        update_response = supabase.auth.admin.update_user_by_id(
            current_user.id,  # Pass user_id as a positional argument
            {
                "password": password_change.new_password
            }
        )
        
        if hasattr(update_response, 'error') and update_response.error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to update password: {update_response.error}"
            )
        
        return {"message": "Password updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/me")
async def delete_user(current_user: User = Depends(get_current_user)):
    """
    Delete current user account.
    """
    try:
        # Delete user from database
        supabase.table("users").delete().eq("id", current_user.id).execute()
        
        # Delete user from Supabase Auth
        supabase.auth.admin.delete_user(current_user.id)
        
        return {"message": "User deleted successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 