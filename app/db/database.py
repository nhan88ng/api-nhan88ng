from pymongo import MongoClient
from app.core.config import settings

# Create MongoDB clients for each database with SSL configuration
tinashop_client = MongoClient(
    settings.MONGODB_TINASHOP_URL,
    tlsInsecure=True,
    serverSelectionTimeoutMS=10000
)
micocah_client = MongoClient(
    settings.MONGODB_MICOCAH_URL,
    tlsInsecure=True,
    serverSelectionTimeoutMS=10000
)
shared_client = MongoClient(
    settings.MONGODB_SHARED_URL,
    tlsInsecure=True,
    serverSelectionTimeoutMS=10000
)

# Get database instances
db_tinashop = tinashop_client.get_default_database()
db_micocah = micocah_client.get_default_database()
db_shared = shared_client.get_default_database()

def get_database(shop: str = "shared"):
    """
    Get database by shop name
    Args:
        shop: "tinashop", "micocah", or "shared"
    Returns:
        MongoDB database instance
    """
    if shop == "tinashop":
        return db_tinashop
    elif shop == "micocah":
        return db_micocah
    else:
        return db_shared

def get_tinashop_db():
    """Get Tina Shop database"""
    return db_tinashop

def get_micocah_db():
    """Get Micocah VN database"""
    return db_micocah

def get_shared_db():
    """Get shared database (users, auth, etc.)"""
    return db_shared
