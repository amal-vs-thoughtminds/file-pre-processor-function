from azure.storage.queue.aio import QueueServiceClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
import os
import logging
from typing import List

class QueueManager:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.queue_service_client = QueueServiceClient.from_connection_string(connection_string)

    async def create_queue(self, queue_name: str) -> bool:
        try:
            queue_client = self.queue_service_client.get_queue_client(queue_name)
            await queue_client.create_queue()
            logging.info(f"Queue {queue_name} created successfully")
            return True
        except ResourceExistsError:
            logging.info(f"Queue {queue_name} already exists")
            return False
        except Exception as e:
            logging.error(f"Error creating queue {queue_name}: {str(e)}")
            raise
        finally:
            await queue_client.close()

    async def delete_queue(self, queue_name: str) -> bool:
        try:
            queue_client = self.queue_service_client.get_queue_client(queue_name)
            await queue_client.delete_queue()
            logging.info(f"Queue {queue_name} deleted successfully")
            return True
        except Exception as e:
            logging.error(f"Error deleting queue {queue_name}: {str(e)}")
            raise
        finally:
            await queue_client.close()

    async def get_messages(self, queue_name: str, max_messages: int = 50) -> List[dict]:
        try:
            queue_client = self.queue_service_client.get_queue_client(queue_name)
            messages = []

            # Asynchronously receive messages from the queue
            async for message in queue_client.receive_messages(messages_per_page=max_messages):
                messages.append({
                    'id': message.id,
                    'content': message.content,
                    'pop_receipt': message.pop_receipt,
                    'inserted_on': message.inserted_on
                })

                # Delete the message after processing
                await queue_client.delete_message(message.id, message.pop_receipt)

            logging.info(f"Retrieved and deleted {len(messages)} messages from queue {queue_name}")
            return messages

        except Exception as e:
            logging.error(f"Error getting messages from queue {queue_name}: {str(e)}")
            raise
        finally:
            await queue_client.close()

    async def close(self):
        await self.queue_service_client.close()

    async def exists(self, queue_name: str) -> bool:
        try:
            queue_client = self.queue_service_client.get_queue_client(queue_name)
            await queue_client.get_queue_properties()
            return True
        except Exception as e:
            logging.error(f"Error checking if queue {queue_name} exists: {str(e)}")
            return False
        finally:
            await queue_client.close()

    async def send_message(self, queue_name: str, message: dict):
        queue_client = self.queue_service_client.get_queue_client(queue_name)
        await queue_client.send_message(message)
        logging.info(f"Message sent to queue {queue_name}")
        await queue_client.close()
