from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import timedelta
from typing import List
from app.schemas.auth import (
    UserLogin, UserRegister, AdminUserCreate, Token, UserResponse, 
    TokenRefresh, PasswordResetRequest, PasswordReset, EmailVerification,
    ChangePassword, UpdateProfile, UserListResponse
)
from app.crud.user import user_crud
from app.services.auth import (
    create_access_token, create_refresh_token, verify_token,
    create_password_reset_token, create_email_verification_token
)
from app.core.config import settings
from app.core.deps import get_current_user, get_current_user_for_me_endpoint, RequireAdmin, RequireUserRead
from app.core.permissions import UserRole, get_user_permissions
from app.services.email import send_verification_email, send_password_reset_email

router = APIRouter()
security = HTTPBearer()

def create_user_response(user: dict) -> UserResponse:
    """Create UserResponse from user dict"""
    user_role = UserRole(user.get("role", "customer"))
    permissions = get_user_permissions(user_role)
    
    return UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        full_name=user["full_name"],
        is_active=user["is_active"],
        is_verified=user.get("is_verified", False),
        shop=user["shop"],
        role=user_role,
        permissions=permissions,
        created_at=user["created_at"]
    )

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, background_tasks: BackgroundTasks):
    """Register a new user"""
    try:
        # Create user
        user = user_crud.create_user(user_data)
        
        # Create tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=str(user["_id"]), expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(subject=str(user["_id"]))
        
        # Store refresh token
        user_crud.store_refresh_token(str(user["_id"]), refresh_token)
        
        # Send verification email
        verification_token = create_email_verification_token(user["email"])
        background_tasks.add_task(
            send_verification_email, 
            user["email"], 
            user["full_name"], 
            verification_token
        )
        
        # Prepare user response
        user_response = create_user_response(user)
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_response
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Login user"""
    # Authenticate user
    user = user_crud.authenticate_user(user_credentials.email, user_credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=str(user["_id"]), expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(subject=str(user["_id"]))
    
    # Store refresh token
    user_crud.store_refresh_token(str(user["_id"]), refresh_token)
    
    # Prepare user response
    user_response = create_user_response(user)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_response
    )

@router.post("/refresh", response_model=Token)
async def refresh_access_token(token_data: TokenRefresh):
    """Refresh access token using refresh token"""
    # Verify refresh token
    user_id = verify_token(token_data.refresh_token, "refresh")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Validate refresh token in database
    stored_user_id = user_crud.validate_refresh_token(token_data.refresh_token)
    if not stored_user_id or stored_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # Get user
    user = user_crud.get_user_by_id(user_id)
    if not user or not user.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=str(user["_id"]), expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token(subject=str(user["_id"]))
    
    # Revoke old refresh token and store new one
    user_crud.revoke_refresh_token(token_data.refresh_token)
    user_crud.store_refresh_token(str(user["_id"]), new_refresh_token)
    
    # Prepare user response
    user_response = create_user_response(user)
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_response
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user_for_me_endpoint)):
    """Get current user information"""
    return create_user_response(current_user)

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    update_data: UpdateProfile,
    current_user: dict = Depends(get_current_user)
):
    """Update current user profile"""
    update_dict = update_data.dict(exclude_unset=True)
    
    if update_dict:
        success = user_crud.update_user(str(current_user["_id"]), update_dict)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update profile"
            )
    
    # Get updated user
    updated_user = user_crud.get_user_by_id(str(current_user["_id"]))
    return create_user_response(updated_user)

@router.post("/change-password")
async def change_password(
    password_data: ChangePassword,
    current_user: dict = Depends(get_current_user)
):
    """Change user password"""
    # Verify current password
    if not user_crud.authenticate_user(current_user["email"], password_data.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Change password
    success = user_crud.change_password(str(current_user["_id"]), password_data.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )
    
    return {"message": "Password changed successfully"}

@router.post("/logout")
async def logout(token_data: TokenRefresh):
    """Logout user by revoking refresh token"""
    user_crud.revoke_refresh_token(token_data.refresh_token)
    return {"message": "Logged out successfully"}

@router.post("/request-password-reset")
async def request_password_reset(
    reset_data: PasswordResetRequest,
    background_tasks: BackgroundTasks
):
    """Request password reset"""
    user = user_crud.get_user_by_email(reset_data.email)
    if user:  # Always return success for security
        reset_token = create_password_reset_token(reset_data.email)
        background_tasks.add_task(
            send_password_reset_email,
            reset_data.email,
            user["full_name"],
            reset_token
        )
    
    return {"message": "If the email exists, a reset link has been sent"}

@router.post("/reset-password")
async def reset_password(reset_data: PasswordReset):
    """Reset password using token"""
    # Verify reset token
    email = verify_token(reset_data.token, "password_reset")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Get user and change password
    user = user_crud.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    success = user_crud.change_password(str(user["_id"]), reset_data.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        )
    
    return {"message": "Password reset successfully"}

@router.post("/verify-email")
async def verify_email(verification_data: EmailVerification):
    """Verify email using token"""
    # Verify email token
    email = verify_token(verification_data.token, "email_verification")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    # Verify email
    success = user_crud.verify_email(email)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "Email verified successfully"}

@router.get("/users", response_model=UserListResponse)
async def get_users(
    page: int = 1,
    size: int = 10,
    shop: str = None,
    current_user: dict = RequireUserRead
):
    """Get list of users (admin only)"""
    skip = (page - 1) * size
    users = user_crud.get_users(skip=skip, limit=size, shop=shop)
    total = user_crud.count_users(shop=shop)
    
    user_responses = [create_user_response(user) for user in users]
    
    return UserListResponse(
        users=user_responses,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )
