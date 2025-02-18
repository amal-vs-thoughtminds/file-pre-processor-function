import os
import logging
from azure.storage.fileshare.aio import ShareServiceClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError

class AzureFileShareManager:
    def __init__(self, connection_string: str, share_name: str):
        self.connection_string = connection_string
        self.share_name = share_name
        self.share_client = None 
        self.service_client = None

        try:
            # Initialize the ShareServiceClient
            self.service_client = ShareServiceClient.from_connection_string(connection_string)
            self.share_client = self.service_client.get_share_client(share_name)
        except Exception as e:
            logging.error(f"Failed to initialize ShareServiceClient: {str(e)}")
            raise

    async def initialize(self):
        try:
            # Check if the share exists
            await self.exists() 
            logging.info(f"Initialized file share: {self.share_name}")
        except Exception as e:
            logging.error(f"Failed to initialize file share connection: {str(e)}")
            raise

    async def exists(self) -> bool:
        try:
            await self.share_client.get_share_properties()
            return True
        except ResourceNotFoundError:
            return False
        except Exception as e:
            logging.error(f"Error checking if share {self.share_name} exists: {str(e)}")
            raise

    async def file_exists(self, file_path: str) -> bool:
        """Check if a file exists in the Azure File Share."""
        try:
            file_client = self.share_client.get_file_client(file_path)
            await file_client.get_file_properties()
            return True
        except ResourceNotFoundError:
            return False
        except Exception as e:
            logging.error(f"Error checking if file {file_path} exists: {str(e)}")
            raise

    async def create_folder_structure(self, path: str):
        if not self.share_client:
            raise Exception("Share client is not initialized.")
        
        directory_client = self.share_client.get_directory_client(path)
        await directory_client.create_directory()

    async def close(self):
        if self.share_client:
            await self.share_client.close()
        if self.service_client:
            await self.service_client.close()

    async def directory_exists(self, path: str) -> bool:
        try:
            if not self.share_client:
                await self.initialize()
            
            directory_client = self.share_client.get_directory_client(path)
            await directory_client.get_directory_properties()
            return True
        except ResourceNotFoundError:
            return False
        except Exception as e:
            logging.error(f"Error checking if directory exists {path}: {str(e)}")
            raise
    async def copy_file(self, source_path: str, dest_path: str) -> None:
        try:
            source_file = self.share_client.get_file_client(source_path)
            dest_file = self.share_client.get_file_client(dest_path)
            
            # Download source file content
            downloaded_data = await source_file.download_file()
            file_content = await downloaded_data.readall()
            
            # Upload to destination
            await dest_file.upload_file(file_content)
            
            logging.info(f"Successfully copied file from {source_path} to {dest_path}")
        except Exception as e:
            logging.error(f"Error copying file from {source_path} to {dest_path}: {str(e)}")
            raise
    async def delete_file(self, file_path: str) -> None:
        """Delete a file from the Azure File Share."""
        try:
            file_client = self.share_client.get_file_client(file_path)
            await file_client.delete_file()
            logging.info(f"Successfully deleted file: {file_path}")
        except Exception as e:
            logging.error(f"Error deleting file {file_path}: {str(e)}")
            raise