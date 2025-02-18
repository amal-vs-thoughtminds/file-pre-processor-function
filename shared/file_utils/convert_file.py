from shared.file_share_connection import AzureFileShareManager
from shared.file_utils.convert_image_to_pdf import convert_image_to_pdf
from shared.file_utils.convert_excel_to_pdf import convert_excel_to_pdf
from shared.file_utils.convert_word_to_pdf import convert_word_to_pdf
import logging  

async def convert_file(file_share: AzureFileShareManager, source: str, dest_path: str, file_ext: str) -> None:
    """Convert file to PDF based on extension"""
    try:
        if file_ext in ['.jpg', '.jpeg', '.png', '.tiff']:
            await convert_image_to_pdf(file_share, source, dest_path)
        elif file_ext in ['.xlsx', '.xls','.csv']:
            await convert_excel_to_pdf(file_share, source, dest_path)
        elif file_ext in ['.doc', '.docx']:
            await convert_word_to_pdf(file_share, source, dest_path)
    except Exception as e:
        logging.error(f"Error converting file {source}: {str(e)}")
        raise