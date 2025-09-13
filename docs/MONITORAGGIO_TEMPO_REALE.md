# 📡 Guida al Monitoraggio Email in Tempo Reale

## Panoramica
Il sistema di monitoraggio in tempo reale ti permette di vedere le email che arrivano **istantaneamente** e verificare se vengono **accettate o rifiutate** dai filtri che hai configurato.

## Come Accedere

1. **Accedi come Amministratore** al sistema
2. Vai alla sezione **"Admin"** → **"Email Management"** 
3. Clicca sulla tab **"📡 Tempo Reale"**

## Funzionalità Principali

### 🎯 **Monitoraggio Live**
- **▶️ Avvia Monitoraggio**: Inizia il monitoraggio in tempo reale
- **⏹️ Stop Monitoraggio**: Ferma il monitoraggio
- **🔄 Aggiornamento Automatico**: Ogni 5 secondi (configurabile)
- **📡 Indicatore di Stato**: Pallino verde quando attivo

### 📧 **Visualizzazione Email**
Ogni email che arriva viene mostrata con:

#### ✅ **Email Accettate (Processate)**
- **Icona**: ✅ 
- **Stato**: `PROCESSED` (verde)
- **Dettagli**: Mostra se il manifest è stato scaricato
- **Significato**: L'email rispetta tutti i filtri ed è stata elaborata

#### 🚫 **Email Rifiutate (Ignorate)**  
- **Icona**: 🚫
- **Stato**: `IGNORED` (giallo)
- **Motivo**: Specifica quale filtro ha bloccato l'email
- **Esempi di Filtri**:
  - Mittente non autorizzato
  - Oggetto non corrispondente
  - Nessun allegato trovato
  - Tipo file non supportato

#### ❌ **Email con Errori**
- **Icona**: ❌ 
- **Stato**: `ERROR` (rosso)
- **Dettagli**: Descrizione dell'errore
- **Esempi di Errori**:
  - Impossibile scaricare allegato
  - Formato manifest non valido
  - Errore di connessione

### 🧪 **Simulazione per Test**
Quando il monitoraggio è attivo, puoi simulare email di test:

- **✅ Accettata**: Simula un'email che passa tutti i filtri
- **🚫 Rifiutata**: Simula un'email bloccata dai filtri  
- **❌ Errore**: Simula un'email con errore di processing

## Come Interpretare i Risultati

### ✅ **Sistema Funzionante Correttamente**
```
✅ Email da: supplier@example.com
📧 Oggetto: "Manifest W3-12345"
✅ Email processata con successo
📎 File: manifest_W3-12345.pdf
⏰ 14:32:15
```
**Significato**: L'email è stata accettata e il manifest scaricato

### 🚫 **Email Bloccata dai Filtri**
```
🚫 Email da: spam@unknown.com  
📧 Oggetto: "Offerta speciale!"
🚫 Filtro applicato: Mittente non autorizzato
⏰ 14:35:22
```
**Significato**: L'email non rispetta i filtri configurati (comportamento corretto)

### ❌ **Errore nel Processing**
```
❌ Email da: supplier@example.com
📧 Oggetto: "Manifest W3-12346"  
❌ Errore: Impossibile scaricare allegato
⏰ 14:38:09
```
**Significato**: L'email è valida ma c'è un problema tecnico

## Verifica che Tutto Funzioni

### 🔍 **Controllo Filtri Efficaci**
1. **Avvia il monitoraggio**
2. **Osserva le email che arrivano**
3. **Verifica che le email spam/indesiderate** vengano mostrate come `🚫 IGNORED`
4. **Verifica che le email valide** vengano mostrate come `✅ PROCESSED`

### 📊 **Pattern da Monitorare**

#### **Scenario Ideale** ✅
- 80-90% email `✅ PROCESSED`
- 10-20% email `🚫 IGNORED` (spam/irrilevanti)
- 0-5% email `❌ ERROR`

#### **Problemi da Investigare** ⚠️
- **Troppe email `🚫 IGNORED`**: Filtri troppo restrittivi
- **Troppe email `❌ ERROR`**: Problemi tecnici
- **Nessuna email `✅ PROCESSED`**: Filtri sbagliati o nessuna email valida

## Risoluzione Problemi Comuni

### 🚫 **Tutte le Email Vengono Rifiutate**
**Cause Possibili:**
- Filtri mittente troppo restrittivi
- Filtri oggetto non corrispondenti
- Filtri allegato non configurati correttamente

**Soluzioni:**
1. Vai alla tab "Configurazioni"
2. Controlla i filtri della configurazione
3. Espandi i criteri di accettazione
4. Testa la configurazione

### ❌ **Molte Email con Errori**
**Cause Possibili:**
- Problemi di connessione internet
- Server email temporaneamente offline
- Formato allegati non supportato

**Soluzioni:**
1. Controlla la connessione internet
2. Testa la configurazione manualmente
3. Verifica i log dettagliati

### 📭 **Nessuna Email in Arrivo**
**Cause Possibili:**
- Configurazioni disattivate
- Cartelle email sbagliate
- Credenziali scadute

**Soluzioni:**
1. Verifica che le configurazioni siano attive
2. Controlla che le cartelle esistano
3. Aggiorna credenziali se necessario

## Consigli per l'Uso Ottimale

### 📅 **Monitoraggio Quotidiano**
- **Mattina**: Avvia per 15-30 minuti per vedere l'attività notturna
- **Durante il giorno**: Controlla periodicamente durante le ore di punta
- **Fine giornata**: Verifica che tutte le email importanti siano state processate

### 🔧 **Ottimizzazione Filtri**
1. **Osserva i pattern** delle email che arrivano
2. **Identifica email valide rifiutate** (falsi positivi)
3. **Identifica email spam accettate** (falsi negativi)  
4. **Aggiusta i filtri** di conseguenza

### 📈 **Analisi delle Performance**
- **Tempo di risposta**: Le email dovrebbero essere processate entro 1-2 minuti
- **Tasso di successo**: >90% di email valide dovrebbero essere processate
- **Efficacia filtri**: <20% di spam dovrebbe passare

## Simulazione per Training

Usa i pulsanti di simulazione per:

1. **Formare il team**: Mostra come funziona il sistema
2. **Testare modifiche**: Verifica l'impatto dei nuovi filtri
3. **Debugging**: Identifica problemi senza aspettare email reali

### Esempio di Sessione di Test:
```
1. Avvia monitoraggio
2. Simula "Email Accettata" → Verifica che appaia come ✅
3. Simula "Email Rifiutata" → Verifica che appaia come 🚫  
4. Simula "Email con Errore" → Verifica che appaia come ❌
```

---

**💡 Pro Tip**: Tieni sempre aperta la tab "Tempo Reale" durante le ore di maggiore attività email per avere visibilità immediata su cosa sta succedendo!

## FAQ

**Q: Quanto spesso si aggiorna?**
A: Ogni 5 secondi automaticamente quando il monitoraggio è attivo.

**Q: Quante email vengono mostrate?**
A: Le ultime 200 email per evitare problemi di memoria.

**Q: Posso vedere email più vecchie?**
A: Sì, usa la tab "Log Attività" per vedere tutto lo storico.

**Q: Il monitoraggio rallenta il sistema?**
A: No, usa pochissime risorse e si aggiorna solo quando ci sono nuove email.

**Q: Posso monitorare multiple configurazioni?**
A: Sì, il monitoraggio mostra email da tutte le configurazioni attive contemporaneamente.
