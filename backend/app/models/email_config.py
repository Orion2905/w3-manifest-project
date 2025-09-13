"""
Email configuration models for IMAP monitoring.
"""
from app import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from app.utils.encryption import email_password_manager

class EmailConfig(db.Model):
    """Email configuration for IMAP monitoring."""
    __tablename__ = 'email_configs'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)  # Configuration name
    imap_server = Column(String(255), nullable=False)  # e.g., imap.gmail.com
    imap_port = Column(Integer, nullable=False, default=993)  # IMAP port
    email = Column(String(255), nullable=False)  # Email address
    password_hash = Column(Text, nullable=False)  # Encrypted password
    use_ssl = Column(Boolean, default=True)  # Use SSL/TLS
    use_starttls = Column(Boolean, default=False)  # Use STARTTLS
    folder = Column(String(100), default='INBOX')  # IMAP folder to monitor
    
    # Email filtering settings
    subject_filter = Column(String(255), nullable=True)  # Filter by subject
    sender_filter = Column(String(255), nullable=True)  # Filter by sender
    attachment_filter = Column(String(100), nullable=True)  # Filter by attachment type
    
    # Status and monitoring
    is_active = Column(Boolean, default=True)
    last_check = Column(DateTime, nullable=True)
    last_success = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, db.ForeignKey('users.id'), nullable=False)
    
    def set_password(self, password):
        """Set encrypted password."""
        self.password_hash = email_password_manager.encrypt_password(password)
    
    def get_password(self):
        """Get decrypted password."""
        return email_password_manager.decrypt_password(self.password_hash)
    
    def check_password(self, password):
        """Check password against encrypted version."""
        try:
            return self.get_password() == password
        except Exception:
            return False
    
    def to_dict(self, include_sensitive=False):
        """Convert to dictionary."""
        data = {
            'id': self.id,
            'name': self.name,
            'imap_server': self.imap_server,
            'imap_port': self.imap_port,
            'email': self.email,
            'use_ssl': self.use_ssl,
            'use_starttls': self.use_starttls,
            'folder': self.folder,
            'subject_filter': self.subject_filter,
            'sender_filter': self.sender_filter,
            'attachment_filter': self.attachment_filter,
            'is_active': self.is_active,
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'last_success': self.last_success.isoformat() if self.last_success else None,
            'last_error': self.last_error,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': self.created_by
        }
        
        if include_sensitive:
            # Only include for admin users, never include actual password
            data['has_password'] = bool(self.password_hash)
        
        return data
    
    def update_last_check(self, success=True, error_message=None):
        """Update monitoring status."""
        self.last_check = datetime.utcnow()
        if success:
            self.last_success = datetime.utcnow()
            self.last_error = None
        else:
            self.last_error = error_message
        db.session.commit()
    
    @staticmethod
    def get_active_configs():
        """Get all active email configurations."""
        return EmailConfig.query.filter_by(is_active=True).all()
    
    def __repr__(self):
        return f'<EmailConfig {self.name}: {self.email}>'


class EmailLog(db.Model):
    """Log of email monitoring activities."""
    __tablename__ = 'email_logs'
    
    id = Column(Integer, primary_key=True)
    config_id = Column(Integer, db.ForeignKey('email_configs.id'), nullable=False)
    
    # Email details
    email_subject = Column(String(500), nullable=True)
    email_sender = Column(String(255), nullable=True)
    email_date = Column(DateTime, nullable=True)
    
    # Processing details
    action = Column(String(50), nullable=False)  # 'downloaded', 'processed', 'error', 'ignored'
    manifest_file = Column(String(255), nullable=True)  # Downloaded manifest filename
    status = Column(String(50), nullable=False)  # 'success', 'error', 'warning'
    message = Column(Text, nullable=True)  # Status message or error details
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    config = db.relationship('EmailConfig', backref='logs')
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'config_id': self.config_id,
            'email_subject': self.email_subject,
            'email_sender': self.email_sender,
            'email_date': self.email_date.isoformat() if self.email_date else None,
            'action': self.action,
            'manifest_file': self.manifest_file,
            'status': self.status,
            'message': self.message,
            'created_at': self.created_at.isoformat()
        }
    
    @staticmethod
    def log_activity(config_id, action, status, message=None, **kwargs):
        """Log an email monitoring activity."""
        log = EmailLog(
            config_id=config_id,
            action=action,
            status=status,
            message=message,
            **kwargs
        )
        db.session.add(log)
        db.session.commit()
        return log
    
    def __repr__(self):
        return f'<EmailLog {self.action}: {self.status}>'
