#!/bin/bash

# Script per installare i driver ODBC per SQL Server su Azure App Service

# Aggiorna i repository dei pacchetti
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Aggiorna la lista dei pacchetti
apt-get update

# Installa il driver ODBC per SQL Server
ACCEPT_EULA=Y apt-get install -y msodbcsql18

# Installa unixODBC development headers (necessari per pyodbc)
apt-get install -y unixodbc-dev

# Installa g++ compiler (necessario per compilare pyodbc)
apt-get install -y g++

echo "Driver ODBC installati con successo"
