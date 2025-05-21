import base64
import json
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_reminder_email(event, context):
    """
    Background Cloud Function to be triggered by Pub/Sub.
    Args:
        event (dict):  The dictionary with data specific to this type of
                       event. The `data` field contains the PubsubMessage.
        context (google.cloud.functions.Context): The Cloud Functions event
                       metadata.
    """
    # Extract the Pub/Sub message
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    logger.info(f"Received message: {pubsub_message}")
    
    try:
        # Parse the JSON message
        task_data = json.loads(pubsub_message)
        
        # Extract task details
        task_id = task_data.get('task_id')
        description = task_data.get('description', 'No description')
        due_date_str = task_data.get('due_date')
        
        if not task_id or not due_date_str:
            logger.error("Missing required fields in task data")
            return
        
        # Parse the due date
        due_date = datetime.fromisoformat(due_date_str)
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        # Check if the task is due today or tomorrow
        if due_date.date() == today or due_date.date() == tomorrow:
            # In a real implementation, this would send an email
            # For now, we'll just log a message
            logger.info(f"REMINDER: Task '{description}' (ID: {task_id}) is due on {due_date_str}.")
        else:
            logger.info(f"Task {task_id} is not due soon (due on {due_date_str})")
            
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Error processing message: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}") 