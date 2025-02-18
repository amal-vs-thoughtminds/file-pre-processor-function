import os
import logging
# Import the function directly from the module
from shared.remove_duplicate import remove_duplicates
from shared.split_file_name import split_file_name  
from shared.QueueManager import QueueManager

async def main(msg):
    queue_name = msg.get("queue_name")
    max_messages = msg.get("max_messages", 32)

    if not queue_name:
        logging.error("Queue name is required.")
        raise ValueError("Queue name is required.")

    # Enforce the maximum limit for messages
    max_messages = min(max_messages, 32)

    try:
        connection_string = os.environ.get("QUEUE_URI")
        queue_manager = QueueManager(connection_string)

        # First check if queue exists
        if await queue_manager.exists(queue_name):
            messages = await queue_manager.get_messages(queue_name, max_messages)
            
            print("Messages:", messages)
            processed_messages = [split_file_name(message['content']) for message in messages]
            return remove_duplicates(processed_messages)
        else:
            logging.warning(f"Queue {queue_name} does not exist")
            return []
    except Exception as e:
        logging.error(f"Error retrieving messages from queue {queue_name}: {e}")
        raise
