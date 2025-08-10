from fastapi import HTTPException, Depends, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.services.auth import verify_token
from app.crud.user import user_crud
from app.core.permissions import UserRole, Permission, has_permission

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    try:
        # Verify token
        user_id = verify_token(credentials.credentials)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        user = user_crud.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.get("is_active", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled"
            )
        
        return user
    except HTTPException:
        raise
    except Exception:
        # Any other authentication error should return 401
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user_for_me_endpoint(authorization: Optional[str] = Header(None)):
    """Special dependency for /auth/me endpoint that returns 401 instead of 403"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.replace("Bearer ", "")
    
    try:
        # Verify token
        user_id = verify_token(token)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        user = user_crud.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.get("is_active", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled"
            )
        
        return user
    except HTTPException:
        raise
    except Exception:
        # Any other authentication error should return 401
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))):
    """Get current user if token is provided, otherwise return None"""
    if not credentials:
        return None
        
    try:
        # Verify token
        user_id = verify_token(credentials.credentials)
        if not user_id:
            return None
        
        # Get user from database
        user = user_crud.get_user_by_id(user_id)
        if not user or not user.get("is_active", False):
            return None
            
        return user
    except Exception:
        return None

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """Get current active user"""
    return current_user

def require_permission(permission: Permission):
    """Decorator to require specific permission"""
    def permission_checker(current_user: dict = Depends(get_current_user)):
        user_role = UserRole(current_user.get("role", "customer"))
        
        if not has_permission(user_role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {permission.value}"
            )
        
        return current_user
    
    return permission_checker

def require_role(required_role: UserRole):
    """Decorator to require specific role"""
    def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = UserRole(current_user.get("role", "customer"))
        
        # Super admin can access everything
        if user_role == UserRole.SUPER_ADMIN:
            return current_user
            
        # Check if user has required role or higher
        role_hierarchy = {
            UserRole.CUSTOMER: 0,
            UserRole.ADMIN: 1,
            UserRole.SUPER_ADMIN: 2
        }
        
        if role_hierarchy.get(user_role, 0) < role_hierarchy.get(required_role, 999):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient role. Required: {required_role} or higher"
            )
        
        return current_user
    
    return role_checker

# Common permission dependencies
RequireAdmin = Depends(require_role(UserRole.ADMIN))
RequireSuperAdmin = Depends(require_role(UserRole.SUPER_ADMIN))
RequireUserRead = Depends(require_permission(Permission.USER_READ))
RequireUserWrite = Depends(require_permission(Permission.USER_WRITE))
RequireProductWrite = Depends(require_permission(Permission.PRODUCT_WRITE))
