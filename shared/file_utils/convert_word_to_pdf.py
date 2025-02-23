import os
import logging
import subprocess
import tempfile
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

        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_word = os.path.join(temp_dir, f"{file_name}.docx")
            temp_pdf = os.path.join(temp_dir, f"{file_name}.pdf")

            # Download the file from Azure
            source_file = file_share.share_client.get_file_client(source)
            word_data = await source_file.download_file()
            word_bytes = await word_data.readall()
            
            # Write word file to temp location
            with open(temp_word, 'wb') as f:
                f.write(word_bytes)

            # Convert using LibreOffice with optimized settings
            cmd = [
                'soffice',
                '--headless',
                '--convert-to', 'pdf:writer_pdf_Export',
                '--outdir', temp_dir,
                temp_word
            ]
            process = subprocess.run(cmd, capture_output=True, text=True)

            if process.returncode != 0:
                raise Exception(f"LibreOffice conversion failed: {process.stderr}")

            # Read the converted PDF
            with open(temp_pdf, 'rb') as pdf_file:
                pdf_bytes = pdf_file.read()

            # Upload to Azure
            dest_file = file_share.share_client.get_file_client(dest_file_path)
            await dest_file.upload_file(pdf_bytes)

        logging.info(f"Converted Word document to PDF successfully: {file_name}")

    except Exception as e:
        logging.error(f"Error converting Word document {source}: {str(e)}")
        raise