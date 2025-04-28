from pymongo import MongoClient
from config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB client instance
_mongo_client = None

def get_mongo_client():
    """
    Get or create MongoDB client instance
    """
    global _mongo_client
    
    if _mongo_client is None:
        try:
            _mongo_client = MongoClient(settings.MONGODB_URI)
            _mongo_client.server_info()  # Check if connection is successful
            logger.info(f"Connected to MongoDB at {settings.MONGODB_URI}")
            return _mongo_client
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
    return _mongo_client

def get_database():
    """
    Get MongoDB database instance
    """
    client = get_mongo_client()
    return client[settings.MONGODB_COLLECTION]

def get_email_collection():
    """
    Get emails collection from MongoDB
    """
    db = get_database()
    return db["emails"]

def close_mongo_connection():
    """
    Close MongoDB connection
    """
    global _mongo_client
    
    if _mongo_client is not None:
        _mongo_client.close()
        _mongo_client = None
        logger.info("MongoDB connection closed")