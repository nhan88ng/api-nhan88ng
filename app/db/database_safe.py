"""
Database configuration with fallback for testing
"""
from pymongo import MongoClient
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Global database instances
db_tinashop = None
db_micocah = None
db_shared = None

def init_databases():
    """Initialize database connections with error handling"""
    global db_tinashop, db_micocah, db_shared
    
    try:
        # Try to connect to MongoDB Atlas
        tinashop_client = MongoClient(
            settings.MONGODB_TINASHOP_URL,
            serverSelectionTimeoutMS=5000  # 5 second timeout
        )
        micocah_client = MongoClient(
            settings.MONGODB_MICOCAH_URL,
            serverSelectionTimeoutMS=5000
        )
        shared_client = MongoClient(
            settings.MONGODB_SHARED_URL,
            serverSelectionTimeoutMS=5000
        )
        
        # Test connections
        tinashop_client.admin.command('ismaster')
        micocah_client.admin.command('ismaster')
        shared_client.admin.command('ismaster')
        
        # Get databases
        db_tinashop = tinashop_client.get_default_database()
        db_micocah = micocah_client.get_default_database()
        db_shared = shared_client.get_default_database()
        
        logger.info("Successfully connected to MongoDB Atlas")
        return True
        
    except Exception as e:
        logger.warning(f"MongoDB connection failed: {e}")
        logger.info("Running in offline mode - database features disabled")
        return False

def get_database(shop: str = "shared"):
    """
    Get database by shop name
    Args:
        shop: "tinashop", "micocah", or "shared"
    Returns:
        MongoDB database instance or None if not connected
    """
    if shop == "tinashop":
        return db_tinashop
    elif shop == "micocah":
        return db_micocah
    else:
        return db_shared

def get_tinashop_db():
    """Get TinaShop database"""
    return db_tinashop

def get_micocah_db():
    """Get Micocah database"""
    return db_micocah

def get_shared_db():
    """Get shared database"""
    return db_shared

def is_database_available():
    """Check if database is available"""
    return db_shared is not None

# Try to initialize databases on import
try:
    init_databases()
except Exception as e:
    logger.warning(f"Database initialization failed on import: {e}")
    # Continue without database for testing
