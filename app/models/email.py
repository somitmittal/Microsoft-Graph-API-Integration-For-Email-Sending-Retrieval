from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

class EmailSendRequest(BaseModel):
    """Model for sending email requests"""
    to_recipients: List[EmailStr]
    subject: str
    body: str
    cc_recipients: Optional[List[EmailStr]] = Field(default=[])
    bcc_recipients: Optional[List[EmailStr]] = Field(default=[])
    is_html: Optional[bool] = Field(default=False)

class EmailResponse(BaseModel):
    """Model for email response data"""
    message: Optional[str] = None
    email_id: Optional[str] = None
    subject: Optional[str] = None
    sender: Optional[str] = None
    received_datetime: Optional[datetime] = None
    body: Optional[str] = None

class EmailDB(BaseModel):
    """Model for storing emails in MongoDB"""
    email_id: str
    subject: str
    sender: str
    recipients: List[str]
    cc_recipients: List[str] = Field(default=[])
    bcc_recipients: List[str] = Field(default=[])
    body: str
    is_html: bool = False
    received_datetime: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        schema_extra = {
            "example": {
                "email_id": "AAMkAGVmMDEzMTM4LTZmYWUtNDdkNC1hMDZiLTU1OGY5OTZhYmY4OABGAAAAAAAiQ8W967B7TKBjgx9rVEURBwAiIsqMbYjsT5e-T7KzowPTAAAAAAEMAAAiIsqMbYjsT5e-T7KzowPTAAAYbvZuAAA=",
                "subject": "Test Email",
                "sender": "user@example.com",
                "recipients": ["recipient@example.com"],
                "cc_recipients": [],
                "bcc_recipients": [],
                "body": "This is a test email",
                "is_html": False,
                "received_datetime": "2023-05-01T12:00:00Z",
                "created_at": "2023-05-01T12:05:00Z"
            }
        }