#!/usr/bin/env python3
"""
Script di monitoraggio IMAP continuo per il controllo email in tempo reale.
Basato sulla logica fornita dall'utente con controllo ogni 5 secondi.
"""
import imaplib
import email
import time
import logging
from datetime import datetime
from typing import List, Dict, Set
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.utils.logging_config import setup_imap_logger

class ContinuousIMAPMonitor:
    """Monitor IMAP continuo per il controllo email ogni 5 secondi."""
    
    def __init__(self, imap_server: str, email_account: str, password: str, 
                 keyword_filter: str = None, folder: str = 'INBOX'):
        self.imap_server = imap_server
        self.email_account = email_account
        self.password = password
        self.keyword_filter = keyword_filter
        self.folder = folder
        self.logger = setup_imap_logger('continuous_monitor')
        self.processed_emails: Set[str] = set()  # Track processed email IDs
        self.running = False
        
        self.logger.info(f"🚀 IMAP Continuous Monitor - Initialized | Email Account: {self.email_account} | Server: {self.imap_server} | Keyword Filter: '{self.keyword_filter or 'None'}'")
    
    def connect(self) -> imaplib.IMAP4:
        """Stabilisce connessione IMAP."""
        try:
            self.logger.debug(f"🌐 IMAP Connect - Connecting to {self.imap_server} for account {self.email_account}")
            
            # Nota: Nell'esempio originale usa IMAP4, qui manteniamo la stessa logica
            # Per production, considera di usare IMAP4_SSL
            mail = imaplib.IMAP4(self.imap_server)
            
            self.logger.debug(f"🔑 IMAP Auth - Logging in as {self.email_account}")
            mail.login(self.email_account, self.password)
            
            self.logger.debug(f"📁 IMAP Folder - Selecting folder '{self.folder}'")
            mail.select(self.folder)
            
            self.logger.info(f"✅ IMAP Connected - Successfully connected to {self.email_account}@{self.imap_server}")
            return mail
            
        except Exception as e:
            self.logger.error(f"❌ IMAP Connection Failed - Account: {self.email_account} | Error: {str(e)}")
            raise
    
    def get_latest_emails(self, mail: imaplib.IMAP4, limit: int = 10) -> List[Dict]:
        """Ottiene le ultime email dalla casella."""
        try:
            # Cerca tutte le email
            typ, data = mail.search(None, 'ALL')
            
            if typ != 'OK' or not data[0]:
                self.logger.warning(f"⚠️ IMAP Search - No emails found in {self.email_account}")
                return []
            
            # Prendi gli ultimi email_ids (più recenti)
            email_ids = data[0].split()
            latest_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            
            self.logger.debug(f"📊 IMAP Search - Found {len(email_ids)} total emails, checking latest {len(latest_ids)} | Account: {self.email_account}")
            
            emails = []
            for num in latest_ids:
                try:
                    # Fetch l'email completo
                    typ, data = mail.fetch(num, '(RFC822)')
                    if typ == 'OK' and data[0]:
                        # Parse dell'email
                        email_message = email.message_from_bytes(data[0][1])
                        
                        email_info = {
                            'id': num.decode(),
                            'subject': email_message.get('Subject', ''),
                            'sender': email_message.get('From', ''),
                            'date': email_message.get('Date', ''),
                            'message_id': email_message.get('Message-ID', ''),
                            'body': self._extract_body(email_message)
                        }
                        emails.append(email_info)
                        
                except Exception as e:
                    self.logger.warning(f"⚠️ IMAP Parse Error - Failed to parse email {num.decode()} | Account: {self.email_account} | Error: {str(e)}")
            
            return emails
            
        except Exception as e:
            self.logger.error(f"❌ IMAP Fetch Error - Failed to get emails | Account: {self.email_account} | Error: {str(e)}")
            return []
    
    def _extract_body(self, email_message) -> str:
        """Estrae il corpo del messaggio email."""
        try:
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        return part.get_payload(decode=True).decode('utf-8', errors='ignore')
            else:
                return email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
        except Exception:
            return ""
        return ""
    
    def check_email_approval(self, email_info: Dict) -> bool:
        """Controlla se l'email deve essere approvata in base ai filtri."""
        if not self.keyword_filter:
            # Se non c'è filtro, approva tutto
            return True
        
        subject = email_info.get('subject', '').lower()
        body = email_info.get('body', '').lower()
        keyword_lower = self.keyword_filter.lower()
        
        # Controlla se la parola chiave è nel subject o nel body
        if keyword_lower in subject or keyword_lower in body:
            return True
        
        return False
    
    def process_new_emails(self, emails: List[Dict]) -> Dict:
        """Processa le nuove email e determina approvazione."""
        new_emails = []
        approved_count = 0
        rejected_count = 0
        
        for email_info in emails:
            email_id = email_info['id']
            
            # Controlla se è una nuova email (non ancora processata)
            if email_id not in self.processed_emails:
                new_emails.append(email_info)
                self.processed_emails.add(email_id)
                
                # Controlla approvazione
                is_approved = self.check_email_approval(email_info)
                
                subject_preview = email_info['subject'][:50] + '...' if len(email_info['subject']) > 50 else email_info['subject']
                sender = email_info['sender']
                
                if is_approved:
                    approved_count += 1
                    self.logger.info(f"✅ NUOVA MAIL APPROVATA | Account: {self.email_account} | From: {sender} | Subject: '{subject_preview}' | Keyword: '{self.keyword_filter}' found")
                else:
                    rejected_count += 1
                    self.logger.info(f"❌ NUOVA MAIL NON APPROVATA | Account: {self.email_account} | From: {sender} | Subject: '{subject_preview}' | Keyword: '{self.keyword_filter}' not found")
        
        return {
            'new_emails': len(new_emails),
            'approved': approved_count,
            'rejected': rejected_count,
            'emails': new_emails
        }
    
    def run_continuous_check(self, check_interval: int = 5):
        """Esegue il controllo continuo ogni N secondi."""
        self.running = True
        self.logger.info(f"🔄 IMAP Continuous Check - Starting monitoring | Account: {self.email_account} | Interval: {check_interval}s | Keyword Filter: '{self.keyword_filter or 'None'}'")
        
        while self.running:
            try:
                # Connetti ad IMAP
                mail = self.connect()
                
                # Ottieni le ultime 10 email
                emails = self.get_latest_emails(mail, limit=10)
                
                # Processa nuove email
                result = self.process_new_emails(emails)
                print("qui",result, emails)
                if result['new_emails'] > 0:
                    self.logger.info(f"📊 IMAP Check Summary | Account: {self.email_account} | New emails: {result['new_emails']} | Approved: {result['approved']} | Rejected: {result['rejected']}")
                else:
                    self.logger.debug(f"📭 IMAP Check - No new emails found | Account: {self.email_account}")
                
                # Chiudi connessione
                mail.close()
                mail.logout()
                
                # Aspetta prima del prossimo controllo
                self.logger.debug(f"⏱️ IMAP Wait - Next check in {check_interval} seconds | Account: {self.email_account}")
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                self.logger.info(f"🛑 IMAP Monitor - Stopped by user | Account: {self.email_account}")
                self.running = False
                break
            except Exception as e:
                self.logger.error(f"❌ IMAP Monitor Error - Check failed | Account: {self.email_account} | Error: {str(e)}")
                # Aspetta un po' prima di ritentare in caso di errore
                time.sleep(check_interval)
    
    def stop(self):
        """Ferma il monitoraggio continuo."""
        self.running = False
        self.logger.info(f"🛑 IMAP Monitor - Stopping | Account: {self.email_account}")

