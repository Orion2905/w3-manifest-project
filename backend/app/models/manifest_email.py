from datetime import datetime
from app import db

class ManifestEmail(db.Model):
    """Model for storing received manifest emails."""
    
    __tablename__ = 'manifest_emails'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Email metadata
    email_subject = db.Column(db.String(500), nullable=False)
    email_sender = db.Column(db.String(120), nullable=False)
    email_date = db.Column(db.DateTime, nullable=False)
    email_message_id = db.Column(db.String(200), unique=True, nullable=False)  # Unique email identifier
    
    # Email content
    email_body_text = db.Column(db.Text)
    email_body_html = db.Column(db.Text)
    has_attachments = db.Column(db.Boolean, default=False)
    attachment_filenames = db.Column(db.JSON)  # List of attachment filenames
    
    # Processing status
    processing_status = db.Column(db.String(50), nullable=False, default='received')
    # Possible statuses: 'received', 'processing', 'completed', 'failed', 'skipped'
    
    processing_started_at = db.Column(db.DateTime)
    processing_completed_at = db.Column(db.DateTime)
    processing_error = db.Column(db.Text)
    
    # Parsing results
    services_found = db.Column(db.Integer, default=0)
    services_processed = db.Column(db.Integer, default=0)
    services_failed = db.Column(db.Integer, default=0)
    
    # Raw content for debugging
    raw_email_content = db.Column(db.Text)  # Complete raw email
    parsed_services_data = db.Column(db.JSON)  # Parsed services before DB insertion
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Storage information (for Azure Blob)
    blob_storage_path = db.Column(db.String(500))  # Path in Azure Blob Storage
    
    def __init__(self, email_subject, email_sender, email_date, email_message_id, **kwargs):
        self.email_subject = email_subject
        self.email_sender = email_sender
        self.email_date = email_date
        self.email_message_id = email_message_id
        
        # Set other attributes from kwargs
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def start_processing(self):
        """Mark email as being processed."""
        self.processing_status = 'processing'
        self.processing_started_at = datetime.utcnow()
        db.session.commit()
    
    def complete_processing(self, services_found=0, services_processed=0, services_failed=0):
        """Mark email processing as completed."""
        self.processing_status = 'completed'
        self.processing_completed_at = datetime.utcnow()
        self.services_found = services_found
        self.services_processed = services_processed
        self.services_failed = services_failed
        db.session.commit()
    
    def fail_processing(self, error_message):
        """Mark email processing as failed."""
        self.processing_status = 'failed'
        self.processing_completed_at = datetime.utcnow()
        self.processing_error = error_message
        db.session.commit()
    
    def skip_processing(self, reason):
        """Mark email as skipped (e.g., not a manifest email)."""
        self.processing_status = 'skipped'
        self.processing_completed_at = datetime.utcnow()
        self.processing_error = f"Skipped: {reason}"
        db.session.commit()
    
    @property
    def is_processed(self):
        """Check if email has been processed."""
        return self.processing_status in ['completed', 'failed', 'skipped']
    
    @property
    def processing_duration(self):
        """Calculate processing duration in seconds."""
        if self.processing_started_at and self.processing_completed_at:
            return (self.processing_completed_at - self.processing_started_at).total_seconds()
        return None
    
    @property
    def success_rate(self):
        """Calculate success rate of service processing."""
        if self.services_found > 0:
            return (self.services_processed / self.services_found) * 100
        return 0
    
    def to_dict(self, include_content=False):
        """Convert manifest email to dictionary."""
        data = {
            'id': self.id,
            'email_subject': self.email_subject,
            'email_sender': self.email_sender,
            'email_date': self.email_date.isoformat() if self.email_date else None,
            'email_message_id': self.email_message_id,
            'has_attachments': self.has_attachments,
            'attachment_filenames': self.attachment_filenames,
            'processing_status': self.processing_status,
            'processing_started_at': self.processing_started_at.isoformat() if self.processing_started_at else None,
            'processing_completed_at': self.processing_completed_at.isoformat() if self.processing_completed_at else None,
            'processing_error': self.processing_error,
            'processing_duration': self.processing_duration,
            'services_found': self.services_found,
            'services_processed': self.services_processed,
            'services_failed': self.services_failed,
            'success_rate': self.success_rate,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'blob_storage_path': self.blob_storage_path
        }
        
        if include_content:
            data.update({
                'email_body_text': self.email_body_text,
                'email_body_html': self.email_body_html,
                'raw_email_content': self.raw_email_content,
                'parsed_services_data': self.parsed_services_data
            })
        
        return data
    
    def __repr__(self):
        return f'<ManifestEmail {self.id}: {self.email_subject} from {self.email_sender}>'
