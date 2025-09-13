# Script per deployare usando ARM Template

param(
    [string]$ResourceGroupName = "rg-w3-manifest",
    [string]$Location = "West Europe",
    [string]$ProjectName = "w3manifest",
    [string]$Environment = "prod",
    [string]$TemplateFile = "azure-resources.json"
)

Write-Host "🚀 Deploy infrastruttura usando ARM Template..." -ForegroundColor Green

# Verifica se il file template esiste
$templatePath = Join-Path $PSScriptRoot $TemplateFile
if (-not (Test-Path $templatePath)) {
    Write-Host "❌ File template non trovato: $templatePath" -ForegroundColor Red
    exit 1
}

# Richiedi password SQL
$sqlPassword = Read-Host "Inserisci password per SQL Server Admin" -AsSecureString
$sqlPasswordText = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($sqlPassword))

try {
    # Crea Resource Group se non esiste
    Write-Host "📁 Creazione/verifica Resource Group..." -ForegroundColor Green
    az group create --name $ResourceGroupName --location $Location

    # Deploy ARM Template
    Write-Host "🏗️ Deploy ARM Template..." -ForegroundColor Green
    $deployResult = az deployment group create `
        --resource-group $ResourceGroupName `
        --template-file $templatePath `
        --parameters projectName=$ProjectName environment=$Environment sqlAdminPassword=$sqlPasswordText `
        --output json | ConvertFrom-Json

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Deploy completato con successo!" -ForegroundColor Green
        
        # Mostra gli output
        $outputs = $deployResult.properties.outputs
        Write-Host ""
        Write-Host "📋 URLs delle applicazioni:" -ForegroundColor Yellow
        Write-Host "Backend:  $($outputs.backendUrl.value)" -ForegroundColor Yellow
        Write-Host "Frontend: $($outputs.frontendUrl.value)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "🗄️ Database:" -ForegroundColor Yellow
        Write-Host "Server: $($outputs.sqlServerFqdn.value)" -ForegroundColor Yellow
        Write-Host "Database: $($outputs.databaseName.value)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "📦 Storage: $($outputs.storageAccountName.value)" -ForegroundColor Yellow
    } else {
        throw "Deploy ARM Template fallito"
    }

} catch {
    Write-Host "❌ Errore durante il deploy: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎉 Infrastruttura Azure pronta!" -ForegroundColor Green
