from pymongo import MongoClient
from typing import Dict
from app.core.config import settings
from app.core.shop_manager import get_shop_manager

# Create MongoDB client for shared database
shared_client = MongoClient(
    settings.MONGODB_SHARED_URL,
    tlsInsecure=True,
    serverSelectionTimeoutMS=10000
)

# Get shared database instance
db_shared = shared_client.get_default_database()

# Shop-specific database clients cache
_shop_clients: Dict[str, MongoClient] = {}
_shop_databases: Dict[str, any] = {}

def get_shop_client(shop_id: str) -> MongoClient:
    """Get MongoDB client for specific shop"""
    if shop_id in _shop_clients:
        return _shop_clients[shop_id]
    
    shop_manager = get_shop_manager()
    shop_config = shop_manager.get_shop(shop_id)
    
    if not shop_config:
        raise ValueError(f"Shop '{shop_id}' not found in configuration")
    
    client = MongoClient(
        shop_config.mongodb_url,
        tlsInsecure=True,
        serverSelectionTimeoutMS=10000
    )
    
    _shop_clients[shop_id] = client
    return client

def get_shop_database(shop_id: str):
    """Get database instance for specific shop"""
    if shop_id in _shop_databases:
        return _shop_databases[shop_id]
    
    client = get_shop_client(shop_id)
    database = client.get_default_database()
    
    _shop_databases[shop_id] = database
    return database

def get_database(shop: str = "shared"):
    """
    Get database by shop name - supports both legacy and dynamic shops
    Args:
        shop: shop_id from configuration or "shared"
    Returns:
        MongoDB database instance
    """
    if shop == "shared":
        return db_shared
    
    # Use shop manager for dynamic shop databases
    shop_manager = get_shop_manager()
    if shop_manager.is_valid_shop(shop):
        return get_shop_database(shop)
    
    # Fallback for unknown shops
    raise ValueError(f"Unknown shop: {shop}")

def get_tinashop_db():
    """Get Tina Shop database - legacy compatibility"""
    return get_shop_database("tinashop")

def get_micocah_db():
    """Get Micocah VN database - legacy compatibility"""
    return get_shop_database("micocah")

def get_shared_db():
    """Get shared database (users, auth, etc.)"""
    return db_shared
