import msal
import logging
from datetime import datetime, timedelta
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TokenService:
    _access_token = None
    _token_expiration = None

    def get_access_token():
        """
        Get Microsoft Graph API access token using MSAL
        """

        try:
            # Check if the token is still valid
            if datetime.utcnow() < _token_expiration:
                return _access_token

            # Create a confidential client application
            app = msal.ConfidentialClientApplication(
                client_id=settings.MS_CLIENT_ID,
                client_credential=settings.MS_CLIENT_SECRET,
                authority=settings.MS_AUTHORITY
            )
            
            # Acquire token for Microsoft Graph API
            result = app.acquire_token_for_client(scopes=settings.MS_SCOPE)
            
            if "access_token" in result:
                _access_token = result["access_token"]
                # Set token expiration time (assuming token is valid for 1 hour)
                _token_expiration = datetime.utcnow() + timedelta(seconds=result.get("expires_in", 3600))
                return _access_token
            else:
                logger.error(f"Failed to acquire token: {result.get('error')}, {result.get('error_description')}")
                raise Exception(f"Failed to acquire token: {result.get('error')}")
        except Exception as e:
            logger.error(f"Error getting access token: {str(e)}")
            raise e
