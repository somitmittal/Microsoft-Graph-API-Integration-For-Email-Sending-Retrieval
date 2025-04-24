from fastapi import APIRouter, HTTPException, Depends
from app.models.email import EmailSendRequest, EmailResponse
from app.services.email_service import send_email, retrieve_emails
from typing import List

router = APIRouter()

@router.post("/email/send", response_model=EmailResponse)
async def send_email_route(email_request: EmailSendRequest):
    """
    Send an email using Microsoft Graph API
    """
    try:
        result = send_email(email_request)
        return {"message": "Email sent successfully", "email_id": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/email/retrieve", response_model=List[EmailResponse])
async def retrieve_emails_route():
    """
    Manually trigger email retrieval from Microsoft Graph API
    """
    try:
        emails = retrieve_emails()
        return emails
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))