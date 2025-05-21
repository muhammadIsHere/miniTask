import base64
import json
import logging
import os
from datetime import datetime, timedelta
import dateutil.parser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_reminder_email(event, context):
    """Cloud Function triggered by Pub/Sub to send task reminders.
    
    Args:
        event (dict): The dictionary with data specific to this type of event.
        context (google.cloud.functions.Context): The Cloud Functions event 
            metadata.
    """
    # Extract the Pub/Sub message
    try:
        pubsub_message = base64.b64decode(event['data']).decode('utf-8')
        message_data = json.loads(pubsub_message)
        
        logger.info(f"Received message: {message_data}")
        
        # Extract task information
        task_id = message_data.get('task_id')
        due_date_str = message_data.get('due_date')
        description = message_data.get('description', 'No description')
        
        if not task_id or not due_date_str:
            logger.error("Missing required fields in message")
            return
        
        # Parse the due date
        due_date = dateutil.parser.parse(due_date_str)
        
        # Check if the task is due today or tomorrow
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        due_date_date = due_date.date()
        
        if due_date_date == today or due_date_date == tomorrow:
            # Log the reminder message
            reminder_msg = f"REMINDER: Task '{description}' (ID: {task_id}) is due on {due_date_date.isoformat()}."
            logger.info(reminder_msg)
            
            # In a real implementation, this is where you would send an email
            # But for this assignment, logging is sufficient
        else:
            logger.info(f"Task {task_id} is not due soon (due on {due_date_date.isoformat()}), no reminder needed.")
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise 