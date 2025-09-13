# 📧 Guida al Monitoraggio Dettagliato delle Caselle Email IMAP

## 🎯 Panoramica

Il sistema ora include logging dettagliato che mostra **esattamente** da quale casella di posta elettronica vengono letti i dati, chi sta facendo le operazioni e quando.

## 📊 Informazioni Tracciate per Ogni Casella Email

### 🔍 **Identificazione della Casella Email**
Ogni log include:
- **Email Account**: L'indirizzo email specifico (es. `manifests@company.com`)
- **Server IMAP**: Server e porta (es. `imap.gmail.com:993`)
- **Folder**: Cartella specifica (es. `INBOX`, `Manifests`, `Archive`)
- **Configuration Name**: Nome amichevole della configurazione

### 👤 **Contesto Utente**
- **Username**: Chi ha fatto la richiesta
- **User ID**: ID numerico dell'utente
- **IP Address**: Da dove arriva la richiesta

## 📝 Esempi di Log Dettagliati

### 🔗 **Test di Connessione**
```
📧 IMAP CONNECTION_TEST_START | User: admin (ID: 1) | Config: 'Gmail Production' | 
Email Account: manifests@company.com | Server: imap.gmail.com:993 | 
Folder: INBOX | IP: 192.168.1.100

🔒 IMAP SSL_CONNECTION | Email Account: manifests@company.com | 
Server: imap.gmail.com:993 | Connection established successfully

✅ IMAP TEST_SUCCESS | Config: 'Gmail Production' | 
Email Account: manifests@company.com | Messages: 1,247
```

### 📨 **Controllo Email Automatico**
```
📧 IMAP EMAIL_CHECK_START | Config: 'Office365 Backup' | 
Email Account: backup@company.com | Server: outlook.office365.com:993 | 
Folder: Manifests | Filters: Subject: manifest, Sender: None

📁 IMAP FOLDER_SELECTED | Email Account: backup@company.com | 
Folder: 'Manifests' | Messages: 152 | Server: outlook.office365.com:993

✅ IMAP EMAIL_CHECK_COMPLETE | Config: 'Office365 Backup' | 
Email Account: backup@company.com | New emails: 3 | Processed: 2 | Ignored: 1
```

### 🚀 **Monitoraggio Automatico**
```
🚀 IMAP MONITORING_STARTED | User: admin (ID: 1) | 
Monitoring 3 accounts: [manifests@company.com, backup@company.com, archive@company.com] | 
Interval: 300s

📧 IMAP BATCH_CHECK_START | Configs: 3 active accounts

📊 IMAP EMAIL_CHECK_COMPLETE | Email Account: manifests@company.com | 
Server: imap.gmail.com:993 | Folder: INBOX | New emails: 5

📊 IMAP EMAIL_CHECK_COMPLETE | Email Account: backup@company.com | 
Server: outlook.office365.com:993 | Folder: Manifests | New emails: 2

📊 IMAP EMAIL_CHECK_COMPLETE | Email Account: archive@company.com | 
Server: mail.company.com:993 | Folder: Archive | New emails: 0
```

## 🔧 Come Utilizzare i Log per Monitoring

### 1. **Identificare Problemi per Account Specifico**

**Problema**: Una casella email non riceve manifest
```bash
# Cerca nei log per account specifico
grep "manifests@company.com" logs/imap_monitor_*.log

# Risultati mostrano:
❌ IMAP TEST_FAILED | Email Account: manifests@company.com | 
Error: Authentication failed
```

### 2. **Monitorare Volume Email per Casella**

**Scenario**: Verificare quale account riceve più email
```bash
# Cerca statistiche per tutti gli account
grep "EMAIL_CHECK_COMPLETE" logs/imap_monitor_*.log

# Risultati:
✅ IMAP EMAIL_CHECK_COMPLETE | Email Account: manifests@company.com | New emails: 15
✅ IMAP EMAIL_CHECK_COMPLETE | Email Account: backup@company.com | New emails: 3  
✅ IMAP EMAIL_CHECK_COMPLETE | Email Account: archive@company.com | New emails: 0
```

### 3. **Tracciare Attività Utente per Account**