def main():
    """Funzione principale per testare il monitor continuo."""
    print("🧪 IMAP Continuous Monitor - Test")
    print("=" * 50)
    
    # Configurazione di test (puoi modificare questi valori)
    config = {
        'imap_server': 'imap.hostinger.com',
        'email_account': 'info@oriondev.it',  # Modifica con il tuo account
        'password': '^Q7LgUE7:rL',          # Modifica con la tua password
        'keyword_filter': 'manifest',         # Parola chiave da cercare
        'folder': 'INBOX'
    }
    
    print("Configurazione di test:")
    print(f"  Server: {config['imap_server']}")
    print(f"  Account: {config['email_account']}")
    print(f"  Keyword Filter: '{config['keyword_filter']}'")
    print(f"  Folder: {config['folder']}")
    print("\nPer usare con i tuoi dati, modifica la configurazione nel file.")
    print("\nAvvio monitoraggio (Ctrl+C per fermare)...")
    print("-" * 50)
    
    try:
        # Crea e avvia il monitor
        monitor = ContinuousIMAPMonitor(
            imap_server=config['imap_server'],
            email_account=config['email_account'],
            password=config['password'],
            keyword_filter=config['keyword_filter'],
            folder=config['folder']
        )
        
        # Avvia il controllo continuo ogni 5 secondi
        monitor.run_continuous_check(check_interval=5)
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
