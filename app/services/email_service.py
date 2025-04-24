import requests
import logging
from datetime import datetime, timedelta
from app.repositories.email_repository import EmailRepository
from app.models.email import EmailSendRequest
from app.services.token_service import TokenService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.token_service = TokenService()
        self.email_repository = EmailRepository()

    def send_email(self, email_request: EmailSendRequest):
        """
        Send an email using Microsoft Graph API
        """
        try:
            # Get access token
            access_token = self.token_service.get_access_token()
            
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

    def retrieve_emails(self):
        """
        Retrieve emails from the past 24 hours using Microsoft Graph API
        and store them in MongoDB
        """
        try:
            # Get access token
            access_token = self.token_service.get_access_token()
            
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
                self.email_repository.store_emails(emails_data)
            else:
                logger.error(f"Failed to retrieve emails: {response.text}")
                raise Exception(f"Failed to retrieve emails: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Error retrieving emails: {str(e)}")
            raise e
