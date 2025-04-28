from math import log
import urllib
import requests
import logging
import msal

from fastapi import APIRouter, HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse, HTMLResponse

from app.models.email import EmailSendRequest, EmailResponse
from app.services.email_service import EmailService
from typing import Any, List

from app.services.token_service import token_cache
from config import settings

router = APIRouter()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@router.post("/email/send", response_model=EmailResponse)
async def send_email_route(email_request: EmailSendRequest):
    """
    Send an email using Microsoft Graph API
    """
    try:
        result = EmailService().send_email(email_request)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/email/retrieve", response_model=List[Any])
async def retrieve_emails_route():
    """
    Manually trigger email retrieval from Microsoft Graph API
    """
    try:
        emails = EmailService().retrieve_emails()
        return emails
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Step 1: Redirect to Microsoft's login page
@router.get("/auth/login")
async def login():
    params = {
        "client_id": settings.MS_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": settings.REDIRECT_URI,
        "response_mode": "query",
        "scope": settings.MS_SCOPE,
        "state": "12345"
    }
    auth_url = f"{settings.MS_AUTHORITY}/oauth2/v2.0/authorize?{urllib.parse.urlencode(params)}"
    logger.debug(f"Auth URL: {auth_url}")
    return RedirectResponse(auth_url)

# Step 2: Handle callback and exchange code for access token
@router.get("/auth/callback")
async def auth_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return HTMLResponse(content="Authorization code not found.", status_code=400)

    msal_app = msal.ConfidentialClientApplication(
    client_id=settings.MS_CLIENT_ID,
    client_credential=settings.MS_CLIENT_SECRET,
    authority=settings.MS_AUTHORITY
    )

    result = msal_app.acquire_token_by_authorization_code(
    code,  # The authorization code from the redirect
    scopes=["Mail.Send", "Mail.Read"],
    redirect_uri=settings.REDIRECT_URI
    )
    access_token = result.get("access_token")
    refresh_token = result.get("refresh_token")
    expires_in = result.get("expires_in")
    if not access_token:
        return HTMLResponse(content="Failed to retrieve access token.", status_code=400)
    token_cache.set_tokens(access_token, expires_in, refresh_token)
    return "Authentication Successful"
