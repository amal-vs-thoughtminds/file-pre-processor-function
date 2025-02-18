import os
import logging
from PIL import Image
import fitz
from shared.file_share_connection import AzureFileShareManager

async def convert_pdf_to_images(folder_structure: dict) -> None:
    """Convert merged PDF to individual page images in high and low quality"""
    try:
        # Initialize file share connection
        connection_string = os.environ["AzureFileShareURI"]
        file_share = AzureFileShareManager(connection_string, "internal")
        await file_share.initialize()

        merge_path = folder_structure['merge_path']
        high_images_path = folder_structure['high_images_path']
        low_images_path = folder_structure['low_images_path']
        file_name = folder_structure['file_name']

        pdf_path = f"{merge_path}/{file_name}.pdf"

        exists = await file_share.file_exists(pdf_path)
        if not exists:
            logging.error(f"Source PDF not found at {pdf_path}")
            await file_share.close()
            return

        pdf_file = file_share.share_client.get_file_client(pdf_path)
        pdf_data = await pdf_file.download_file()
        pdf_bytes = await pdf_data.readall()

        temp_pdf = f"/tmp/{file_name}.pdf"
        with open(temp_pdf, 'wb') as f:
            f.write(pdf_bytes)

        doc = fitz.open(temp_pdf)
        for i, page in enumerate(doc, start=1):
            pix = page.get_pixmap()
            pix = page.get_pixmap()
            temp_high_path = f"/tmp/high_{i}.jpg"
            pix.save(temp_high_path)

            # Create low quality thumbnail using PIL
            with Image.open(temp_high_path) as img:
                # Resize to smaller dimensions for thumbnail
                img.thumbnail((800, 800))
                temp_low_path = f"/tmp/low_{i}.jpg"
                img.save(temp_low_path, "JPEG", quality=50)

            # Upload high quality image
            with open(temp_high_path, 'rb') as f:
                high_image_bytes = f.read()
            high_dest_path = f"{high_images_path}/{i}.jpg"
            high_dest_file = file_share.share_client.get_file_client(high_dest_path)
            await high_dest_file.upload_file(high_image_bytes)

            # Upload low quality thumbnail
            with open(temp_low_path, 'rb') as f:
                low_image_bytes = f.read()
            low_dest_path = f"{low_images_path}/{i}.jpg"
            low_dest_file = file_share.share_client.get_file_client(low_dest_path)
            await low_dest_file.upload_file(low_image_bytes)

            # Clean up temp files
            os.remove(temp_high_path)
            os.remove(temp_low_path)

        # Clean up temp PDF
        doc.close()
        os.remove(temp_pdf)

        await file_share.close()
        logging.info(f"Successfully converted PDF to {i} high and low quality images")

    except Exception as e:
        logging.error(f"Error converting PDF to images: {str(e)}")
        # Clean up temp files in case of error
        for f in os.listdir('/tmp'):
            if f.endswith(('.jpg', '.pdf')):
                os.remove(f"/tmp/{f}")
        if 'file_share' in locals():
            await file_share.close()
        raise
