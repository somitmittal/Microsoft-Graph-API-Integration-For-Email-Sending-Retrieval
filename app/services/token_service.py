import logging
import requests

from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from datetime import datetime, timedelta
from typing import Optional

class TokenCache:
    def __init__(self):
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.expiry: Optional[datetime] = None

    def is_token_valid(self) -> bool:
        return self.access_token is not None and self.expiry is not None and datetime.now() < self.expiry

    def set_tokens(self, access_token: str, expires_in: int, refresh_token: str):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expiry = datetime.now() + timedelta(seconds=expires_in)  # small buffer
        logger.info(f"Tokens set: access_token={access_token}, refresh_token={refresh_token}, expires_in={expires_in}")

    def get_access_token(self):
        logger.info("Getting access token...")
        if self.is_token_valid():
            logger.info("Token is valid. Returning...")
            return self.access_token
        if self.refresh_token:
            # Refresh using the refresh token
            logger.info("Refreshing token...")
            token_url = f"{settings.MS_AUTHORITY}/oauth2/v2.0/token"
            refresh_response = requests.post(
                url=token_url,
                data={
                    "client_id": settings.MS_CLIENT_ID,
                    "client_secret": settings.MS_CLIENT_SECRET,
                    "refresh_token": self.refresh_token,
                    "grant_type": "refresh_token",
                    "scope": settings.MAIL_SCOPE,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

            if refresh_response.status_code == 200:
                logger.info(f"Refresh Response: {refresh_response.json()}")
                tokens = refresh_response.json()
                self.set_tokens(
                    access_token=tokens["access_token"],
                    refresh_token=tokens["refresh_token"],
                    expires_in=tokens["expires_in"]
                )
            else:
                raise Exception("Failed to refresh token. Re-authentication needed.")
        else:
            raise Exception("No refresh token available. Please Re-authentication.")

# global token cache
token_cache = TokenCache()