import logging

from app.db.mongodb import get_email_collection
from app.models.email import EmailDB, EmailResponse

logger = logging.getLogger(__name__)
class EmailRepository:
    def __init__(self):
        # Set MongoDB collection
        self.collection = get_email_collection()

    def store_emails(self, emails_data):
        # Process and store emails
        stored_emails = []
        email_docs = []
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
            email_docs.append(email_doc)

            # Add to response
            stored_emails.append(EmailResponse(
                message="Email retrieved and stored",
                email_id=email_id,
                subject=subject,
                sender=sender,
                received_datetime=received_datetime,
                body=body
            ))
        try:
            self.collection.insert_many(email_docs)
        except Exception as e:
            logger.error(f"Failed to store emails: {e}")
            raise e
        return stored_emails
        