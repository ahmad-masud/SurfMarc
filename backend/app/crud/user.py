from typing import Optional, Dict, Any
from app.core import security
from app.schemas.user import UserCreate, UserUpdate
from app.db.supabase import supabase

class CRUDUser:
    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        result = supabase.table("users").select("*").eq("email", email).execute()
        return result.data[0] if result.data else None

    def create(self, obj_in: UserCreate) -> Dict[str, Any]:
        user_data = obj_in.dict()
        user_data["hashed_password"] = security.get_password_hash(user_data.pop("password"))
        result = supabase.table("users").insert(user_data).execute()
        return result.data[0]

    def update(self, id: str, obj_in: UserUpdate) -> Optional[Dict[str, Any]]:
        user_data = obj_in.dict(exclude_unset=True)
        if "password" in user_data:
            user_data["hashed_password"] = security.get_password_hash(user_data.pop("password"))
        result = supabase.table("users").update(user_data).eq("id", id).execute()
        return result.data[0] if result.data else None

    def authenticate(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        user = self.get_by_email(email)
        if not user:
            return None
        if not security.verify_password(password, user["hashed_password"]):
            return None
        return user

user = CRUDUser() 