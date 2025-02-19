import logging
import os
from shared import split_file_name
from shared.QueueManager import QueueManager  # Ensure this imports the class
from shared.file_utils.move_file import move_file  # Ensure this imports the function

async def main(msg: dict) -> dict:
    logging.info(f"PushToNextQueue started with message: {msg}")
    try:
        processed_results = msg.get("processed_results", [])
        stage = msg.get("stage")
        
        if not processed_results:
            logging.warning("No processed results to push to queue")
            return
            
        connection_string = os.environ.get("QUEUE_URI")
        queue_manager = QueueManager(connection_string)

        for result in processed_results:
            # Ensure result is a dictionary
            logging.info(f"Result: {result}")
            if isinstance(result, str):
                result = {'file_name': result}
            
            if isinstance(result, dict) and 'file_name' in result:
                file_info = split_file_name.split_file_name(result['file_name'])
                

                # Azure Queue Storage has strict naming requirements create use name like vendor-priority-stage
                queue_name = f"{file_info['vendor']}-{file_info['priority']}-{stage}".lower()
                
                # Ensure queue name meets Azure requirements
                if len(queue_name) < 3:
                    queue_name = queue_name.ljust(3, 'x')
                if len(queue_name) > 63:
                    queue_name = queue_name[:63]
                    
                if not await queue_manager.exists(queue_name):
                    await queue_manager.create_queue(queue_name)
                    logging.info(f"Created new queue: {queue_name}")
                
                await queue_manager.send_message(queue_name, result)
                logging.info(f"Pushed message to queue: {queue_name}")
                queue_manager.close()
                source_path = f'{file_info["vendor"]}/primary/{file_info["file_name"]}.zip'
                dest_path = f'{file_info["vendor"]}/processed/{file_info["file_name"]}.zip'
                
                await move_file(source_path, dest_path)
                logging.info(f"Moved file {file_info['file_name']} to processed folder")
            else:
                logging.warning(f"Unexpected result format: {result}")

    except Exception as e:
        logging.error(f"Error in PushToNextQueue: {str(e)}")