import os
import logging
from io import BytesIO
import aspose.words as aw
from shared.file_share_connection import AzureFileShareManager

async def convert_word_to_pdf(file_share: AzureFileShareManager, source: str, dest_path: str) -> None:
    try:
        # Extract file details
        file_name = os.path.splitext(os.path.basename(source))[0]
        dest_file_path = f"{dest_path}/{file_name}.pdf"

        # Check if file already exists before processing
        exists = await file_share.file_exists(dest_file_path)
        if exists:
            logging.info(f"PDF already exists, skipping conversion: {file_name}")
            return
        
        # Download the file from Azure
        source_file = file_share.share_client.get_file_client(source)
        word_data = await source_file.download_file()
        word_bytes = await word_data.readall()

        # Convert using Aspose.Words
        with BytesIO(word_bytes) as in_stream:
            # Load document from stream
            doc = aw.Document(in_stream)
            
            # Configure save options for optimization
            save_options = aw.saving.PdfSaveOptions()
            save_options.compliance = aw.saving.PdfCompliance.PDF17
            save_options.embed_full_fonts = True
            
            # Save to memory stream
            with BytesIO() as pdf_stream:
                doc.save(pdf_stream, save_options)
                pdf_bytes = pdf_stream.getvalue()

        # Upload to Azure
        dest_file = file_share.share_client.get_file_client(dest_file_path)
        await dest_file.upload_file(pdf_bytes)
            
        logging.info(f"Converted Word document to PDF successfully: {file_name}")

    except Exception as e:
        logging.error(f"Error converting Word document {source}: {str(e)}")
        raise