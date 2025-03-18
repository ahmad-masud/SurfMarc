from typing import Optional
from pydantic import BaseModel, EmailStr
from uuid import UUID

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    email: EmailStr
    password: str
    full_name: str
    is_active: bool = True

class UserUpdate(UserBase):
    password: Optional[str] = None

class User(UserBase):
    id: UUID
    hashed_password: str

    class Config:
        orm_mode = True

class UserInDB(UserBase):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    sub: Optional[int] = None 