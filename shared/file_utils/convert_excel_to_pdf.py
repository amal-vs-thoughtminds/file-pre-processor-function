import os
import logging
import pandas as pd
import matplotlib.pyplot as plt
import img2pdf
from shared.file_share_connection import AzureFileShareManager

async def convert_excel_to_pdf(file_share: AzureFileShareManager, source: str, dest_path: str) -> None:

    try:
        file_name = os.path.splitext(os.path.basename(source))[0]
        file_ext = os.path.splitext(source)[1].lower()
        dest_file_path = f"{dest_path}/{file_name}.pdf"

        # Check if file already exists before processing
        exists = await file_share.file_exists(dest_file_path)
        if exists:
            logging.info(f"PDF already exists, skipping conversion: {file_name}")
            return

        source_file = file_share.share_client.get_file_client(source)
        
        # Download file
        file_data = await source_file.download_file()
        file_bytes = await file_data.readall()
        
        # Create temporary files for image and PDF
        temp_file = f"/tmp/{file_name}{file_ext}"
        temp_image = f"/tmp/{file_name}.png"
        temp_pdf = f"/tmp/{file_name}.pdf"
        
        # Save data to temp file
        with open(temp_file, 'wb') as f:
            f.write(file_bytes)
            
        # Read the file based on extension with optimized settings
        if file_ext in ['.xlsx', '.xls']:
            df = pd.read_excel(temp_file)
        else:  # CSV
            df = pd.read_csv(temp_file, encoding='utf-8', on_bad_lines='skip', low_memory=True)

        # Apply common optimizations for both Excel and CSV
        if len(df.columns) > 8:
            df = df.iloc[:, :8]
            logging.warning(f"File {file_name} truncated to 8 columns")
            
        # Drop rows with all NaN values and limit to 50 rows
        df = df.dropna(how='all').head(50)
        logging.info(f"File {file_name} limited to 50 rows")
            
        # Skip empty dataframes
        if df.empty:
            logging.warning(f"File {file_name} is empty, skipping conversion")
            return
            
        # Convert to image with A4 size (210mm × 297mm)
        fig, ax = plt.subplots(figsize=(8.27, 11.69))
        ax.axis('tight')
        ax.axis('off')
        
        # Create table with data
        table = ax.table(cellText=df.values, 
                        colLabels=df.columns, 
                        cellLoc='center', 
                        loc='center')
        
        # Adjust table properties for better visibility
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.2, 1.5)
        
        # Save as image with compression
        plt.savefig(temp_image, bbox_inches='tight', pad_inches=0.05, dpi=300)
        plt.close()
        
        # Convert image to PDF using img2pdf with A4 layout
        a4_layout = img2pdf.get_layout_fun((img2pdf.mm_to_pt(210), img2pdf.mm_to_pt(297)))
        with open(temp_pdf, "wb") as f:
            f.write(img2pdf.convert(temp_image, layout_fun=a4_layout))

        # Read PDF bytes
        with open(temp_pdf, "rb") as f:
            pdf_bytes = f.read()
            
        # Upload to Azure
        dest_file = file_share.share_client.get_file_client(dest_file_path)
        await dest_file.upload_file(pdf_bytes)
        
        # Clean up temp files
        os.remove(temp_file)
        os.remove(temp_image)
        os.remove(temp_pdf)
        
        logging.info(f"Converted {file_ext[1:].upper()} to PDF: {file_name}")
    except Exception as e:
        # Clean up temp files in case of error
        for temp_file in [f"/tmp/{file_name}{file_ext}", f"/tmp/{file_name}.png", f"/tmp/{file_name}.pdf"]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        logging.error(f"Error converting file {source}: {str(e)}")
        raise