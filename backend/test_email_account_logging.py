#!/usr/bin/env python3
"""
Test script per verificare i log dettagliati con informazioni sulla casella di posta.
"""
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.utils.logging_config import imap_logger, log_imap_info, log_imap_success, log_imap_warning

def test_email_account_logging():
    """Test logging with detailed email account information."""
    print("📧 Testing Email Account Logging")
    print("=" * 60)
    
    # Simula log di test di connessione con dettagli casella di posta
    log_imap_info(
        'connection_test_start',
        config_name='Gmail Production',
        details={
            'server': 'imap.gmail.com:993',
            'email_account': 'manifests@company.com',
            'folder': 'INBOX',
            'user': 'admin',
            'ip': '192.168.1.100'
        }
    )
    
    # Simula log di successo con statistiche
    log_imap_success(
        'email_check_complete',
        config_name='Office365 Backup',
        details={
            'email_account': 'backup.manifests@company.com',
            'server': 'outlook.office365.com:993',
            'folder': 'Manifests',
            'total_messages': 152,
            'new_emails': 3,
            'processed': 2,
            'ignored': 1,
            'user': 'operator'
        }
    )
    
    # Simula log di warning per troppe email
    log_imap_warning(
        'too_many_emails',
        config_name='High Volume Account',
        details={
            'email_account': 'highvolume@company.com',
            'server': 'mail.company.com:993',
            'found': 1250,
            'limit': 100,
            'action': 'limited to most recent'
        }
    )
    
    # Simula log di monitoraggio automatico
    log_imap_info(
        'monitoring_batch_check',
        details={
            'configs_checked': [
                'manifests@company.com (Gmail)',
                'backup@company.com (Office365)', 
                'archive@company.com (Exchange)'
            ],
            'total_configs': 3,
            'active_configs': 3,
            'check_interval': '300s'
        }
    )
    
    print("\n✅ Email account logging test completed!")
    print("📋 Check the output above for detailed email account information")

def show_enhanced_log_examples():
    """Show examples of enhanced logs with email account details."""
    print("\n📝 Enhanced Log Examples with Email Account Details:")
    print("=" * 70)
    
    examples = [
        "📧 IMAP CONNECTION_TEST_START | User: admin (ID: 1) | Config: 'Gmail Production' | Email Account: manifests@company.com | Server: imap.gmail.com:993 | Folder: INBOX | IP: 192.168.1.100",
        
        "✅ IMAP EMAIL_CHECK_COMPLETE | User: operator (ID: 2) | Config: 'Office365' | Email Account: backup@company.com | Server: outlook.office365.com:993 | Folder: Manifests | New emails: 3 | Processed: 2 | Ignored: 1",
        
        "🔒 IMAP SSL_CONNECTION | Config: 'Exchange Server' | Email Account: archive@company.com | Server: mail.company.com:993 | Connection established successfully",
        
        "📁 IMAP FOLDER_SELECTED | Config: 'Gmail Prod' | Email Account: manifests@company.com | Folder: 'INBOX' | Messages: 1,247",
        
        "⚠️ IMAP TOO_MANY_EMAILS | Config: 'High Volume' | Email Account: bulk@company.com | Found: 2,500 | Limited to: 100 most recent",
        
        "🔍 IMAP EMAIL_SEARCH | Config: 'Filtered Account' | Email Account: filtered@company.com | Folder: 'Manifests' | Criteria: 'SINCE 11-Sep-2025 SUBJECT manifest'",
        
        "🚀 IMAP MONITORING_STARTED | User: admin (ID: 1) | Monitoring 3 accounts: [manifests@company.com, backup@company.com, archive@company.com] | Interval: 300s"
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example}")
    
    print(f"\n🎯 Enhanced Information Now Logged:")
    print("  • Specific email account being monitored (e.g., manifests@company.com)")
    print("  • IMAP server and port details")
    print("  • Folder being accessed (INBOX, Manifests, etc.)")
    print("  • Connection type (SSL, STARTTLS, Plain)")
    print("  • Message counts and processing statistics")
    print("  • Search criteria and filters applied")
    print("  • Multi-account monitoring status")
    print("  • User who initiated each operation")

def show_monitoring_scenarios():
    """Show common monitoring scenarios with detailed logging."""
    print(f"\n📊 Common Monitoring Scenarios:")
    print("=" * 70)
    
    scenarios = [
        {
            'title': '🏢 Multi-Account Setup',
            'description': 'Company monitoring multiple email accounts',
            'accounts': [
                'manifests@company.com (Primary Gmail)',
                'backup@company.com (Office365 Backup)',
                'archive@company.com (Exchange Archive)'
            ]
        },
        {
            'title': '🔍 Filtered Monitoring', 
            'description': 'Monitoring with specific filters',
            'details': [
                'Subject filter: "manifest" OR "shipping"',
                'Sender filter: "@shipping-company.com"',
                'Folder: "Manifests" (not INBOX)'
            ]
        },
        {
            'title': '⚡ Real-time Processing',
            'description': 'Live email processing with immediate feedback',
            'flow': [
                '1. New email arrives at manifests@company.com',
                '2. IMAP service detects email (logged with account)',
                '3. Email processed (success/failure logged)',
                '4. Admin sees real-time activity in dashboard'
            ]
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['title']}")
        print("-" * 40)
        print(f"  {scenario['description']}")
        
        if 'accounts' in scenario:
            print("  Accounts monitored:")
            for account in scenario['accounts']:
                print(f"    • {account}")
        
        if 'details' in scenario:
            print("  Configuration:")
            for detail in scenario['details']:
                print(f"    • {detail}")
        
        if 'flow' in scenario:
            print("  Process flow:")
            for step in scenario['flow']:
                print(f"    {step}")

if __name__ == "__main__":
    test_email_account_logging()
    show_enhanced_log_examples()
    show_monitoring_scenarios()
    
    print(f"\n🔧 Key Benefits of Enhanced Logging:")
    print("=" * 50)
    print("1. 📧 **Account Identification**: Sempre sai da quale casella arrivano i dati")
    print("2. 🔍 **Debugging Facilitato**: Problemi specifici per account facilmente identificabili")
    print("3. 📊 **Statistiche Precise**: Metriche per singolo account o complessive")
    print("4. 🛡️ **Security Auditing**: Tracciamento completo di chi accede a quale account")
    print("5. ⚡ **Real-time Monitoring**: Visibilità immediata su quale account sta processando email")
    
    print(f"\n🎯 Utilizzo Pratico:")
    print("  • Identifica rapidamente quale account ha problemi di connessione")
    print("  • Monitora il volume di email per account specifico") 
    print("  • Verifica che tutti gli account configurati siano attivi")
    print("  • Traccia l'attività degli utenti per account di posta specifici")
