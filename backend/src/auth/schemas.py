
from typing import Optional
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: Optional[str] = None


class LoginCredentials(BaseModel):
    email: EmailStr
    password: str


class OAuthRequest(BaseModel):
    token: str
