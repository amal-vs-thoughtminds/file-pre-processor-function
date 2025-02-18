import os
import logging
from typing import List
from shared.file_share_connection import AzureFileShareManager

async def list_files(file_share: AzureFileShareManager, path: str) -> List[str]:
    """List all files in the given path"""
    try:
        files = []
        async for item in file_share.share_client.get_directory_client(path).list_directories_and_files():
            if not item.is_directory:
                files.append(f"{path}/{item.name}")
        return files
    except Exception as e:
        logging.error(f"Error listing files in {path}: {str(e)}")
        raise