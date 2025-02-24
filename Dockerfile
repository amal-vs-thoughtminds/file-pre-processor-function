# Use the Azure Functions Python base image (platform specified at build time)
# FROM mcr.microsoft.com/azure-functions/python:4-python3.11
FROM mcr.microsoft.com/azure-functions/python:4-python3.11
# Install dependencies including Node.js for npm
RUN apt-get update && \
    apt-get install -y libreoffice build-essential python3-dev curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Azure Functions Core Tools via npm
RUN npm install -g azure-functions-core-tools@4 --unsafe-perm true

# Set environment variables
ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true

# Copy and install Python dependencies
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt || \
    (echo "Ignoring appscript installation error" && \
    sed -i '/appscript/d' /requirements.txt && \
    pip install --no-cache-dir -r /requirements.txt)

# Copy application code
COPY . /home/site/wwwroot

# Set working directory
WORKDIR /home/site/wwwroot

# Expose port (Azure Functions uses 7071 by default)
EXPOSE 7071

# Start Azure Functions runtime
CMD ["func", "start"]