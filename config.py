import os

from pydantic import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from typing import List

class Settings(BaseSettings):
    # Server settings
    HOST: str = os.getenv("HOST")
    PORT: int = int(os.getenv("PORT"))

    # MongoDB settings
    MONGODB_URI: str = os.getenv("MONGODB_URI")
    MONGODB_COLLECTION: str = os.getenv("MONGODB_COLLECTION")

    # Microsoft Graph API settings
    MS_CLIENT_ID: str = os.getenv("MS_CLIENT_ID")
    MS_CLIENT_SECRET: str = os.getenv("MS_CLIENT_SECRET")
    MS_TENANT_ID: str = os.getenv("MS_TENANT_ID")
    MS_AUTHORITY: str = os.getenv("MS_AUTHORITY")
    MS_SCOPE: str = os.getenv("MS_SCOPE")
    MAIL_SCOPE: str = os.getenv("MAIL_SCOPE")
    REDIRECT_URI: str = os.getenv("REDIRECT_URI")

    # Email retrieval settings
    EMAIL_RETRIEVAL_INTERVAL: int = int(os.getenv("EMAIL_RETRIEVAL_INTERVAL"))
    SEND_EMAIL_URL: str = os.getenv("SEND_EMAIL_URL")
    RETRIEVE_EMAIL_URL: str = os.getenv("RETRIEVE_EMAIL_URL")

    class Config:
        env_file = ".env"

    @property
    def ms_scope_list(self) -> List[str]:
        return [scope.strip() for scope in self.MS_SCOPE.split(",") if scope.strip()]

settings = Settings()