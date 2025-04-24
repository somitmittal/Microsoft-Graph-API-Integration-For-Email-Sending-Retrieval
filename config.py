import os
from pydantic import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # MongoDB settings
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB: str = os.getenv("MONGODB_DB", "email_integration")
    
    # Microsoft Graph API settings
    MS_CLIENT_ID: str = os.getenv("MS_CLIENT_ID", "")
    MS_CLIENT_SECRET: str = os.getenv("MS_CLIENT_SECRET", "")
    MS_TENANT_ID: str = os.getenv("MS_TENANT_ID", "")
    MS_AUTHORITY: str = os.getenv("MS_AUTHORITY", f"https://login.microsoftonline.com/{os.getenv('MS_TENANT_ID')}")
    MS_SCOPE: list = os.getenv("MS_SCOPE", "https://graph.microsoft.com/.default").split(',')
    
    # Email retrieval settings
    EMAIL_RETRIEVAL_INTERVAL: int = int(os.getenv("EMAIL_RETRIEVAL_INTERVAL", "300"))  # in seconds

    class Config:
        env_file = ".env"

settings = Settings()