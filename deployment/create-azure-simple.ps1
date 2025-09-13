# Script PowerShell semplificato per Azure Infrastructure
param(
    [string]$ResourceGroupName = "rg-w3-manifest",
    [string]$Location = "West Europe", 
    [string]$ProjectName = "w3manifest",
    [string]$Environment = "prod"
)

Write-Host "🚀 Creazione infrastruttura Azure per W3 Manifest Project" -ForegroundColor Green

# Variabili
$BackendAppName = "$ProjectName-backend-$Environment"
$FrontendAppName = "$ProjectName-frontend-$Environment"  
$SqlServerName = "$ProjectName-sql-server-$Environment"
$DatabaseName = "$ProjectName-db"
$StorageAccountName = "$ProjectName" + "storage" + $Environment
$AppServicePlanName = "$ProjectName-asp-$Environment"
$SqlAdminUser = "w3admin"
$SqlAdminPassword = "W3Manifest2024!"

Write-Host "📋 Configurazione:" -ForegroundColor Yellow
Write-Host "  Resource Group: $ResourceGroupName"
Write-Host "  Backend App: $BackendAppName"
Write-Host "  Frontend App: $FrontendAppName"
Write-Host "  SQL Server: $SqlServerName"

$confirm = Read-Host "Vuoi procedere? (y/N)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "Operazione annullata" -ForegroundColor Red
    exit
}

# 1. Resource Group
Write-Host "📁 Creazione Resource Group..." -ForegroundColor Green
az group create --name $ResourceGroupName --location $Location

# 2. App Service Plan  
Write-Host "⚡ Creazione App Service Plan..." -ForegroundColor Green
az appservice plan create --name $AppServicePlanName --resource-group $ResourceGroupName --location $Location --sku B1 --is-linux

# 3. Backend App Service
Write-Host "🐍 Creazione Backend App Service..." -ForegroundColor Green
az webapp create --name $BackendAppName --resource-group $ResourceGroupName --plan $AppServicePlanName --runtime "PYTHON:3.11"

# 4. Frontend App Service
Write-Host "⚛️ Creazione Frontend App Service..." -ForegroundColor Green  
az webapp create --name $FrontendAppName --resource-group $ResourceGroupName --plan $AppServicePlanName --runtime "NODE:18-lts"

# 5. SQL Server
Write-Host "🗄️ Creazione SQL Server..." -ForegroundColor Green
az sql server create --name $SqlServerName --resource-group $ResourceGroupName --location $Location --admin-user $SqlAdminUser --admin-password $SqlAdminPassword

# 6. SQL Firewall  
Write-Host "🔥 Configurazione Firewall..." -ForegroundColor Green
az sql server firewall-rule create --resource-group $ResourceGroupName --server $SqlServerName --name "AllowAzureServices" --start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0

# 7. Database
Write-Host "💾 Creazione Database..." -ForegroundColor Green
az sql db create --name $DatabaseName --server $SqlServerName --resource-group $ResourceGroupName --edition "Basic" --capacity 5

# 8. Storage Account
Write-Host "📦 Creazione Storage Account..." -ForegroundColor Green
az storage account create --name $StorageAccountName --resource-group $ResourceGroupName --location $Location --sku Standard_LRS --kind StorageV2

Write-Host ""
Write-Host "✅ INFRASTRUTTURA CREATA!" -ForegroundColor Green
Write-Host "Backend URL: https://$BackendAppName.azurewebsites.net" -ForegroundColor Yellow
Write-Host "Frontend URL: https://$FrontendAppName.azurewebsites.net" -ForegroundColor Yellow
Write-Host "SQL Server: $SqlServerName.database.windows.net" -ForegroundColor Yellow
Write-Host "Database: $DatabaseName" -ForegroundColor Yellow
Write-Host ""
Write-Host "🔐 Credenziali SQL:" -ForegroundColor Yellow
Write-Host "Username: $SqlAdminUser" -ForegroundColor Yellow
Write-Host "Password: $SqlAdminPassword" -ForegroundColor Yellow
