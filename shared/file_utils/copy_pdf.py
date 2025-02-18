import os
import logging
from shared.file_share_connection import AzureFileShareManager

async def copy_pdf(file_share: AzureFileShareManager, source: str, dest_path: str) -> None:
    """Copy PDF file to destination"""
    try:
        file_name = os.path.basename(source)
        dest = f"{dest_path}/{file_name}"
        
        source_file = file_share.share_client.get_file_client(source)
        dest_file = file_share.share_client.get_file_client(dest)
        
        # Download the file data
        downloaded_data = await source_file.download_file()
        file_content = await downloaded_data.readall()  # Read the content into memory
        
        # Upload the file content to the destination
        await dest_file.upload_file(file_content)
        
        logging.info(f"Copied PDF: {file_name}")
    except Exception as e:
        logging.error(f"Error copying PDF {source}: {str(e)}")
        raise