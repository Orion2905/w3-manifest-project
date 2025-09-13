# Script semplificato per creazione rapida infrastruttura
# Per testing e sviluppo - usa parametri di default

# Configurazione
$ResourceGroup = "rg-w3-manifest-dev"
$Location = "West Europe"
$Project = "w3manifest"

Write-Host "🚀 Creazione infrastruttura di sviluppo..." -ForegroundColor Green

# Verifica login Azure
$account = az account show 2>$null
if (-not $account) {
    Write-Host "❌ Non sei loggato in Azure. Esegui: az login" -ForegroundColor Red
    exit 1
}

# Crea tutte le risorse con un comando
az group create --name $ResourceGroup --location $Location

# App Service Plan
az appservice plan create --name "$Project-asp-dev" --resource-group $ResourceGroup --location $Location --sku B1 --is-linux

# Backend (Python)
az webapp create --name "$Project-backend-dev" --resource-group $ResourceGroup --plan "$Project-asp-dev" --runtime "PYTHON:3.11"

# Frontend (Node.js)  
az webapp create --name "$Project-frontend-dev" --resource-group $ResourceGroup --plan "$Project-asp-dev" --runtime "NODE:18-lts"

# SQL Server e Database
az sql server create --name "$Project-sql-dev" --resource-group $ResourceGroup --location $Location --admin-user "w3admin" --admin-password "DevPassword123!"
az sql server firewall-rule create --resource-group $ResourceGroup --server "$Project-sql-dev" --name "AllowAzure" --start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0
az sql db create --name "$Project-db" --server "$Project-sql-dev" --resource-group $ResourceGroup --edition "Basic"

# Storage Account
az storage account create --name "$Project" + "storagedev" --resource-group $ResourceGroup --location $Location --sku Standard_LRS

Write-Host "✅ Infrastruttura di sviluppo creata!" -ForegroundColor Green
Write-Host "Backend: https://$Project-backend-dev.azurewebsites.net" -ForegroundColor Yellow
Write-Host "Frontend: https://$Project-frontend-dev.azurewebsites.net" -ForegroundColor Yellow
