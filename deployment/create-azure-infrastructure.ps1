# Script PowerShell per creare l'infrastruttura Azure per W3 Manifest Project
# Assicurati di aver fatto login con: az login

param(
    [string]$ResourceGroupName = "rg-w3-manifest",
    [string]$Location = "West Europe",
    [string]$ProjectName = "w3manifest",
    [string]$Environment = "prod"
)

# Colori per output
$Green = "Green"
$Yellow = "Yellow"
$Red = "Red"

Write-Host "🚀 Creazione infrastruttura Azure per W3 Manifest Project" -ForegroundColor $Green
Write-Host "=================================================" -ForegroundColor $Green

# Variabili
$BackendAppName = "$ProjectName-backend-$Environment"
$FrontendAppName = "$ProjectName-frontend-$Environment"
$SqlServerName = "$ProjectName-sql-server-$Environment"
$DatabaseName = "$ProjectName-db"
$StorageAccountName = "$ProjectName" + "storage" + $Environment  # Deve essere univoco globalmente
$AppServicePlanName = "$ProjectName-asp-$Environment"

# SQL Admin (CAMBIA QUESTI VALORI!)
$SqlAdminUser = "w3admin"
$SqlAdminPassword = "W3Manifest2024!" # CAMBIA QUESTA PASSWORD!

Write-Host "📋 Configurazione:" -ForegroundColor $Yellow
Write-Host "  Resource Group: $ResourceGroupName" -ForegroundColor $Yellow
Write-Host "  Location: $Location" -ForegroundColor $Yellow
Write-Host "  Backend App: $BackendAppName" -ForegroundColor $Yellow
Write-Host "  Frontend App: $FrontendAppName" -ForegroundColor $Yellow
Write-Host "  SQL Server: $SqlServerName" -ForegroundColor $Yellow
Write-Host "  Storage Account: $StorageAccountName" -ForegroundColor $Yellow

# Conferma prima di procedere
$confirm = Read-Host "Vuoi procedere con la creazione delle risorse? (y/N)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "❌ Operazione annullata" -ForegroundColor $Red
    exit
}

