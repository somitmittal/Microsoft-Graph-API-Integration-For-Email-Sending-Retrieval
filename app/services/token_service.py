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
        return self.access_token is not None and self.expiry is not None and datetime.utcnow() < self.expiry

    def set_tokens(self, access_token: str, expires_in: int, refresh_token: Optional[str] = None):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expiry = datetime.utcnow() + timedelta(seconds=expires_in)  # small buffer

    def get_access_token(self):
        if self.is_token_valid():
            return self.access_token
        if self.refresh_token:
            # Refresh using the refresh token
            token_url = f"{settings.MS_AUTHORITY}/oauth2/v2.0/token"
            refresh_response = requests.post(
                url=token_url,
                data={
                    "client_id": settings.MS_CLIENT_ID,
                    "client_secret": settings.MS_CLIENT_SECRET,
                    "refresh_token": self.refresh_token,
                    "grant_type": "refresh_token",
                    "scope": " ".join(settings.MS_SCOPE),
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

            if refresh_response.status_code == 200:
                tokens = refresh_response.json()
                self.set_tokens(
                    access_token=tokens["access_token"],
                    refresh_token=tokens.get("refresh_token"),
                    expires_in=tokens["expires_in"]
                )
            else:
                raise Exception("Failed to refresh token. Re-authentication needed.")
        else:
            raise Exception("No refresh token available. Re-authentication needed.")

# global token cache
token_cache = TokenCache()