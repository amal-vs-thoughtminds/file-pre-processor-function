import logging
import os
from shared.file_share_connection import AzureFileShareManager

async def move_file(source_path: str, dest_path: str) -> bool:
    try:
        connection_string = os.environ["AzureFileShareURI"]
        file_share_manager = AzureFileShareManager(connection_string, "internal")
        
        # Copy source to destination
        await file_share_manager.copy_file(source_path, dest_path)
        
        # Delete the source file after successful copy
        await file_share_manager.delete_file(source_path)

        logging.info(f"Successfully moved file from {source_path} to {dest_path}")
        return True

    except Exception as e:
        logging.error(f"Error moving file from {source_path} to {dest_path}: {str(e)}")
        return False
