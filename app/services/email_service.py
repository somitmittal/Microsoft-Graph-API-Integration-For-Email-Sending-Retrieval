import requests
import msal
import logging
from datetime import datetime, timedelta
from config import settings
from app.models.email import EmailSendRequest, EmailResponse, EmailDB
from app.db.mongodb import get_email_collection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_access_token():
    """
    Get Microsoft Graph API access token using MSAL
    """
    try:
        # Create a confidential client application
        app = msal.ConfidentialClientApplication(
            client_id=settings.MS_CLIENT_ID,
            client_credential=settings.MS_CLIENT_SECRET,
            authority=settings.MS_AUTHORITY
        )
        
        # Acquire token for Microsoft Graph API
        result = app.acquire_token_for_client(scopes=settings.MS_SCOPE)
        
        if "access_token" in result:
            return result["access_token"]
        else:
            logger.error(f"Failed to acquire token: {result.get('error')}, {result.get('error_description')}")
            raise Exception(f"Failed to acquire token: {result.get('error')}")
    except Exception as e:
        logger.error(f"Error getting access token: {str(e)}")
        raise

def send_email(email_request: EmailSendRequest):
    """
    Send an email using Microsoft Graph API
    """
    try:
        # Get access token
        access_token = get_access_token()
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Prepare email message
        email_body = {
            "message": {
                "subject": email_request.subject,
                "body": {
                    "contentType": "html" if email_request.is_html else "text",
                    "content": email_request.body
                },
                "toRecipients": [{
                    "emailAddress": {
                        "address": recipient
                    }
                } for recipient in email_request.to_recipients],
                "ccRecipients": [{
                    "emailAddress": {
                        "address": recipient
                    }
                } for recipient in email_request.cc_recipients],
                "bccRecipients": [{
                    "emailAddress": {
                        "address": recipient
                    }
                } for recipient in email_request.bcc_recipients]
            },
            "saveToSentItems": "true"
        }
        
        # Send the email
        response = requests.post(
            "https://graph.microsoft.com/v1.0/me/sendMail",
            headers=headers,
            json=email_body
        )
        
        # Check response
        if response.status_code == 202:
            logger.info(f"Email sent successfully to {email_request.to_recipients}")
            return "email_sent_successfully"
        else:
            logger.error(f"Failed to send email: {response.text}")
            raise Exception(f"Failed to send email: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise

def retrieve_emails():
    """
    Retrieve emails from the past 24 hours using Microsoft Graph API
    and store them in MongoDB
    """
    try:
        # Get access token
        access_token = get_access_token()
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Calculate date for the past 24 hours
        past_24_hours = datetime.utcnow() - timedelta(days=1)
        date_filter = past_24_hours.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Query parameters
        params = {
            "$filter": f"receivedDateTime ge {date_filter}",
            "$select": "id,subject,sender,toRecipients,ccRecipients,bccRecipients,body,receivedDateTime",
            "$top": 50  # Limit to 50 emails
        }
        
        # Get emails
        response = requests.get(
            "https://graph.microsoft.com/v1.0/me/messages",
            headers=headers,
            params=params
        )
        
        # Check response
        if response.status_code == 200:
            emails_data = response.json().get("value", [])
            logger.info(f"Retrieved {len(emails_data)} emails from the past 24 hours")
            
            # Get MongoDB collection
            email_collection = get_email_collection()
            
            # Process and store emails
            stored_emails = []
            for email in emails_data:
                # Extract email data
                email_id = email.get("id")
                subject = email.get("subject", "")
                sender = email.get("sender", {}).get("emailAddress", {}).get("address", "")
                to_recipients = [r.get("emailAddress", {}).get("address", "") for r in email.get("toRecipients", [])]
                cc_recipients = [r.get("emailAddress", {}).get("address", "") for r in email.get("ccRecipients", [])]
                bcc_recipients = [r.get("emailAddress", {}).get("address", "") for r in email.get("bccRecipients", [])]
                body = email.get("body", {}).get("content", "")
                is_html = email.get("body", {}).get("contentType", "") == "html"
                received_datetime = email.get("receivedDateTime")
                
                # Create email document
                email_doc = EmailDB(
                    email_id=email_id,
                    subject=subject,
                    sender=sender,
                    recipients=to_recipients,
                    cc_recipients=cc_recipients,
                    bcc_recipients=bcc_recipients,
                    body=body,
                    is_html=is_html,
                    received_datetime=received_datetime
                )
                
                # Check if email already exists in the database
                existing_email = email_collection.find_one({"email_id": email_id})
                if not existing_email:
                    # Insert email into MongoDB
                    email_collection.insert_one(email_doc.dict())
                    logger.info(f"Stored email with ID: {email_id}")
                    
                    # Add to response
                    stored_emails.append(EmailResponse(
                        message="Email retrieved and stored",
                        email_id=email_id,
                        subject=subject,
                        sender=sender,
                        received_datetime=received_datetime,
                        body=body[:100] + "..." if len(body) > 100 else body
                    ))
            
            return stored_emails
        else:
            logger.error(f"Failed to retrieve emails: {response.text}")
            raise Exception(f"Failed to retrieve emails: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Error retrieving emails: {str(e)}")
        raise