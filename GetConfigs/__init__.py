import logging
from shared.db_connection import DBConnection

async def main(msg):
    db_connection = DBConnection()
    try:
        query = "SELECT short_name FROM public.org_details"
        rows = await db_connection.execute_query(query)
        queues = []
        for row in rows:
            # Get short_name from configuration
            short_name = row[0]  # Access tuple element by index instead of key
            if short_name:
                # Create queue names with format: shortname-priority-preprocessor
                queues.append(f"{short_name}-high-preprocessor")
                queues.append(f"{short_name}-medium-preprocessor") 
                queues.append(f"{short_name}-low-preprocessor")
                print(queues)
        return queues
    except Exception as e:
        logging.error(f"Error retrieving config from DB: {e}")