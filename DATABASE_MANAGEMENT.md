# 🗄️ Database Management Guide - W3 Manifest Project

## 📋 **Panoramica**

Il progetto W3 Manifest utilizza due database diversi:

- **🏠 Local Database (SQLite)**: Per sviluppo locale
- **☁️ Azure Database (SQL Server)**: Per produzione

## 🔧 **Configurazioni Database**

### **Local SQLite Database**
- **Tipo**: SQLite
- **File**: `backend/instance/w3manifest_dev.db`
- **URL**: `sqlite:///w3manifest_dev.db`
- **Uso**: Sviluppo locale, test rapidi

### **Azure SQL Server Database**
- **Server**: `w3manifest-sqlserver-prod.database.windows.net`
- **Database**: `w3manifest-db`
- **Username**: `w3admin`
- **Password**: `W3Manifest2024!`
- **Porta**: `1433`
- **Uso**: Produzione, deploy su Azure

## 🛠️ **Gestione Database**

### **Tool: db_switcher.py**

```bash
# Mostra database attuale
python db_switcher.py status

# Passa al database locale
python db_switcher.py local

# Passa al database Azure
python db_switcher.py azure

# Controlla stato di entrambi i database
python db_switcher.py check-all
```

### **Inizializzazione Database**

#### **Locale (SQLite)**
```bash
cd backend
export FLASK_APP=app.py
flask db upgrade
flask init-db
flask seed-db
```

#### **Azure (SQL Server)**
```bash
cd backend
python db_switcher.py azure
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

## 🔍 **Verificare Connessione Database**

### **Test Connessione Azure**
```bash
# Via Python
python -c "
from app import create_app, db
import os
os.environ['DATABASE_URL'] = 'Server=tcp:w3manifest-sqlserver-prod.database.windows.net,1433;Initial Catalog=w3manifest-db;Persist Security Info=False;User ID=w3admin;Password=W3Manifest2024!;MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;'
app = create_app()
app.app_context().push()
from app.models.user import User
users = User.query.all()
print(f'Connected! Users: {len(users)}')
"
```

### **Test Connessione via SQL**
```bash
# Usando sqlcmd (se installato)
sqlcmd -S w3manifest-sqlserver-prod.database.windows.net -d w3manifest-db -U w3admin -P W3Manifest2024! -Q "SELECT COUNT(*) FROM users"
```

## 📊 **Monitoraggio Database**

### **Verifica Tabelle**
```python
from app import create_app, db
app = create_app()
app.app_context().push()

# Lista tabelle
inspector = db.inspect(db.engine)
tables = inspector.get_table_names()
print(f"Tables: {tables}")

# Conta record per tabella
for table in tables:
    try:
        result = db.engine.execute(f"SELECT COUNT(*) FROM {table}")
        count = result.scalar()
        print(f"{table}: {count} records")
    except Exception as e:
        print(f"{table}: Error - {e}")
```

## 🚨 **Risoluzione Problemi**

### **Problema: "No such table"**
- Causa: Database non inizializzato
- Soluzione: Eseguire `db.create_all()` o `flask db upgrade`

### **Problema: "Login failed for user"**
- Causa: Credenziali errate
- Soluzione: Verificare username/password in Azure Portal

### **Problema: "Cannot open server"**
- Causa: Firewall Azure o connessione di rete
- Soluzione: Configurare firewall Azure per il tuo IP

### **Problema: "Database non sincronizzato"**
- Causa: Modifiche solo su un database
- Soluzione: Usare `db_switcher.py check-all` per verificare

## 🔐 **Sicurezza**

### **Password Recovery Azure**
Se dimentichi la password del database Azure:

1. **Via Azure Portal**:
   - Vai su SQL Server resource
   - Clicca "Reset password"
   - Inserisci nuova password

2. **Via Azure CLI**:
   ```bash
   az sql server update --name w3manifest-sqlserver-prod --resource-group rg-w3-manifest --admin-password "NuovaPassword123!"
   ```

3. **Aggiorna configurazione**:
   - Modifica `.env` file
   - Aggiorna script di deployment
   - Aggiorna `db_switcher.py`

## 📋 **Best Practices**

1. **🔄 Sempre fare backup** prima di modifiche importanti
2. **🧪 Testare prima su locale** poi su Azure
3. **📊 Monitorare performance** database Azure
4. **🔐 Rotatare password** periodicamente
5. **📝 Documentare cambiamenti** di schema

## 🎯 **Quick Reference**

```bash
# Switch rapido database
python db_switcher.py local    # Sviluppo
python db_switcher.py azure    # Produzione

# Backup locale
cp backend/instance/w3manifest_dev.db backend/instance/backup_$(date +%Y%m%d).db

# Restart servizi dopo switch
# Restart Flask app
# Restart frontend se necessario
```

## 📞 **Contatti**

Per problemi database contattare:
- Admin: orion.stanchieri@gmail.com
- Documentazione: [Repository GitHub]
