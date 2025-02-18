import os
import logging
from pypdf import PdfWriter
from shared.file_share_connection import AzureFileShareManager
from shared.file_utils.list_files import list_files

async def merge_pdfs(folder_structure: dict) -> None:
    try:
        # Initialize file share connection
        connection_string = os.environ["AzureFileShareURI"]
        file_share = AzureFileShareManager(connection_string, "internal")
        await file_share.initialize()

        converted_path = folder_structure['converted_path']
        merge_path = folder_structure['merge_path']
        file_name = folder_structure['file_name']

        # Check if merged file already exists
        dest_path = f"{merge_path}/{file_name}.pdf"
        exists = await file_share.file_exists(dest_path)
        if exists:
            logging.info(f"Merged PDF already exists at {dest_path}, skipping merge")
            await file_share.close()
            return

        # List all PDF files in converted folder
        files = await list_files(file_share, converted_path)
        pdf_files = [os.path.basename(f) for f in files if f.lower().endswith('.pdf')]

        if not pdf_files:
            logging.info("No PDF files found to merge")
            await file_share.close()
            return

        # Create PDF writer
        writer = PdfWriter()

        # Download and merge each PDF
        for pdf_file in pdf_files:
            source_path = f"{converted_path}/{pdf_file}"
            source_file = file_share.share_client.get_file_client(source_path)
            
            # Download PDF content
            downloaded_data = await source_file.download_file()
            pdf_content = await downloaded_data.readall()
            
            # Save temporarily and append to writer
            temp_path = f"/tmp/{pdf_file}"
            with open(temp_path, 'wb') as f:
                f.write(pdf_content)
            
            # Append all pages from this PDF
            writer.append(temp_path)
            os.remove(temp_path)

        # Save merged PDF temporarily
        merged_temp_path = f"/tmp/{file_name}.pdf"
        with open(merged_temp_path, 'wb') as output_file:
            writer.write(output_file)

        # Read merged PDF and upload to merge folder
        with open(merged_temp_path, 'rb') as f:
            merged_content = f.read()

        dest_file = file_share.share_client.get_file_client(dest_path)
        await dest_file.upload_file(merged_content)

        # Clean up merged PDF
        os.remove(merged_temp_path)
        await file_share.close()

        logging.info(f"Successfully merged {len(pdf_files)} PDFs into {dest_path}")

    except Exception as e:
        logging.error(f"Error merging PDFs: {str(e)}")
        # Clean up temp files in case of error
        for f in os.listdir('/tmp'):
            if f.endswith('.pdf'):
                os.remove(f"/tmp/{f}")
        if 'file_share' in locals():
            await file_share.close()
        raise
