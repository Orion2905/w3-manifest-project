# Deployment Configuration

Questa cartella contiene le configurazioni per il deployment su Azure.

## File inclusi

- **docker-compose.yml**: Configurazione per container Docker
- **backend.dockerfile**: Dockerfile per l'API backend
- **frontend.dockerfile**: Dockerfile per l'applicazione frontend
- **azure-app-service.yml**: Template ARM per Azure App Service
- **scripts/**: Script di deployment e configurazione

## Deployment Options

### 1. Azure App Service (Recommended)
- Backend: Python App Service
- Frontend: Static Web App o Node.js App Service

### 2. Container Deployment
- Docker containers su Azure Container Instances
- Azure Kubernetes Service (AKS)

### 3. Serverless
- Backend: Azure Functions
- Frontend: Azure Static Web Apps

## TODO

- [ ] Creare Dockerfile per backend
- [ ] Creare Dockerfile per frontend  
- [ ] Template ARM per infrastruttura Azure
- [ ] Script di deployment automatico
- [ ] Configurazione environment variables
