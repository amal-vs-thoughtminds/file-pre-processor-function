import os
import zipfile
import logging
from io import BytesIO
from shared.file_share_connection import AzureFileShareManager

def sanitize_filename(filename: str) -> str:
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def sanitize_azure_path(path: str) -> str:
    parts = path.replace("\\", "/").split("/")
    sanitized_parts = [sanitize_filename(part) for part in parts if part not in ["", "."]]
    return "/".join(sanitized_parts)

async def get_unique_file_path(file_share_manager, file_path: str) -> str:
    file_client = file_share_manager.share_client.get_file_client(file_path)
    if not await file_client.exists():
        return file_path
    else:
        dirname = os.path.dirname(file_path)
        basename = os.path.basename(file_path)
        base, ext = os.path.splitext(basename)
        counter = 1
        new_file_name = f"{base}({counter}){ext}"
        new_file_path = os.path.join(dirname, new_file_name) if dirname else new_file_name
        file_client = file_share_manager.share_client.get_file_client(new_file_path)
        while await file_client.exists():
            counter += 1
            new_file_name = f"{base}({counter}){ext}"
            new_file_path = os.path.join(dirname, new_file_name) if dirname else new_file_name
            file_client = file_share_manager.share_client.get_file_client(new_file_path)
        return new_file_path

async def unzip_file(zip_path: str, extract_to: str):
    try:
        connection_string = os.environ["AzureFileShareURI"]
        logging.info(f"Processing zip file: {zip_path} to extract into: {extract_to}")
        print(f"Unzipping file: {zip_path}")
        
        file_share_manager = AzureFileShareManager(connection_string, "internal")
        await file_share_manager.initialize()

        # Verify zip file exists in primary folder
        zip_file_client = file_share_manager.share_client.get_file_client(zip_path)
        if not await zip_file_client.exists():
            raise FileNotFoundError(f"Zip file not found at path: {zip_path}")

        # Download the zip file into memory
        zip_stream = BytesIO()
        data = await zip_file_client.download_file()
        zip_stream.write(await data.readall())
        zip_stream.seek(0)

        # Get the zip file name without extension
        zip_file_name = os.path.basename(zip_path) 
        zip_file_name_without_ext = os.path.splitext(zip_file_name)[0]  

        # Set the base extraction folder as <extract_to>/original/<zip_file_name>
        base_extract_path = os.path.join(extract_to, "original", zip_file_name_without_ext)
        try:
            await file_share_manager.create_folder_structure(base_extract_path)
            logging.info(f"Ensured extract path exists: {base_extract_path}")
        except Exception as e:
            if "ResourceAlreadyExists" in str(e):
                logging.info(f"Extract path already exists: {base_extract_path}")
            else:
                raise

        # Process each entry in the zip file
        with zipfile.ZipFile(zip_stream) as zip_ref:
            for zip_info in zip_ref.infolist():
                # Skip directories (we only want files)
                if zip_info.is_dir():
                    continue

                # Sanitize the zip file entry path
                sanitized_path = sanitize_azure_path(zip_info.filename)

                # Remove leading "original/" if present
                if sanitized_path.lower().startswith("original/"):
                    sanitized_path = sanitized_path[len("original/"):]
                elif sanitized_path.lower() == "original":
                    sanitized_path = ""

                # Extract only the filename (ignore subdirectories)
                file_name = os.path.basename(sanitized_path)
                if not file_name:  # Skip invalid entries
                    continue

                # Create the full target path (directly inside base_extract_path)
                target_path = os.path.join(base_extract_path, file_name)

                # Check if file already exists
                file_client = file_share_manager.share_client.get_file_client(target_path)
                if await file_client.exists():
                    logging.info(f"Skipping existing file: {target_path}")
                    continue

                # Ensure the directory for the file exists (base_extract_path is already created)
                dir_name = os.path.dirname(target_path)
                if dir_name:
                    try:
                        await file_share_manager.create_folder_structure(dir_name)
                    except Exception as e:
                        if "ResourceAlreadyExists" not in str(e):
                            raise

                # Read file data from the zip and upload
                with zip_ref.open(zip_info) as source:
                    file_data = source.read()

                await file_client.upload_file(file_data)
                logging.info(f"Uploaded new file: {target_path}")

        logging.info(f"Successfully unzipped file {zip_path} to {extract_to}")
    except Exception as e:
        logging.error(f"Failed to unzip file {zip_path}: {e}")