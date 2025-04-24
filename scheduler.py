from apscheduler.schedulers.background import BackgroundScheduler
from app.services.email_service import retrieve_emails
from config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a scheduler instance
scheduler = BackgroundScheduler()

def start_scheduler():
    """
    Start the background scheduler for periodic email retrieval
    """
    try:
        # Add job to retrieve emails at regular intervals
        scheduler.add_job(
            retrieve_emails,
            'interval',
            seconds=settings.EMAIL_RETRIEVAL_INTERVAL,
            id='retrieve_emails_job',
            replace_existing=True
        )
        
        # Start the scheduler
        if not scheduler.running:
            scheduler.start()
            logger.info(f"Email retrieval scheduler started. Running every {settings.EMAIL_RETRIEVAL_INTERVAL} seconds")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {str(e)}")

def stop_scheduler():
    """
    Stop the background scheduler
    """
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Email retrieval scheduler stopped")