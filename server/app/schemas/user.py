from typing import Optional
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    is_active: bool = True

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    is_active: bool = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str 