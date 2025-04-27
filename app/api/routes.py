import urllib
import requests
import msal

from fastapi import APIRouter, HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse, HTMLResponse

from app.models.email import EmailSendRequest, EmailResponse
from app.services.email_service import EmailService
from typing import List

from app.services.token_service import token_cache
from config import settings

router = APIRouter()
access_token = {}

@router.post("/email/send", response_model=EmailResponse)
async def send_email_route(email_request: EmailSendRequest):
    """
    Send an email using Microsoft Graph API
    """
    try:
        result = EmailService().send_email(email_request)
        return {"message": "Email sent successfully", "email_id": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/email/retrieve", response_model=List[EmailResponse])
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
        "scope": " ".join(settings.MS_SCOPE),
        "state": "12345"
    }
    auth_url = f"{settings.MS_AUTHORITY}/oauth2/v2.0/authorize?{urllib.parse.urlencode(params)}"
    return RedirectResponse(auth_url)

# Step 2: Handle callback and exchange code for access token
@router.get("/auth/callback")
async def auth_callback(request: Request):
    global access_token
    code = request.query_params.get("code")
    if not code:
        return HTMLResponse(content="Authorization code not found.", status_code=400)

    # token_url = f"{settings.MS_AUTHORITY}/oauth2/v2.0/token"
    # token_data = {
    #     "client_id": settings.MS_CLIENT_ID,
    #     "client_secret": settings.MS_CLIENT_SECRET,
    #     "code": code,
    #     "redirect_uri": settings.REDIRECT_URI,
    #     "grant_type": "authorization_code",
    #     "scope": " ".join(settings.MS_SCOPE),
    # }
    # token_headers = {
    #     "Content-Type": "application/x-www-form-urlencoded"
    # }

    msal_app = msal.ConfidentialClientApplication(
    client_id=settings.MS_CLIENT_ID,
    client_credential=settings.MS_CLIENT_SECRET,
    authority=settings.MS_AUTHORITY
    )

    result = msal_app.acquire_token_by_authorization_code(
    code,  # The authorization code from the redirect
    scopes=["Mail.Send"],
    redirect_uri=settings.REDIRECT_URI
    )
    access_token = result.get("access_token")
    refresh_token = result.get("refresh_token")
    expires_in = result.get("expires_in")
    print(f"Access Token: {access_token}")
    print(f"RESULT: {result}")
    # refresh_token = token_json["refresh_token"]
    # expires_in = token_json["expires_in"]
    # print(f"Access Token: {access_token}")

    # token_response = requests.post(token_url, data=token_data, headers=token_headers)
    # token_json = token_response.json()
    # print(f"Token json:{token_json}")

    # if "access_token" not in token_json:
    #     return HTMLResponse(content=f"Error getting token: {token_json}", status_code=400)
    # access_token = token_json["access_token"]
    # refresh_token = token_json["refresh_token"]
    # expires_in = token_json["expires_in"]
    # print(f"Access Token: {access_token}")
    token_cache.set_tokens(access_token, expires_in, refresh_token)
    return "Authentication Successful"
