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
    Update current user information, including optional email update.
    """
    try:
        update_data = user_update.dict(exclude_unset=True)

        # Step 1: Update email if requested
        if "email" in update_data:
            print(f"Updating email to {update_data['email']}")
            email_update_response = supabase.auth.update_user({"email": update_data["email"]})

            if hasattr(email_update_response, "error") and email_update_response.error:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to update email in authentication system"
                )

        # Step 2: Remove email from DB update payload
        update_data.pop("email", None)

        # Step 3: Update user profile in your DB
        response = supabase.table("users").update(update_data).eq("id", current_user.id).execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        updated_user = response.data[0]

        # Step 4: Get the updated email from Supabase Auth
        auth_user = supabase.auth.get_user()
        updated_user["email"] = auth_user.user.email if auth_user and auth_user.user else None

        # Step 5: Return full user object
        return User(**updated_user)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Update user error: {str(e)}")
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
    Change user password by verifying the current one first.
    Fetch email from Supabase Auth (not DB).
    """
    try:
        # Step 1: Get the authenticated user's info from Supabase
        user_info = supabase.auth.get_user()
        if not user_info.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not fetch user info from Supabase"
            )

        user_email = user_info.user.email
        if not user_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User email not available"
            )

        # Step 2: Re-authenticate using current password
        auth_check = supabase.auth.sign_in_with_password({
            "email": user_email,
            "password": password_change.current_password
        })

        if not auth_check.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )

        # Step 3: Proceed to update the password
        update_response = supabase.auth.update_user({
            "password": password_change.new_password
        })

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
        db_response = supabase.table("users").delete().eq("id", current_user.id).execute()

        auth_response = supabase.auth.admin.delete_user(current_user.id)

        return {"message": "User deleted successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
