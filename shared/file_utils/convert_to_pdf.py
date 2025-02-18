import os
import logging
from shared.file_share_connection import AzureFileShareManager
from shared.file_utils.list_files import list_files
from shared.file_utils.copy_pdf import copy_pdf
from shared.file_utils.convert_file import convert_file
ALLOWED_TYPES = ['.xlsx', '.xls', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.tiff','.csv']

async def convert_to_pdf(folder_structure: dict,file_name: str) -> None:
    try:
        access_path = f"{folder_structure['original_path']}/{file_name}"
        converted_path = folder_structure['converted_path']
        save_path = converted_path
        
        # Initialize Azure File Share connection
        connection_string = os.environ["AzureFileShareURI"] 
        file_share = AzureFileShareManager(connection_string, "internal")
        await file_share.initialize()

        # Get list of files in access path
        files = await list_files(file_share, access_path)
        
        for file in files:
            file_name = os.path.basename(file)
            file_ext = os.path.splitext(file_name)[1].lower()
            
            if file_ext == '.pdf':
                dest_file = f"{save_path}/{os.path.basename(file)}"
                exists = await file_share.file_exists(dest_file)
                if not exists:
                    await copy_pdf(file_share, file, save_path)
            elif file_ext in ALLOWED_TYPES:
                await convert_file(file_share, file, save_path, file_ext)
            else:
                logging.warning(f"Unsupported file type: {file_ext}")

        await file_share.close()

    except Exception as e:
        logging.error(f"Error in convert_to_pdf: {str(e)}")
        raise

