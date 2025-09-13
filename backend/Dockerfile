# Use Azure App Service Python base image
FROM mcr.microsoft.com/appsvc/python:3.11_20230828.3.1

# Set working directory
WORKDIR /home/site/wwwroot

# Install system dependencies
RUN apt-get update && \
    apt-get install -y curl apt-transport-https && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18 && \
    apt-get install -y unixodbc-dev g++ && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application code
COPY . .

# Create startup script
COPY startup.sh /opt/startup/
RUN chmod +x /opt/startup/startup.sh

# Expose port
EXPOSE 8000

# Start the application
CMD ["/opt/startup/startup.sh"]
