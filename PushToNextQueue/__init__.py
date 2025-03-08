import logging
import os
from shared.db_connection import DBConnection
from shared.split_file_name import split_file_name
from shared.QueueManager import QueueManager
from shared.file_utils.move_file import move_file

async def main(msg: dict) -> dict:
    logging.info(f"PushToNextQueue started with message: {msg}")
    queue_manager = None
    db_connection = None
    try:
        processed_results = msg.get("processed_results", [])
        stage = msg.get("stage")
        
        if not processed_results:
            logging.warning("No processed results to push to queue")
            return {"status": "skipped"}

        connection_string = os.environ.get("QUEUE_URI")
        queue_manager = QueueManager(connection_string)
        db_connection = DBConnection()

        for result in processed_results:
            try:
                if isinstance(result, str):
                    result = {'file_name': result}
                
                if not isinstance(result, dict) or 'file_name' not in result:
                    logging.warning(f"Unexpected result format: {result}")
                    continue

                file_info = split_file_name(result['file_name'])
                query = f"SELECT id, loan_no, priority FROM {file_info['vendor']}.loan WHERE unique_id = '{file_info['unique_id']}'"
                rows = await db_connection.execute_query(query)
                
                if not rows:
                    logging.warning(f"No loan found for unique_id: {file_info['unique_id']}")
                    continue

                # Build AIQueueData-compliant message
                message_data = {
                    "unique_id": file_info["unique_id"],
                    "loan_id": rows[0][0],
                    "loan_no": rows[0][1],
                    "vendor": file_info["vendor"],
                    "transaction_id": file_info["transaction_id"],
                    "org_name": file_info["vendor"],
                    "priority": rows[0][2],
                    "image_base_url": f"https://emeraldinternal.file.core.windows.net/internal/opus/secondary/{file_info['unique_id']}/images/high/",
                    "pdf_base_url": f"https://emeraldinternal.file.core.windows.net/internal/opus/secondary/{file_info['unique_id']}/merge/{file_info['file_name']}.pdf"
                }

                # Queue name construction
                # Example: "opus-high-classification"
                queue_name = (
                    f"{file_info['vendor']}-{rows[0][2]}-{stage}"
                    .lower()[:63].ljust(3, 'x')
                )

                # Queue management
                if not await queue_manager.exists(queue_name):
                    await queue_manager.create_queue(queue_name)
                
                # Send validated message
                await queue_manager.send_message(queue_name, message_data)
                logging.info(f"Pushed message to {queue_name}")

                # File movement
                ext = "zip"
                source = f'{file_info["vendor"]}/primary/{file_info["file_name"]}{ext}'
                dest = f'{file_info["vendor"]}/processed/{file_info["file_name"]}{ext}'
                await move_file(source, dest)

            except Exception as e:
                logging.error(f"Error processing result {result}: {str(e)}")
                continue

        return {"status": "completed"}

    except Exception as e:
        logging.error(f"Error in PushToNextQueue: {str(e)}")
        return {"status": "failed", "error": str(e)}
    finally:
        if queue_manager:
            await queue_manager.close()