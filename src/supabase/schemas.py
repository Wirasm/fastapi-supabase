from typing import List, Dict, Any, Optional
from pydantic import BaseModel, EmailStr
from gotrue import UserAttributes


class Token(BaseModel):
    """OAuth2 compatible token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "refresh_token": "optional-refresh-token"
            }
        }


class UserBase(BaseModel):
    """Base user properties"""
    email: EmailStr
    is_active: bool = True
    roles: List[str] = ["user"]
    metadata: Dict[str, Any] = {}


class UserIn(UserBase):
    """User model with enhanced security features"""
    id: str

    @property
    def is_admin(self) -> bool:
        return "admin" in self.roles

    @property
    def is_guest(self) -> bool:
        return "guest" in self.roles

    def has_role(self, role: str) -> bool:
        return role in self.roles


class UserCreate(UserBase):
    """Properties to receive via API on creation"""
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "strongpassword123",
                "roles": ["user"],
                "metadata": {"full_name": "John Doe"}
            }
        }


class UserUpdate(UserAttributes):
    """Properties to receive via API on update"""
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    roles: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "email": "newemail@example.com",
                "roles": ["user", "admin"],
                "metadata": {"full_name": "John Doe Updated"}
            }
        }


class TokenResponse(Token):
    """Complete token response with user data"""
    user: UserIn

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "refresh_token": "optional-refresh-token",
                "user": {
                    "id": "user_id",
                    "email": "user@example.com",
                    "roles": ["user"],
                    "metadata": {},
                    "is_active": True
                }
            }
        }
