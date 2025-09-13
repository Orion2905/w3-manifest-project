#!/bin/bash

# W3 Manifest Project - Azure Deployment Script
# Versione bash per macOS/Linux

set -e  # Exit on any error

# Configuration
PROJECT_NAME="w3manifest"
RESOURCE_GROUP="rg-w3-manifest"  # Using existing resource group
LOCATION="West Europe"  # Changed to match existing resources location
ENVIRONMENT="prod"

# Resource Names (matching existing resources)
APP_SERVICE_PLAN="w3manifest-asp-${ENVIRONMENT}"
BACKEND_APP="w3manifest-backend-${ENVIRONMENT}"
FRONTEND_APP="w3manifest-frontend-${ENVIRONMENT}"
SQL_SERVER="w3manifest-sqlserver-${ENVIRONMENT}"
SQL_DATABASE="w3manifest-db"
STORAGE_ACCOUNT="w3manifeststorage${ENVIRONMENT}"

# SQL Configuration
SQL_ADMIN_USER="w3admin"
SQL_ADMIN_PASSWORD="W3Manifest2024!"

echo "🚀 Starting W3 Manifest deployment to Azure..."
echo "📍 Resource Group: $RESOURCE_GROUP"
echo "🌍 Location: $LOCATION"
echo "🏷️  Environment: $ENVIRONMENT"

# Check if resource group exists
echo "📦 Checking/Creating Resource Group..."
if ! az group show --name "$RESOURCE_GROUP" &>/dev/null; then
    echo "Creating Resource Group: $RESOURCE_GROUP"
    az group create --name "$RESOURCE_GROUP" --location "$LOCATION"
else
    echo "Resource Group already exists: $RESOURCE_GROUP"
fi

# Create App Service Plan
echo "🏗️  Creating App Service Plan..."
az appservice plan create \
    --name "$APP_SERVICE_PLAN" \
    --resource-group "$RESOURCE_GROUP" \
    --sku B1 \
    --is-linux \
    || echo "App Service Plan may already exist"

# Create SQL Server
echo "🗄️  Creating SQL Server..."
az sql server create \
    --name "$SQL_SERVER" \
    --resource-group "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --admin-user "$SQL_ADMIN_USER" \
    --admin-password "$SQL_ADMIN_PASSWORD" \
    || echo "SQL Server may already exist"

# Configure SQL Server firewall (allow Azure services)
echo "🔒 Configuring SQL Server firewall..."
az sql server firewall-rule create \
    --resource-group "$RESOURCE_GROUP" \
    --server "$SQL_SERVER" \
    --name "AllowAzureServices" \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 0.0.0.0 \
    || echo "Firewall rule may already exist"

# Create SQL Database
echo "💾 Creating SQL Database..."
az sql db create \
    --resource-group "$RESOURCE_GROUP" \
    --server "$SQL_SERVER" \
    --name "$SQL_DATABASE" \
    --service-objective Basic \
    || echo "SQL Database may already exist"

# Create Storage Account
echo "📁 Creating Storage Account..."
az storage account create \
    --name "$STORAGE_ACCOUNT" \
    --resource-group "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --sku Standard_LRS \
    || echo "Storage Account may already exist"

# Get Storage Connection String
echo "🔗 Getting Storage Connection String..."
STORAGE_CONNECTION_STRING=$(az storage account show-connection-string \
    --name "$STORAGE_ACCOUNT" \
    --resource-group "$RESOURCE_GROUP" \
    --query connectionString --output tsv)

# Create Backend App Service
echo "🐍 Creating Backend App Service (Python)..."
az webapp create \
    --resource-group "$RESOURCE_GROUP" \
    --plan "$APP_SERVICE_PLAN" \
    --name "$BACKEND_APP" \
    --runtime "PYTHON:3.11" \
    || echo "Backend App may already exist"

# Create Frontend App Service  
echo "⚛️  Creating Frontend App Service (Node.js)..."
az webapp create \
    --resource-group "$RESOURCE_GROUP" \
    --plan "$APP_SERVICE_PLAN" \
    --name "$FRONTEND_APP" \
    --runtime "NODE:18-lts" \
    || echo "Frontend App may already exist"

# Configure Backend App Settings
echo "⚙️  Configuring Backend App Settings..."
az webapp config appsettings set \
    --name "$BACKEND_APP" \
    --resource-group "$RESOURCE_GROUP" \
    --settings \
        ENVIRONMENT="$ENVIRONMENT" \
        DATABASE_URL="mssql+pyodbc://${SQL_ADMIN_USER}:${SQL_ADMIN_PASSWORD}@${SQL_SERVER}.database.windows.net:1433/${SQL_DATABASE}?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no" \
        STORAGE_CONNECTION_STRING="$STORAGE_CONNECTION_STRING" \
        FRONTEND_URL="https://${FRONTEND_APP}.azurewebsites.net" \
        SCM_DO_BUILD_DURING_DEPLOYMENT=true \
        ENABLE_ORYX_BUILD=true

# Configure Frontend App Settings
echo "⚙️  Configuring Frontend App Settings..."
az webapp config appsettings set \
    --name "$FRONTEND_APP" \
    --resource-group "$RESOURCE_GROUP" \
    --settings \
        REACT_APP_API_URL="https://${BACKEND_APP}.azurewebsites.net" \
        NODE_ENV="production" \
        SCM_DO_BUILD_DURING_DEPLOYMENT=true \
        ENABLE_ORYX_BUILD=true

# Enable HTTPS only
echo "🔐 Enabling HTTPS only..."
az webapp update --name "$BACKEND_APP" --resource-group "$RESOURCE_GROUP" --https-only true
az webapp update --name "$FRONTEND_APP" --resource-group "$RESOURCE_GROUP" --https-only true

echo ""
echo "✅ Deployment completed!"
echo ""
echo "📋 Resource Information:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Backend URL:     https://${BACKEND_APP}.azurewebsites.net"
echo "🌐 Frontend URL:    https://${FRONTEND_APP}.azurewebsites.net"
echo "🗄️  SQL Server:     ${SQL_SERVER}.database.windows.net"
echo "💾 Database:        ${SQL_DATABASE}"
echo "📁 Storage:         ${STORAGE_ACCOUNT}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 Next Steps:"
echo "1. Deploy your code using:"
echo "   Backend:  az webapp deployment source config-zip --name '$BACKEND_APP' --resource-group '$RESOURCE_GROUP' --src backend.zip"
echo "   Frontend: az webapp deployment source config-zip --name '$FRONTEND_APP' --resource-group '$RESOURCE_GROUP' --src frontend.zip"
echo ""
echo "2. Or configure GitHub Actions for automatic deployment"
echo ""
echo "3. Access your application at: https://${FRONTEND_APP}.azurewebsites.net"
echo ""
echo "⚠️  IMPORTANT: Change the SQL admin password after deployment!"
