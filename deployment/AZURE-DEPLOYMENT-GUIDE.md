# Guida al Deployment su Azure

## 🚀 Script Disponibili

### 1. **create-azure-infrastructure.ps1** (Raccomandato)
Script completo e interattivo per creare tutta l'infrastruttura.

**Uso:**
```powershell
.\deployment\create-azure-infrastructure.ps1
```

**Con parametri personalizzati:**
```powershell
.\deployment\create-azure-infrastructure.ps1 -ResourceGroupName "mio-rg" -Location "North Europe" -Environment "dev"
```

### 2. **quick-setup.ps1**
Setup rapido per sviluppo con configurazioni predefinite.

```powershell
.\deployment\quick-setup.ps1
```

### 3. **deploy-arm-template.ps1**
Deployment usando ARM Template per maggiore controllo.

```powershell
.\deployment\deploy-arm-template.ps1
```

## 📋 Prerequisiti

1. **Azure CLI installato e configurato**
   ```powershell
   # Installa Azure CLI
   winget install Microsoft.AzureCLI
   
   # Login
   az login
   
   # Verifica sottoscrizione
   az account show
   ```

2. **Privilegi di creazione risorse** sulla sottoscrizione Azure

## 🏗️ Risorse Create

| Risorsa | Tipo | Scopo |
|---------|------|-------|
| **App Service Plan** | Linux B1 | Hosting per backend e frontend |
| **Backend App Service** | Python 3.11 | API REST |
| **Frontend App Service** | Node.js 18 | Applicazione web |
| **SQL Server** | Azure SQL | Database principale |
| **SQL Database** | Basic tier | Dati dell'applicazione |
| **Storage Account** | Standard LRS | File e blob storage |

## ⚙️ Configurazioni Automatiche

### Backend App Settings:
- `DATABASE_URL`: Connection string per SQL Database
- `STORAGE_CONNECTION_STRING`: Connection string per Storage
- `ENVIRONMENT`: prod/dev/test
- `FRONTEND_URL`: URL del frontend per CORS

### Frontend App Settings:
- `REACT_APP_API_URL`: URL dell'API backend
- `NODE_ENV`: production/development

### Sicurezza:
- **CORS** configurato tra frontend e backend
- **SQL Firewall** aperto per servizi Azure
- **HTTPS** obbligatorio per tutte le app

## 🔐 Credenziali

### SQL Server Admin:
- **Username**: `w3admin`
- **Password**: `W3Manifest2024!` (⚠️ CAMBIALA!)

**IMPORTANTE**: Cambia immediatamente la password SQL nel file script prima di eseguirlo!

## 🚀 Deployment del Codice

Dopo aver creato l'infrastruttura, configura il deployment automatico:

### Opzione 1: GitHub Actions
```yaml
# .github/workflows/deploy.yml
- uses: azure/webapps-deploy@v2
  with:
    app-name: 'w3manifest-backend-prod'
    publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
```

### Opzione 2: Azure DevOps
Usa il file `azure-pipelines.yml` nella root del progetto.

### Opzione 3: Deploy Manuale
```powershell
# Backend
az webapp deployment source config-zip --resource-group "rg-w3-manifest" --name "w3manifest-backend-prod" --src backend.zip

# Frontend  
az webapp deployment source config-zip --resource-group "rg-w3-manifest" --name "w3manifest-frontend-prod" --src frontend.zip
```

## 📊 Monitoraggio

### Application Insights (Opzionale)
Per abilitare il monitoraggio:
```powershell
# Crea Application Insights
az extension add --name application-insights
az monitor app-insights component create --app w3manifest-insights --location "West Europe" --resource-group rg-w3-manifest

# Collega alle app
az webapp config appsettings set --name w3manifest-backend-prod --resource-group rg-w3-manifest --settings APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=your-key"
```

## 🧹 Pulizia Risorse

Per eliminare tutto:
```powershell
az group delete --name "rg-w3-manifest" --yes --no-wait
```

## 💡 Tips

1. **Nomi Unici**: I nomi delle app devono essere unici globalmente. Lo script aggiunge suffissi automatici.

2. **Costi**: Le risorse Basic hanno costi contenuti (~30-50€/mese). Monitor con Azure Cost Management.

3. **Backup**: SQL Database ha backup automatici. Storage Account supporta versioning.

4. **SSL/TLS**: Certificati SSL gratuiti sono automaticamente configurati per i domini *.azurewebsites.net.

5. **Scaling**: Puoi modificare lo SKU dell'App Service Plan per performance migliori.

## 🆘 Troubleshooting

### Errore: Nome già in uso
Cambia il parametro `ProjectName` per rendere i nomi unici.

### Errore: Quota superata
Verifica i limiti della tua sottoscrizione Azure.

### App non si avvia
Controlla i log con:
```powershell
az webapp log tail --name "w3manifest-backend-prod" --resource-group "rg-w3-manifest"
```
