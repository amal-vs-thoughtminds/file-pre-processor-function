import os
import logging
import img2pdf

from shared.file_share_connection import AzureFileShareManager

async def convert_image_to_pdf(file_share: AzureFileShareManager, source: str, dest_path: str) -> None:
    try:
        file_name = os.path.splitext(os.path.basename(source))[0]
        dest_file_path = f"{dest_path}/{file_name}.pdf"
        
        exists = await file_share.file_exists(dest_file_path)
        if exists:
            logging.info(f"PDF already exists, skipping conversion: {file_name}")
            return
            
        source_file = file_share.share_client.get_file_client(source)
        
        image_data = await source_file.download_file()
        
        image_bytes = await image_data.readall()
        
        # Convert to PDF with A4 size (210mm x 297mm)
        a4_layout = img2pdf.get_layout_fun((img2pdf.mm_to_pt(210), img2pdf.mm_to_pt(297)))
        pdf_bytes = img2pdf.convert(image_bytes, layout_fun=a4_layout)
        
        dest_file = file_share.share_client.get_file_client(dest_file_path)
        await dest_file.upload_file(pdf_bytes)
        
        logging.info(f"Converted image to A4 PDF: {file_name}")
    except Exception as e:
        logging.error(f"Error converting image {source}: {str(e)}")
        raise