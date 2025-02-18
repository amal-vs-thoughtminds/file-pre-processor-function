import os
import logging
from shared.file_share_connection import AzureFileShareManager

async def create_folder_structure(file_name: str, unique_id: str, vendor_name: str) -> dict:
    try:
        # Initialize the Azure File Share Manager
        connection_string = os.environ["AzureFileShareURI"]
        file_share_manager = AzureFileShareManager(connection_string, f"internal")

        await file_share_manager.initialize()
        # Create directory paths
        vendor_path = f"{vendor_name}"
        bin_path = f"{vendor_path}/bin"
        processed_path = f"{vendor_path}/processed"
        primary_path = f"{vendor_path}/primary"
        secondary_path = f"{vendor_path}/secondary"
        loan_path = f"{secondary_path}/{unique_id}"
        original_path = f"{loan_path}/original" 
        merge_path = f"{loan_path}/merge"
        images_path = f"{loan_path}/images"
        converted_path = f"{original_path}/converted"
        high_images_path = f"{images_path}/high"
        low_images_path = f"{images_path}/low"

        # Create directories using the manager and verify they exist
        for path in [primary_path, secondary_path, loan_path, original_path, merge_path, images_path, bin_path, processed_path, converted_path, high_images_path, low_images_path]:
            try:
                await file_share_manager.create_folder_structure(path)
                exists = await file_share_manager.directory_exists(path)
                if exists:
                    logging.info(f"Verified path created: {path}")
                    print(f"Created and verified path: {path}")
                else:
                    raise Exception(f"Failed to create path: {path}")
            except Exception as e:
                if "ResourceAlreadyExists" in str(e):
                    logging.info(f"Path already exists: {path}")
                    print(f"Path already exists: {path}")
                else:
                    logging.error(f"Failed to create folder structure for path {path}: {str(e)}")
                    raise

        # Close connection after all folders are created
        await file_share_manager.close()

        return {
            "primary_path": primary_path,
            "secondary_path": secondary_path,
            "loan_path": loan_path,
            "original_path": original_path,
            "merge_path": merge_path,
            "images_path": images_path,
            "file_name": file_name,
            "bin_path": bin_path,
            "processed_path": processed_path,
            "converted_path": converted_path,
            "high_images_path": high_images_path,
            "low_images_path": low_images_path
        }

    except Exception as e:
        logging.error(f"Failed to create folder structure: {str(e)}")
        raise
