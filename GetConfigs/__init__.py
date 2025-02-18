import logging
from shared.db_connection import DBConnection

async def main(msg):
    db_connection = DBConnection()
    try:
        print("i am here")
        query = "SELECT configuration FROM public.resource"
        rows = await db_connection.execute_query(query)
        queues = []
        for row in rows:
            # Extract just the queue names from each configuration
            if row[0].get('high_queue_name'):
                queues.append(row[0]['high_queue_name'])
            if row[0].get('medium_queue_name'):
                queues.append(row[0]['medium_queue_name'])
            if row[0].get('low_queue_name'): 
                queues.append(row[0]['low_queue_name'])
        return queues
    except Exception as e:
        logging.error(f"Error retrieving config from DB: {e}")
        raise