import logging
import os
import json
from shared.file_utils.create_folder_path import create_folder_structure
from shared.file_utils.un_zip import unzip_file  
from shared.file_utils.convert_to_pdf import convert_to_pdf
from shared.file_utils.merge_pdfs import merge_pdfs
from shared.file_utils.convert_pdf_to_images import convert_pdf_to_images


async def main(message: dict) -> dict:
    try:
        logging.info("FilePreProcessor started")
        file_name = message.get("file_name")
        unique_id = message.get("unique_id")
        vendor_name = message.get("vendor")
        logging.info(f"Processing file name: {file_name}")
        
        # Create folder structure
        folder_structure = await create_folder_structure(file_name, unique_id, vendor_name)
        logging.info(f"Folder structure created: {folder_structure}")
        
        # Unzip the file
        source_path = f"{folder_structure['primary_path']}/{file_name}.zip"
        destination_path = folder_structure['loan_path']
        await unzip_file(source_path, destination_path)

        # Convert to PDF
        await convert_to_pdf(folder_structure,file_name)

        # Merge PDF files
        await merge_pdfs(folder_structure)

        # Convert PDF to images
        await convert_pdf_to_images(folder_structure)
        return file_name
        
    except Exception as e:
        return 'Error';
