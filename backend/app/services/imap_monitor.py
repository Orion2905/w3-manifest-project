"""
IMAP Email Monitoring Service
Handles background monitoring of email accounts for new manifest emails.
"""
import imaplib
import email
import ssl
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from app import db
from app.models.email_config import EmailConfig, EmailLog
from app.utils.logging_config import setup_imap_logger, log_imap_activity
import threading
import time

class IMAPMonitorService:
    """Service for monitoring IMAP email accounts."""
    
    def __init__(self):
        self.logger = setup_imap_logger('imap_service')
        self.monitoring_active = False
        self.monitor_thread = None
        self.check_interval = 300  # 5 minutes default
        self.continuous_monitoring = False
        self.continuous_thread = None
        self.processed_email_ids = {}  # Track processed emails per config
        
    def start_monitoring(self, interval_seconds=300):
        """Start background monitoring of all active email configurations."""
        if self.monitoring_active:
            self.logger.warning("🔄 IMAP monitoring already active")
            return
        
        self.check_interval = interval_seconds
        self.monitoring_active = True
        
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        log_imap_activity(
            self.logger, 'INFO', 'monitoring_started',
            details={'interval': f'{interval_seconds}s'}
        )
    
    def start_continuous_monitoring(self, interval_seconds=5):
        """Start continuous monitoring every 5 seconds (like the user's script)."""
        if self.continuous_monitoring:
            self.logger.warning("🔄 IMAP continuous monitoring already active")
            return
        
        self.continuous_monitoring = True
        self.continuous_thread = threading.Thread(target=self._continuous_monitor_loop, args=(interval_seconds,), daemon=True)
        self.continuous_thread.start()
        
        log_imap_activity(
            self.logger, 'INFO', 'continuous_monitoring_started',
            details={'interval': f'{interval_seconds}s', 'mode': 'real_time'}
        )
    
    def stop_continuous_monitoring(self):
        """Stop continuous monitoring."""
        self.continuous_monitoring = False
        log_imap_activity(self.logger, 'INFO', 'continuous_monitoring_stopped')
    
    def _continuous_monitor_loop(self, interval_seconds):
        """Continuous monitoring loop (every 5 seconds like user's script)."""
        while self.continuous_monitoring:
            try:
                self._check_all_configs_continuous()
            except Exception as e:
                log_imap_activity(
                    self.logger, 'ERROR', 'continuous_monitoring_error',
                    error=e
                )
            
            # Wait for next check
            time.sleep(interval_seconds)
    
    def _check_all_configs_continuous(self):
        """Check all active configs continuously (like user's script logic)."""
        configs = EmailConfig.query.filter_by(is_active=True).all()
        
        if not configs:
            return
        
        log_imap_activity(
            self.logger, 'DEBUG', 'continuous_batch_check',
            details={'configs_count': len(configs), 'mode': 'real_time'}
        )
        
        for config in configs:
            try:
                self.check_config_emails_continuous(config)
            except Exception as e:
                log_imap_activity(
                    self.logger, 'ERROR', 'continuous_config_check_failed',
                    config_name=config.name,
                    error=e
                )
    
    def check_config_emails_continuous(self, config: EmailConfig) -> Dict:
        """Check emails continuously for a config (like user's script)."""
        try:
            # Initialize processed emails set for this config if not exists
            if config.id not in self.processed_email_ids:
                self.processed_email_ids[config.id] = set()
            
            # Connect to IMAP
            mail = self._connect_to_imap(config)
            
            # Get latest 10 emails (like user's script)
            latest_emails = self._get_latest_emails_continuous(mail, config, limit=10)
            
            # Close connection
            mail.close()
            mail.logout()
            
            # Process new emails and check approval
            result = self._process_new_emails_for_approval(config, latest_emails)
            
            # Update config status
            config.update_last_check(success=True)
            
            if result['new_emails'] > 0:
                log_imap_activity(
                    self.logger, 'INFO', 'continuous_check_summary',
                    config_name=config.name,
                    details={
                        'email_account': config.email,
                        'new_emails': result['new_emails'],
                        'approved': result['approved'],
                        'rejected': result['rejected']
                    }
                )
            
            return result
            
        except Exception as e:
            config.update_last_check(success=False, error_message=str(e))
            log_imap_activity(
                self.logger, 'ERROR', 'continuous_check_failed',
                config_name=config.name,
                error=e
            )
            raise
    
    def _get_latest_emails_continuous(self, mail: imaplib.IMAP4, config: EmailConfig, limit: int = 10) -> List[Dict]:
        """Get latest emails (like user's script ALL search + limit)."""
        try:
            # Search ALL emails (like user's script)
            status, messages = mail.search(None, 'ALL')
            if status != 'OK' or not messages[0]:
                return []
            
            # Get email IDs and take latest ones
            email_ids = messages[0].split()
            latest_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            
            log_imap_activity(
                self.logger, 'DEBUG', 'continuous_email_fetch',
                config_name=config.name,
                details={
                    'email_account': config.email,
                    'total_emails': len(email_ids),
                    'checking_latest': len(latest_ids)
                }
            )
            
            emails = []
            for email_id in latest_ids:
                try:
                    # Fetch full email (like user's script RFC822)
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    if status == 'OK' and msg_data[0]:
                        email_message = email.message_from_bytes(msg_data[0][1])
                        
                        email_info = {
                            'id': email_id.decode(),
                            'subject': email_message.get('Subject', ''),
                            'sender': email_message.get('From', ''),
                            'date': email_message.get('Date', ''),
                            'message_id': email_message.get('Message-ID', ''),
                            'body': self._extract_email_body(email_message)
                        }
                        emails.append(email_info)
                        
                except Exception as e:
                    log_imap_activity(
                        self.logger, 'WARNING', 'email_parse_error',
                        config_name=config.name,
                        details={'email_id': email_id.decode()},
                        error=e
                    )
            
            return emails
            
        except Exception as e:
            log_imap_activity(
                self.logger, 'ERROR', 'continuous_fetch_error',
                config_name=config.name,
                error=e
            )
            return []
    
    def _extract_email_body(self, email_message) -> str:
        """Extract email body text."""
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
    
    def _process_new_emails_for_approval(self, config: EmailConfig, emails: List[Dict]) -> Dict:
        """Process emails for approval (like user's script logic)."""
        new_emails = []
        approved_count = 0
        rejected_count = 0
        
        for email_info in emails:
            email_id = email_info['id']
            
            # Check if it's a new email (not processed yet)
            if email_id not in self.processed_email_ids[config.id]:
                new_emails.append(email_info)
                self.processed_email_ids[config.id].add(email_id)
                
                # Check approval based on keyword filter
                is_approved = self._check_email_approval(config, email_info)
                
                subject_preview = email_info['subject'][:50] + '...' if len(email_info['subject']) > 50 else email_info['subject']
                sender = email_info['sender']
                
                if is_approved:
                    approved_count += 1
                    self.logger.info(f"✅ NUOVA MAIL APPROVATA | Account: {config.email} | Config: '{config.name}' | From: {sender} | Subject: '{subject_preview}' | Keyword: '{config.subject_filter or 'None'}' found")
                    
                    # Log to EmailLog as approved
                    EmailLog.log_activity(
                        config_id=config.id,
                        action='approved',
                        status='success',
                        message=f'Email approved - keyword "{config.subject_filter}" found',
                        email_subject=email_info['subject'],
                        email_sender=sender,
                        email_date=datetime.now()
                    )
                else:
                    rejected_count += 1
                    self.logger.info(f"❌ NUOVA MAIL NON APPROVATA | Account: {config.email} | Config: '{config.name}' | From: {sender} | Subject: '{subject_preview}' | Keyword: '{config.subject_filter or 'None'}' not found")
                    
                    # Log to EmailLog as rejected
                    EmailLog.log_activity(
                        config_id=config.id,
                        action='rejected',
                        status='warning',
                        message=f'Email rejected - keyword "{config.subject_filter}" not found',
                        email_subject=email_info['subject'],
                        email_sender=sender,
                        email_date=datetime.now()
                    )
        
        return {
            'new_emails': len(new_emails),
            'approved': approved_count,
            'rejected': rejected_count,
            'emails': new_emails
        }
    
    def _check_email_approval(self, config: EmailConfig, email_info: Dict) -> bool:
        """Check if email should be approved based on filters."""
        # If no subject filter, approve everything
        if not config.subject_filter:
            return True
        
        subject = email_info.get('subject', '').lower()
        body = email_info.get('body', '').lower()
        keyword_lower = config.subject_filter.lower()
        
        # Check if keyword is in subject or body (like user's requirement)
        if keyword_lower in subject or keyword_lower in body:
            return True
        
        return False
        
    def start_monitoring(self, interval_seconds=300):
        """Start background monitoring of all active email configurations."""
        if self.monitoring_active:
            self.logger.warning("🔄 IMAP monitoring already active")
            return
        
        self.check_interval = interval_seconds
        self.monitoring_active = True
        
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        log_imap_activity(
            self.logger, 'INFO', 'monitoring_started',
            details={'interval': f'{interval_seconds}s'}
        )
    
    def stop_monitoring(self):
        """Stop background monitoring."""
        self.monitoring_active = False
        log_imap_activity(self.logger, 'INFO', 'monitoring_stopped')
    
    def _monitor_loop(self):
        """Main monitoring loop running in background thread."""
        while self.monitoring_active:
            try:
                self._check_all_configs()
            except Exception as e:
                log_imap_activity(
                    self.logger, 'ERROR', 'monitoring_loop_error',
                    error=e
                )
            
            # Wait for next check
            time.sleep(self.check_interval)
    
    def _check_all_configs(self):
        """Check all active email configurations for new emails."""
        configs = EmailConfig.query.filter_by(is_active=True).all()
        
        if not configs:
            self.logger.debug("📭 No active email configurations to monitor")
            return
        
        log_imap_activity(
            self.logger, 'INFO', 'batch_check_start',
            details={'configs_count': len(configs)}
        )
        
        for config in configs:
            try:
                self.check_config_emails(config)
            except Exception as e:
                log_imap_activity(
                    self.logger, 'ERROR', 'config_check_failed',
                    config_name=config.name,
                    error=e
                )
                # Update config with error
                config.update_last_check(success=False, error_message=str(e))
    
    def check_config_emails(self, config: EmailConfig) -> Dict:
        """Check a specific email configuration for new emails."""
        log_imap_activity(
            self.logger, 'INFO', 'email_check_start',
            config_name=config.name,
            details={
                'server': f"{config.imap_server}:{config.imap_port}",
                'email_account': config.email,
                'folder': config.folder,
                'filters': f"Subject: {config.subject_filter or 'None'}, Sender: {config.sender_filter or 'None'}"
            }
        )
        
        try:
            # Connect to IMAP server
            mail = self._connect_to_imap(config)
            
            # Select folder
            status, messages = mail.select(config.folder)
            if status != 'OK':
                raise Exception(f"Cannot select folder '{config.folder}'")
            
            # Get message count
            message_count = int(messages[0]) if messages and messages[0] else 0
            
            log_imap_activity(
                self.logger, 'DEBUG', 'folder_selected',
                config_name=config.name,
                details={
                    'email_account': config.email,
                    'folder': config.folder, 
                    'messages': message_count,
                    'server': f"{config.imap_server}:{config.imap_port}"
                }
            )
            
            # Check for new emails (last 24 hours)
            new_emails = self._get_recent_emails(mail, config)
            
            # Close connection
            mail.close()
            mail.logout()
            
            # Process found emails
            processed_count = 0
            ignored_count = 0
            error_count = 0
            
            for email_info in new_emails:
                try:
                    action = self._process_email(config, email_info)
                    if action == 'processed':
                        processed_count += 1
                    elif action == 'ignored':
                        ignored_count += 1
                    else:
                        error_count += 1
                except Exception as e:
                    error_count += 1
                    log_imap_activity(
                        self.logger, 'WARNING', 'email_process_error',
                        config_name=config.name,
                        details={'subject': email_info.get('subject', 'Unknown')},
                        error=e
                    )
            
            # Update config status
            config.update_last_check(success=True)
            
            # Log summary
            log_imap_activity(
                self.logger, 'SUCCESS', 'email_check_complete',
                config_name=config.name,
                details={
                    'email_account': config.email,
                    'server': f"{config.imap_server}:{config.imap_port}",
                    'folder': config.folder,
                    'total_messages': message_count,
                    'new_emails': len(new_emails),
                    'processed': processed_count,
                    'ignored': ignored_count,
                    'errors': error_count
                }
            )
            
            return {
                'success': True,
                'total_messages': message_count,
                'new_emails': len(new_emails),
                'processed': processed_count,
                'ignored': ignored_count,
                'errors': error_count
            }
            
        except Exception as e:
            # Update config with error
            config.update_last_check(success=False, error_message=str(e))
            
            log_imap_activity(
                self.logger, 'ERROR', 'email_check_failed',
                config_name=config.name,
                error=e
            )
            
            raise
    
    def _connect_to_imap(self, config: EmailConfig) -> imaplib.IMAP4:
        """Establish IMAP connection with proper authentication."""
        log_imap_activity(
            self.logger, 'DEBUG', 'imap_connecting',
            config_name=config.name,
            details={
                'server': config.imap_server,
                'port': config.imap_port,
                'email_account': config.email,
                'ssl': config.use_ssl,
                'starttls': config.use_starttls
            }
        )
        
        # Create IMAP connection
        if config.use_ssl:
            mail = imaplib.IMAP4_SSL(config.imap_server, config.imap_port)
        else:
            mail = imaplib.IMAP4(config.imap_server, config.imap_port)
            if config.use_starttls:
                mail.starttls()
        
        # Authenticate
        mail.login(config.email, config.get_password())
        
        log_imap_activity(
            self.logger, 'DEBUG', 'imap_connected',
            config_name=config.name,
            details={'email_account': config.email}
        )
        
        return mail
    
    def _get_recent_emails(self, mail: imaplib.IMAP4, config: EmailConfig) -> List[Dict]:
        """Get emails from the last 24 hours."""
        # Search for recent emails
        yesterday = datetime.now() - timedelta(days=1)
        search_criteria = f'SINCE "{yesterday.strftime("%d-%b-%Y")}"'
        
        # Apply filters if configured
        if config.subject_filter:
            search_criteria += f' SUBJECT "{config.subject_filter}"'
        
        if config.sender_filter:
            search_criteria += f' FROM "{config.sender_filter}"'
        
        log_imap_activity(
            self.logger, 'DEBUG', 'email_search',
            config_name=config.name,
            details={
                'email_account': config.email,
                'folder': config.folder,
                'criteria': search_criteria
            }
        )
        
        status, messages = mail.search(None, search_criteria)
        if status != 'OK':
            return []
        
        email_ids = messages[0].split()
        emails = []
        
        # Limit to prevent overwhelming the system
        max_emails = 100
        if len(email_ids) > max_emails:
            log_imap_activity(
                self.logger, 'WARNING', 'too_many_emails',
                config_name=config.name,
                details={
                    'email_account': config.email,
                    'found': len(email_ids), 
                    'limit': max_emails
                }
            )
            email_ids = email_ids[-max_emails:]  # Get most recent
        
        for email_id in email_ids:
            try:
                # Fetch email headers
                status, msg_data = mail.fetch(email_id, '(RFC822.HEADER)')
                if status == 'OK':
                    email_message = email.message_from_bytes(msg_data[0][1])
                    
                    email_info = {
                        'id': email_id.decode(),
                        'subject': email_message.get('Subject', ''),
                        'sender': email_message.get('From', ''),
                        'date': email_message.get('Date', ''),
                        'message_id': email_message.get('Message-ID', '')
                    }
                    emails.append(email_info)
            except Exception as e:
                log_imap_activity(
                    self.logger, 'WARNING', 'email_fetch_error',
                    config_name=config.name,
                    details={'email_id': email_id.decode()},
                    error=e
                )
        
        return emails
    
    def _process_email(self, config: EmailConfig, email_info: Dict) -> str:
        """Process a single email and determine action."""
        subject = email_info.get('subject', '')
        sender = email_info.get('sender', '')
        
        log_imap_activity(
            self.logger, 'DEBUG', 'email_processing',
            config_name=config.name,
            details={
                'email_account': config.email,
                'subject': subject[:50] + '...' if len(subject) > 50 else subject,
                'sender': sender
            }
        )
        
        # Check if email should be ignored based on filters
        if not self._email_matches_filters(config, email_info):
            EmailLog.log_activity(
                config_id=config.id,
                action='ignored',
                status='warning',
                message='Email does not match configured filters',
                email_subject=subject,
                email_sender=sender,
                email_date=datetime.now()
            )
            return 'ignored'
        
        # Check for attachments if required
        if config.attachment_filter:
            # This would require fetching the full email body
            # For now, we'll assume it passes
            pass
        
        # Log as processed (in a real implementation, this would trigger manifest parsing)
        EmailLog.log_activity(
            config_id=config.id,
            action='processed',
            status='success',
            message='Email processed successfully',
            email_subject=subject,
            email_sender=sender,
            email_date=datetime.now()
        )
        
        log_imap_activity(
            self.logger, 'SUCCESS', 'email_processed',
            config_name=config.name,
            details={
                'email_account': config.email,
                'subject': subject[:30] + '...'
            }
        )
        
        return 'processed'
    
    def _email_matches_filters(self, config: EmailConfig, email_info: Dict) -> bool:
        """Check if email matches the configured filters."""
        subject = email_info.get('subject', '').lower()
        sender = email_info.get('sender', '').lower()
        
        # Subject filter
        if config.subject_filter:
            if config.subject_filter.lower() not in subject:
                return False
        
        # Sender filter
        if config.sender_filter:
            if config.sender_filter.lower() not in sender:
                return False
        
        return True
    
    def test_config_connection(self, config: EmailConfig) -> Dict:
        """Test connection to a specific email configuration."""
        log_imap_activity(
            self.logger, 'INFO', 'connection_test',
            config_name=config.name
        )
        
        try:
            mail = self._connect_to_imap(config)
            
            # Test folder selection
            status, messages = mail.select(config.folder)
            if status != 'OK':
                raise Exception(f"Cannot select folder '{config.folder}'")
            
            message_count = int(messages[0]) if messages and messages[0] else 0
            
            mail.close()
            mail.logout()
            
            log_imap_activity(
                self.logger, 'SUCCESS', 'connection_test_passed',
                config_name=config.name,
                details={'messages': message_count}
            )
            
            return {
                'success': True,
                'message_count': message_count,
                'folder': config.folder
            }
            
        except Exception as e:
            log_imap_activity(
                self.logger, 'ERROR', 'connection_test_failed',
                config_name=config.name,
                error=e
            )
            raise

# Global service instance
imap_service = IMAPMonitorService()
