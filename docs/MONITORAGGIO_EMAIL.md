# Guida al Monitoraggio Email - Come Verificare la Lettura Corretta

## Panoramica
Questo sistema ti permette di monitorare e verificare che tutte le email in arrivo vengano lette e processate correttamente.

## Dashboard di Monitoraggio

### Accesso al Monitoring
1. Accedi come amministratore al sistema
2. Vai alla sezione "Admin" → "Email Management"
3. La dashboard di monitoraggio è visibile nella parte superiore della pagina

### Metriche Chiave per Verificare la Lettura Corretta

#### 📊 Statistiche Configurazioni
- **Configurazioni Totali**: Numero totale di configurazioni email create
- **Configurazioni Attive**: Configurazioni in esecuzione (devono essere > 0)
- **Configurazioni Inattive**: Configurazioni disabilitate
- **Configurazioni con Errori**: Configurazioni che hanno problemi (dovrebbe essere 0)

#### 📧 Statistiche Email Giornaliere
- **Email Oggi**: Numero totale di email elaborate oggi
- **Email Processate**: Email scaricate e processate con successo
- **Email Non Lette**: Email che non sono state processate per errori
- **Ultima Email**: Timestamp dell'ultima email ricevuta
- **Tempo Medio Elaborazione**: Tempo medio per processare un'email

## Come Interpretare i Dati

### ✅ Sistema Funzionante Correttamente
- **Configurazioni Attive > 0**: Almeno una configurazione è in esecuzione
- **Configurazioni con Errori = 0**: Nessun errore nelle configurazioni
- **Email Processate ≈ Email Oggi**: La maggior parte delle email vengono processate
- **Email Non Lette ≈ 0**: Poche o nessuna email non processata
- **Ultima Email recente**: L'ultima email è stata ricevuta di recente

### ⚠️ Possibili Problemi

#### 1. Nessuna Email Processata
**Sintomi:**
- Email Oggi = 0
- Email Processate = 0

**Possibili Cause:**
- Nessuna configurazione attiva
- Configurazioni email sbagliate
- Server email non raggiungibile

**Soluzioni:**
1. Verifica che almeno una configurazione sia attiva
2. Testa la connessione delle configurazioni
3. Controlla i log per errori specifici

#### 2. Email Non Lette Elevate
**Sintomi:**
- Email Non Lette > 10% delle Email Oggi
- Email Processate < Email Oggi

**Possibili Cause:**
- Errori di processing dei manifest
- Filtri email troppo restrittivi
- Problemi di formato degli allegati

**Soluzioni:**
1. Controlla i log dettagliati
2. Verifica i filtri delle configurazioni
3. Testa manualmente il download degli allegati

#### 3. Configurazioni con Errori
**Sintomi:**
- Configurazioni con Errori > 0
- Errori mostrati nella sezione "Last Check Times"

**Possibili Cause:**
- Credenziali email scadute
- Server email cambiato
- Cartelle email inesistenti

**Soluzioni:**
1. Aggiorna le credenziali email
2. Verifica le impostazioni server
3. Controlla che le cartelle esistano

## Controlli Periodici Raccomandati

### Controllo Giornaliero (5 minuti)
1. **Verifica Dashboard**: Controlla che le metriche siano normali
2. **Email Processate**: Assicurati che ci siano email processate se attese
3. **Errori**: Verifica che non ci siano configurazioni con errori

### Controllo Settimanale (15 minuti)
1. **Analisi Trend**: Controlla l'andamento delle email nel tempo
2. **Performance**: Verifica i tempi di elaborazione
3. **Configurazioni**: Testa periodicamente le connessioni

### Controllo Mensile (30 minuti)
1. **Pulizia Log**: Archivia o elimina log vecchi
2. **Ottimizzazione**: Rivedi e ottimizza i filtri email
3. **Backup**: Verifica che le configurazioni siano salvate

## Log e Debugging

### Accesso ai Log
1. Vai a "Email Management" → scheda "Logs"
2. Filtra per configurazione, stato o periodo
3. Esamina i dettagli degli errori

### Interpretazione dei Log
- **Status: success** ✅ - Email processata correttamente
- **Status: error** ❌ - Errore nel processing
- **Status: warning** ⚠️ - Processata con avvisi

- **Action: downloaded** - Email scaricata
- **Action: processed** - Manifest elaborato
- **Action: error** - Errore durante l'elaborazione
- **Action: ignored** - Email ignorata dai filtri

## Test delle Configurazioni

### Test Manuale
1. Vai alla configurazione specifica
2. Clicca "Test Connection"
3. Verifica che il test sia successful
4. Controlla il numero di messaggi nella cartella

### Test Automatico
Il sistema testa automaticamente le configurazioni e aggiorna:
- **Last Check**: Ultimo controllo effettuato
- **Last Success**: Ultimo controllo riuscito
- **Error Message**: Eventuale messaggio di errore

## Notifiche e Alert

### Quando Preoccuparsi
- Nessuna email processata per più di 24 ore (se attese)
- Più del 50% delle email non processate
- Configurazioni con errori per più di 1 ora
- Tempo di elaborazione in crescita costante

### Azioni Immediate
1. Controlla i log per errori specifici
2. Testa manualmente le configurazioni
3. Verifica la connettività del server
4. Controlla lo spazio disco disponibile

## Risoluzione Problemi Comuni

### Password Email Scadute
1. Aggiorna la password nella configurazione
2. Testa la connessione
3. Monitora per 1 ora che riprenda a funzionare

### Server Email Non Raggiungibile
1. Verifica la connettività di rete
2. Controlla le impostazioni firewall
3. Verifica che il server email sia operativo

### Spazio Disco Pieno
1. Pulisci i file temporanei
2. Archivia i log vecchi
3. Elimina i manifest processati e non più necessari

---

**💡 Suggerimento**: Tieni sempre d'occhio la dashboard di monitoraggio e imposta controlli regolari per garantire il funzionamento ottimale del sistema.