try {
    # 1. Crea Resource Group
    Write-Host "📁 Creazione Resource Group..." -ForegroundColor $Green
    az group create --name $ResourceGroupName --location $Location
    if ($LASTEXITCODE -ne 0) { throw "Errore nella creazione del Resource Group" }

    # 2. Crea App Service Plan
    Write-Host "⚡ Creazione App Service Plan..." -ForegroundColor $Green
    az appservice plan create `
        --name $AppServicePlanName `
        --resource-group $ResourceGroupName `
        --location $Location `
        --sku B1 `
        --is-linux
    if ($LASTEXITCODE -ne 0) { throw "Errore nella creazione dell'App Service Plan" }

    # 3. Crea Backend App Service (Python)
    Write-Host "🐍 Creazione Backend App Service (Python)..." -ForegroundColor $Green
    az webapp create `
        --name $BackendAppName `
        --resource-group $ResourceGroupName `
        --plan $AppServicePlanName `
        --runtime "PYTHON:3.11"
    if ($LASTEXITCODE -ne 0) { throw "Errore nella creazione del Backend App Service" }

    # 4. Crea Frontend App Service (Node.js)
    Write-Host "⚛️ Creazione Frontend App Service (Node.js)..." -ForegroundColor $Green
    az webapp create `
        --name $FrontendAppName `
        --resource-group $ResourceGroupName `
        --plan $AppServicePlanName `
        --runtime "NODE:18-lts"
    if ($LASTEXITCODE -ne 0) { throw "Errore nella creazione del Frontend App Service" }

    # 5. Crea SQL Server
    Write-Host "🗄️ Creazione SQL Server..." -ForegroundColor $Green
    az sql server create `
        --name $SqlServerName `
        --resource-group $ResourceGroupName `
        --location $Location `
        --admin-user $SqlAdminUser `
        --admin-password $SqlAdminPassword
    if ($LASTEXITCODE -ne 0) { throw "Errore nella creazione del SQL Server" }

    # 6. Configura Firewall SQL Server per Azure Services
    Write-Host "🔥 Configurazione Firewall SQL Server..." -ForegroundColor $Green
    az sql server firewall-rule create `
        --resource-group $ResourceGroupName `
        --server $SqlServerName `
        --name "AllowAzureServices" `
        --start-ip-address 0.0.0.0 `
        --end-ip-address 0.0.0.0
    if ($LASTEXITCODE -ne 0) { throw "Errore nella configurazione del Firewall" }

    # 7. Crea Database SQL
    Write-Host "💾 Creazione Database SQL..." -ForegroundColor $Green
    az sql db create `
        --name $DatabaseName `
        --server $SqlServerName `
        --resource-group $ResourceGroupName `
        --edition "Basic" `
        --capacity 5
    if ($LASTEXITCODE -ne 0) { throw "Errore nella creazione del Database" }

    # 8. Crea Storage Account
    Write-Host "📦 Creazione Storage Account..." -ForegroundColor $Green
    az storage account create `
        --name $StorageAccountName `
        --resource-group $ResourceGroupName `
        --location $Location `
        --sku Standard_LRS `
        --kind StorageV2
    if ($LASTEXITCODE -ne 0) { throw "Errore nella creazione dello Storage Account" }

    # 9. Ottieni connection strings
    Write-Host "🔗 Recupero connection strings..." -ForegroundColor $Green
    
    # SQL Connection String
    $sqlConnectionString = "Server=tcp:$SqlServerName.database.windows.net,1433;Initial Catalog=$DatabaseName;Persist Security Info=False;User ID=$SqlAdminUser;Password=$SqlAdminPassword;MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;"
    
    # Storage Connection String
    $storageKey = az storage account keys list --resource-group $ResourceGroupName --account-name $StorageAccountName --query '[0].value' -o tsv
    $storageConnectionString = "DefaultEndpointsProtocol=https;AccountName=$StorageAccountName;AccountKey=$storageKey;EndpointSuffix=core.windows.net"

    # 10. Configura App Settings per Backend
    Write-Host "⚙️ Configurazione App Settings Backend..." -ForegroundColor $Green
    az webapp config appsettings set `
        --name $BackendAppName `
        --resource-group $ResourceGroupName `
        --settings `
        "DATABASE_URL=$sqlConnectionString" `
        "STORAGE_CONNECTION_STRING=$storageConnectionString" `
        "ENVIRONMENT=$Environment" `
        "FRONTEND_URL=https://$FrontendAppName.azurewebsites.net"

    # 11. Configura App Settings per Frontend
    Write-Host "⚙️ Configurazione App Settings Frontend..." -ForegroundColor $Green
    az webapp config appsettings set `
        --name $FrontendAppName `
        --resource-group $ResourceGroupName `
        --settings `
        "REACT_APP_API_URL=https://$BackendAppName.azurewebsites.net" `
        "NODE_ENV=production"

    # 12. Abilita CORS per Backend
    Write-Host "🌐 Configurazione CORS..." -ForegroundColor $Green
    az webapp cors add `
        --name $BackendAppName `
        --resource-group $ResourceGroupName `
        --allowed-origins "https://$FrontendAppName.azurewebsites.net"

    Write-Host ""
    Write-Host "✅ INFRASTRUTTURA CREATA CON SUCCESSO!" -ForegroundColor $Green
    Write-Host "=====================================" -ForegroundColor $Green
    Write-Host ""
    Write-Host "📋 RIEPILOGO RISORSE:" -ForegroundColor $Yellow
    Write-Host "Resource Group: $ResourceGroupName" -ForegroundColor $Yellow
    Write-Host "Backend URL: https://$BackendAppName.azurewebsites.net" -ForegroundColor $Yellow
    Write-Host "Frontend URL: https://$FrontendAppName.azurewebsites.net" -ForegroundColor $Yellow
    Write-Host "SQL Server: $SqlServerName.database.windows.net" -ForegroundColor $Yellow
    Write-Host "Database: $DatabaseName" -ForegroundColor $Yellow
    Write-Host "Storage Account: $StorageAccountName" -ForegroundColor $Yellow
    Write-Host ""
    Write-Host "🔐 CREDENZIALI SQL:" -ForegroundColor $Yellow
    Write-Host "Username: $SqlAdminUser" -ForegroundColor $Yellow
    Write-Host "Password: $SqlAdminPassword" -ForegroundColor $Yellow
    Write-Host ""
    Write-Host "🚀 PROSSIMI STEP:" -ForegroundColor $Green
    Write-Host "1. Configura il deployment automatico da GitHub" -ForegroundColor $Green
    Write-Host "2. Testa le applicazioni" -ForegroundColor $Green
    Write-Host "3. Configura il monitoraggio con Application Insights" -ForegroundColor $Green
    Write-Host ""
    Write-Host "💡 SUGGERIMENTO: Salva le credenziali SQL in un luogo sicuro!" -ForegroundColor $Yellow

} catch {
    Write-Host "❌ Errore durante la creazione dell'infrastruttura: $_" -ForegroundColor $Red
    Write-Host "🧹 Per ripulire le risorse parzialmente create, esegui:" -ForegroundColor $Yellow
    Write-Host "az group delete --name $ResourceGroupName --yes --no-wait" -ForegroundColor $Yellow
    exit 1
}

Write-Host ""
Write-Host "🎉 Setup completato! Buon sviluppo!" -ForegroundColor $Green
