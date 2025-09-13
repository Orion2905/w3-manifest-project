# GitHub Actions Setup per Deploy Automatico

## Setup GitHub Secrets

Per abilitare il deploy automatico da GitHub ad Azure, devi configurare questo secret nel repository GitHub:

### 1. AZURE_CREDENTIALS

Vai su GitHub → Repository → Settings → Secrets and variables → Actions → New repository secret

**Nome:** `AZURE_CREDENTIALS`

**Valore:** Usa le credenziali generate dal comando Azure CLI precedente (sostituisci i placeholder):
```json
{
  "clientId": "YOUR_CLIENT_ID_FROM_AZURE_CLI",
  "clientSecret": "YOUR_CLIENT_SECRET_FROM_AZURE_CLI", 
  "subscriptionId": "YOUR_SUBSCRIPTION_ID",
  "tenantId": "YOUR_TENANT_ID",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "activeDirectoryGraphResourceId": "https://graph.windows.net/",
  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
  "galleryEndpointUrl": "https://gallery.azure.com/",
  "managementEndpointUrl": "https://management.core.windows.net/"
}
```

## Come Funziona

Una volta configurato il secret, il deploy automatico funzionerà così:

### 🚀 Deploy Automatico del Backend
- **Trigger:** Push di modifiche nella cartella `backend/` al branch `master`
- **Processo:** Build Python → Deploy su `w3manifest-backend-prod`

### 🚀 Deploy Automatico del Frontend  
- **Trigger:** Push di modifiche nella cartella `frontend/` al branch `master`
- **Processo:** Build Next.js → Deploy su `w3manifest-frontend-prod`

### 🔄 Deploy Manuale
Puoi anche eseguire il deploy manualmente da GitHub:
1. Vai su GitHub → Actions
2. Seleziona il workflow desiderato
3. Clicca "Run workflow"

## ✅ Vantaggi

✅ **Deploy automatico** ad ogni push  
✅ **Niente più file ZIP** da creare manualmente  
✅ **Build ottimizzato** in ambiente CI/CD  
✅ **Rollback facile** tramite Git  
✅ **Deploy selettivo** (solo se modifichi backend o frontend)

## 🔗 URL delle Applicazioni

- **Frontend:** https://w3manifest-frontend-prod.azurewebsites.net
- **Backend:** https://w3manifest-backend-prod.azurewebsites.net

## 🔐 Sicurezza

⚠️ **IMPORTANTE:** Le credenziali Azure sono configurate come GitHub Secret e non sono visibili nel codice.
