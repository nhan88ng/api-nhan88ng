from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from pymongo.database import Database
from pymongo import DESCENDING
from app.db.database import get_shared_db
from app.services.auth import get_password_hash, verify_password
from app.schemas.auth import UserRegister, AdminUserCreate
from app.core.permissions import UserRole, get_user_permissions

"""
User CRUD operations for MongoDB Atlas
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pymongo.collection import Collection
from pymongo import ASCENDING, DESCENDING
from bson import ObjectId
from app.db.database import get_shared_db
from app.schemas.auth import UserRegister, AdminUserCreate
from app.services.auth import get_password_hash, verify_password
from app.core.permissions import UserRole

class UserCRUD:
    def __init__(self):
        self.collection: Collection = get_shared_db().users
        self.refresh_tokens: Collection = get_shared_db().refresh_tokens
        
        # Create indexes
        self._create_indexes()
    
    def _create_indexes(self):
        """Create database indexes for performance"""
        try:
            # User indexes
            self.collection.create_index("email", unique=True)
            self.collection.create_index("shop")
            self.collection.create_index([("shop", ASCENDING), ("role", ASCENDING)])
            self.collection.create_index("is_active")
            self.collection.create_index("created_at")
            
            # Refresh token indexes
            self.refresh_tokens.create_index("user_id")
            self.refresh_tokens.create_index("token", unique=True)
            self.refresh_tokens.create_index("expires_at", expireAfterSeconds=0)
            
        except Exception as e:
            print(f"Warning: Could not create indexes: {e}")
    
    def create_user(self, user_data: UserRegister) -> Dict[str, Any]:
        """Create a new user"""
        # Check if user already exists
        if self.get_user_by_email(user_data.email):
            raise ValueError("Email already registered")
        
        # Create user document
        now = datetime.utcnow()
        user_dict = {
            "email": user_data.email.lower(),
            "hashed_password": get_password_hash(user_data.password),
            "full_name": user_data.full_name,
            "shop": user_data.shop.lower(),
            "role": UserRole.CUSTOMER.value,
            "is_active": True,
            "is_verified": False,
            "created_at": now,
            "updated_at": now,
            "last_login": None,
            "login_count": 0
        }
        
        # Insert user
        result = self.collection.insert_one(user_dict)
        user_dict["_id"] = result.inserted_id
        
        return user_dict
    
    def create_admin_user(self, user_data: AdminUserCreate) -> Dict[str, Any]:
        """Create a new admin user"""
        # Check if user already exists
        if self.get_user_by_email(user_data.email):
            raise ValueError("Email already registered")
        
        # Validate role
        if user_data.role not in [UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value]:
            raise ValueError("Invalid admin role")
        
        # Create admin user document
        now = datetime.utcnow()
        user_dict = {
            "email": user_data.email.lower(),
            "hashed_password": get_password_hash(user_data.password),
            "full_name": user_data.full_name,
            "shop": user_data.shop.lower(),
            "role": user_data.role,
            "is_active": user_data.is_active,
            "is_verified": True,  # Admin users are pre-verified
            "created_at": now,
            "updated_at": now,
            "last_login": None,
            "login_count": 0,
            "created_by_admin": True
        }
        
        # Insert user
        result = self.collection.insert_one(user_dict)
        user_dict["_id"] = result.inserted_id
        
        return user_dict
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with email and password"""
        user = self.get_user_by_email(email)
        if not user:
            return None
        
        if not verify_password(password, user["hashed_password"]):
            return None
        
        # Update login information
        self.collection.update_one(
            {"_id": user["_id"]},
            {
                "$set": {"last_login": datetime.utcnow()},
                "$inc": {"login_count": 1}
            }
        )
        
        return user
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        return self.collection.find_one({"email": email.lower()})
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            return self.collection.find_one({"_id": ObjectId(user_id)})
        except Exception:
            return None
    
    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user information"""
        try:
            # Remove fields that shouldn't be updated directly
            forbidden_fields = {"_id", "hashed_password", "email", "role", "created_at"}
            filtered_data = {k: v for k, v in update_data.items() if k not in forbidden_fields}
            
            if not filtered_data:
                return True
            
            filtered_data["updated_at"] = datetime.utcnow()
            
            result = self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": filtered_data}
            )
            
            return result.modified_count > 0
            
        except Exception:
            return False
    
    def change_password(self, user_id: str, new_password: str) -> bool:
        """Change user password"""
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "hashed_password": get_password_hash(new_password),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Revoke all refresh tokens for security
            self.revoke_all_user_refresh_tokens(user_id)
            
            return result.modified_count > 0
            
        except Exception:
            return False
    
    def verify_email(self, email: str) -> bool:
        """Mark user email as verified"""
        try:
            result = self.collection.update_one(
                {"email": email.lower()},
                {
                    "$set": {
                        "is_verified": True,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception:
            return False
    
    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user account"""
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "is_active": False,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Revoke all refresh tokens
            self.revoke_all_user_refresh_tokens(user_id)
            
            return result.modified_count > 0
            
        except Exception:
            return False
    
    def activate_user(self, user_id: str) -> bool:
        """Activate user account"""
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "is_active": True,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception:
            return False
    
    def update_user_role(self, user_id: str, new_role: UserRole) -> bool:
        """Update user role (admin only)"""
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "role": new_role.value,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception:
            return False
    
    def get_users(
        self, 
        skip: int = 0, 
        limit: int = 10, 
        shop: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """Get list of users with filters"""
        filter_dict = {}
        
        if shop:
            filter_dict["shop"] = shop.lower()
        if role:
            filter_dict["role"] = role
        if is_active is not None:
            filter_dict["is_active"] = is_active
        if is_verified is not None:
            filter_dict["is_verified"] = is_verified
        
        cursor = self.collection.find(filter_dict).sort("created_at", DESCENDING)
        
        if skip > 0:
            cursor = cursor.skip(skip)
        if limit > 0:
            cursor = cursor.limit(limit)
        
        return list(cursor)
    
    def count_users(
        self,
        shop: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None
    ) -> int:
        """Count users with filters"""
        filter_dict = {}
        
        if shop:
            filter_dict["shop"] = shop.lower()
        if role:
            filter_dict["role"] = role
        if is_active is not None:
            filter_dict["is_active"] = is_active
        if is_verified is not None:
            filter_dict["is_verified"] = is_verified
        
        return self.collection.count_documents(filter_dict)
    
    def search_users(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search users by name or email"""
        regex_pattern = {"$regex": query, "$options": "i"}
        
        filter_dict = {
            "$or": [
                {"full_name": regex_pattern},
                {"email": regex_pattern}
            ]
        }
        
        return list(
            self.collection.find(filter_dict)
            .sort("created_at", DESCENDING)
            .limit(limit)
        )
    
    # Refresh Token Management
    def store_refresh_token(self, user_id: str, token: str) -> bool:
        """Store refresh token"""
        try:
            expires_at = datetime.utcnow() + timedelta(days=30)  # 30 day expiry
            
            self.refresh_tokens.insert_one({
                "user_id": user_id,
                "token": token,
                "created_at": datetime.utcnow(),
                "expires_at": expires_at,
                "is_active": True
            })
            
            return True
            
        except Exception:
            return False
    
    def validate_refresh_token(self, token: str) -> Optional[str]:
        """Validate refresh token and return user ID"""
        try:
            token_doc = self.refresh_tokens.find_one({
                "token": token,
                "is_active": True,
                "expires_at": {"$gt": datetime.utcnow()}
            })
            
            return token_doc["user_id"] if token_doc else None
            
        except Exception:
            return None
    
    def revoke_refresh_token(self, token: str) -> bool:
        """Revoke a specific refresh token"""
        try:
            result = self.refresh_tokens.update_one(
                {"token": token},
                {"$set": {"is_active": False}}
            )
            
            return result.modified_count > 0
            
        except Exception:
            return False
    
    def revoke_all_user_refresh_tokens(self, user_id: str) -> bool:
        """Revoke all refresh tokens for a user"""
        try:
            result = self.refresh_tokens.update_many(
                {"user_id": user_id},
                {"$set": {"is_active": False}}
            )
            
            return True
            
        except Exception:
            return False
    
    def cleanup_expired_tokens(self) -> int:
        """Clean up expired refresh tokens"""
        try:
            result = self.refresh_tokens.delete_many({
                "expires_at": {"$lt": datetime.utcnow()}
            })
            
            return result.deleted_count
            
        except Exception:
            return 0

# Initialize user CRUD instance
user_crud = UserCRUD()
