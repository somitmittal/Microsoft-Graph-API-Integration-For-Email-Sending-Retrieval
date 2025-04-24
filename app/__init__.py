# Initialize the app package
from fastapi import FastAPI
from app.api.routes import router
from app.db.mongodb import get_mongo_client, close_mongo_connection
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MongoDB connection on import
def init_mongo_connection():
    """
    Initialize MongoDB connection
    """
    try:
        get_mongo_client()
        logger.info("MongoDB connection initialized")
    except Exception as e:
        logger.error(f"Failed to initialize MongoDB connection: {str(e)}")
