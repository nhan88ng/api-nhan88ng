from enum import Enum
from typing import List

class UserRole(str, Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class Permission(str, Enum):
    # User permissions
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"
    
    # Product permissions
    PRODUCT_READ = "product:read"
    PRODUCT_WRITE = "product:write"
    PRODUCT_DELETE = "product:delete"
    
    # Order permissions
    ORDER_READ = "order:read"
    ORDER_WRITE = "order:write"
    ORDER_DELETE = "order:delete"
    
    # Admin permissions
    ADMIN_PANEL = "admin:panel"
    SYSTEM_CONFIG = "system:config"

# Role permissions mapping
ROLE_PERMISSIONS = {
    UserRole.CUSTOMER: [
        Permission.PRODUCT_READ,
        Permission.ORDER_READ,
        Permission.ORDER_WRITE,
    ],
    UserRole.ADMIN: [
        Permission.USER_READ,
        Permission.USER_WRITE,
        Permission.PRODUCT_READ,
        Permission.PRODUCT_WRITE,
        Permission.PRODUCT_DELETE,
        Permission.ORDER_READ,
        Permission.ORDER_WRITE,
        Permission.ORDER_DELETE,
        Permission.ADMIN_PANEL,
    ],
    UserRole.SUPER_ADMIN: [
        Permission.USER_READ,
        Permission.USER_WRITE,
        Permission.USER_DELETE,
        Permission.PRODUCT_READ,
        Permission.PRODUCT_WRITE,
        Permission.PRODUCT_DELETE,
        Permission.ORDER_READ,
        Permission.ORDER_WRITE,
        Permission.ORDER_DELETE,
        Permission.ADMIN_PANEL,
        Permission.SYSTEM_CONFIG,
    ]
}

def has_permission(user_role: UserRole, permission: Permission) -> bool:
    """Check if user role has specific permission"""
    return permission in ROLE_PERMISSIONS.get(user_role, [])

def get_user_permissions(user_role: UserRole) -> List[Permission]:
    """Get all permissions for a user role"""
    return ROLE_PERMISSIONS.get(user_role, [])