**Scenario**: Vedere chi sta testando quali account
```bash
# Cerca attività per utente specifico
grep "User: admin" logs/imap_monitor_*.log | grep "CONNECTION_TEST"

# Risultati:
🔍 IMAP CONNECTION_TEST | User: admin | Email Account: manifests@company.com
🔍 IMAP CONNECTION_TEST | User: admin | Email Account: backup@company.com
```

## 📈 Dashboard Real-time

### 🎯 **Cosa Vedere in Tempo Reale**

Quando accedi al pannello admin, i log mostrano:

1. **Attività Live per Account**:
   ```
   📡 IMAP REALTIME_LOGS | User: admin | 
   Retrieved logs for: manifests@company.com, backup@company.com
   ```

2. **Operazioni in Corso**:
   ```
   🔍 IMAP MANUAL_CHECK | User: operator | 
   Email Account: manifests@company.com | Starting check...
   
   ✅ IMAP MANUAL_CHECK | User: operator | 
   Email Account: manifests@company.com | Completed: 3 new emails
   ```

## 🛡️ Security e Auditing

### 📊 **Tracciamento Accessi**

Ogni accesso alle caselle email è tracciato:

```
📧 IMAP GET_CONFIGS | User: john_doe (ID: 5) | IP: 10.0.1.45
🔍 IMAP CONNECTION_TEST | User: john_doe | Email Account: sensitive@company.com
⚠️ IMAP AUTH_FAILED | Email Account: sensitive@company.com | Invalid credentials
```

### 🚨 **Alert Automatici**

Il sistema logga eventi che richiedono attenzione:

```
⚠️ IMAP TOO_MANY_EMAILS | Email Account: bulk@company.com | 
Found: 2,500 | Limited to: 100 most recent

❌ IMAP CONNECTION_FAILED | Email Account: old@company.com | 
Error: Server not responding

🔒 IMAP AUTH_FAILED | Email Account: secure@company.com | 
Multiple failed attempts detected
```

## 🎛️ Controllo Avanzato

### 📋 **API Endpoints con Logging Dettagliato**

Tutti questi endpoint ora loggano l'account email coinvolto:

- `GET /api/email-config/` - Lista configurazioni
- `POST /api/email-config/{id}/test` - Test connessione per account
- `POST /api/email-config/{id}/check` - Controllo manuale account
- `GET /api/email-config/realtime-logs` - Log in tempo reale
- `POST /api/email-config/monitor/start` - Avvio monitoraggio
- `POST /api/email-config/monitor/stop` - Stop monitoraggio

### 📊 **File di Log Persistenti**

I log vengono salvati in:
```
backend/logs/imap_monitor_YYYYMMDD.log
```

Formato timestamp dettagliato:
```
2025-09-12 14:30:15 - imap_monitor - INFO - 
📧 IMAP EMAIL_CHECK_START | Config: 'Gmail Production' | 
Email Account: manifests@company.com | Server: imap.gmail.com:993
```

## 🔧 Troubleshooting

### 🐛 **Problemi Comuni e Come Identificarli**

1. **Account non risponde**:
   ```
   ❌ IMAP CONNECTION_FAILED | Email Account: old@company.com | 
   Error: [Errno 61] Connection refused
   ```

2. **Credenziali errate**:
   ```
   ❌ IMAP AUTH_FAILED | Email Account: test@company.com | 
   Error: Authentication failed
   ```

3. **Folder non trovato**:
   ```
   ❌ IMAP FOLDER_ERROR | Email Account: backup@company.com | 
   Error: Cannot select folder 'WrongFolder'
   ```

4. **Troppi email**:
   ```
   ⚠️ IMAP TOO_MANY_EMAILS | Email Account: bulk@company.com | 
   Found: 5,000 | Performance impact: high
   ```

## 🎯 Best Practices

1. **Monitoraggio Regolare**: Controlla i log quotidianamente per ogni account
2. **Alert Setup**: Configura notifiche per errori di autenticazione
3. **Performance**: Monitora account con alto volume per evitare sovraccarichi
4. **Security**: Traccia accessi non autorizzati ai log degli account
5. **Backup**: Mantieni storico dei log per analisi a lungo termine

Con questo sistema di logging dettagliato, hai **visibilità completa** su quale casella di posta sta processando cosa, quando e da parte di chi! 🎯
