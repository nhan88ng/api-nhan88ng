from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from app.core.permissions import UserRole, Permission

# Auth schemas
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    full_name: str = Field(..., min_length=2, description="Full name must be at least 2 characters")
    shop: str = Field(..., description="Shop identifier: 'tinashop' or 'micocah'")
    
    @validator('shop')
    def validate_shop(cls, v):
        allowed_shops = ['tinashop', 'micocah']
        if v not in allowed_shops:
            raise ValueError(f'Shop must be one of: {allowed_shops}')
        return v

class AdminUserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    shop: str
    role: UserRole = UserRole.ADMIN
    
class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    shop: str
    role: UserRole = UserRole.CUSTOMER
    permissions: List[Permission] = []
    created_at: datetime

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes
    user: UserResponse

class TokenRefresh(BaseModel):
    refresh_token: str

class TokenData(BaseModel):
    user_id: Optional[str] = None

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)

class EmailVerification(BaseModel):
    token: str

class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)

class UpdateProfile(BaseModel):
    full_name: Optional[str] = None
    
class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    size: int
    pages: int
