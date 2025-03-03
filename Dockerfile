FROM --platform=linux/amd64 mcr.microsoft.com/azure-functions/python:4-python3.11
ENV AzureWebJobsScriptRoot=/home/site/wwwroot
ENV AzureFunctionsJobHost__functions__logs=/home/site/wwwroot/logs
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt && \
    pip install --upgrade pip
COPY . /home/site/wwwroot