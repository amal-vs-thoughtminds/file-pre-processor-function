# Project Title: Azure Durable Functions File Processing

## Description
This project is an Azure Durable Functions application designed for pre-processing files. It includes functionalities for converting various file types (images, Word documents, Excel spreadsheets) to PDF, merging PDFs, and converting PDFs to images. The application utilizes Azure File Share for file storage and Azure Durable Functions for orchestrating workflows.

## Features
- Convert images to PDF.
- Convert Word documents to PDF.
- Convert Excel files to PDF.
- Merge multiple PDFs into a single document.
- Convert PDF pages to high and low-quality images.
- List files in Azure File Share.
- Create folder structures in Azure File Share.

## Architecture
The application is structured around Azure Durable Functions, which manage the orchestration of file processing tasks. The main components include:
- **Orchestrator**: Manages the workflow of file processing.
- **Activities**: Individual tasks such as file conversion, merging, and listing files.
- **File Share Connection**: Handles interactions with Azure File Share.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/amal-vs-thoughtminds/file-pre-processor-function.git
   cd file-pre-processor-function
   ```

2. **Set up a virtual environment** (optional but recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use .venv\Scripts\activate
   ```

3. **Install the required packages**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Azure credentials**:
   - Create a `local.settings.json` file in the root directory with the following structure:
   ```json
   {
       "IsEncrypted": false,
       "Values": {
           "AzureFileShareURI": "your_azure_file_share_connection_string",
           "DB_CONNECTION_STRING": "your_database_connection_string"
       }
   }
   ```

## Usage

### Running the Functions
- Deploy the functions to Azure or run them locally using Azure Functions Core Tools.
- Trigger the orchestrator function to start the file processing workflow.

### Example Workflow
1. Upload files to the Azure File Share.
2. Trigger the orchestrator function with the necessary parameters.
3. The orchestrator will call the appropriate activity functions to process the files.



## Acknowledgments
- Azure Functions documentation for guidance on serverless architecture.
- Various libraries used for file processing, including `img2pdf`, `aspose.words`, and `pypdf`.
