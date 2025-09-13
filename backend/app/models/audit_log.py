from datetime import datetime
from app import db

class AuditLog(db.Model):
    """Audit log model for tracking user actions and system events."""
    
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # User information
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Nullable for system events
    user_email = db.Column(db.String(120))  # Store email for reference even if user is deleted
    
    # Action information
    action = db.Column(db.String(100), nullable=False)
    # Common actions: 'login', 'logout', 'order_approved', 'order_modified', 'order_cancelled', 
    # 'manifest_processed', 'user_created', 'user_updated', 'system_error', etc.
    
    resource_type = db.Column(db.String(50))  # 'order', 'user', 'manifest', 'system'
    resource_id = db.Column(db.String(100))  # ID of the affected resource
    
    # Order-specific tracking
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=True)
    order_service_id = db.Column(db.String(100))  # ServiceID for reference
    
    # Request information
    ip_address = db.Column(db.String(45))  # IPv6 support
    user_agent = db.Column(db.String(500))
    request_method = db.Column(db.String(10))
    request_path = db.Column(db.String(500))
    
    # Change tracking
    old_values = db.Column(db.JSON)  # Previous values (for updates)
    new_values = db.Column(db.JSON)  # New values (for updates/creates)
    
    # Additional context
    description = db.Column(db.String(500))
    details = db.Column(db.JSON)  # Additional context data (renamed from metadata)
    
    # Status and error information
    status = db.Column(db.String(20), default='success')  # 'success', 'error', 'warning'
    error_message = db.Column(db.Text)
    
    # Timing
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    duration_ms = db.Column(db.Integer)  # Request duration in milliseconds
    
    def __init__(self, action, user_id=None, user_email=None, **kwargs):
        self.action = action
        self.user_id = user_id
        self.user_email = user_email
        
        # Set other attributes from kwargs
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @classmethod
    def log_user_action(cls, action, user, resource_type=None, resource_id=None, 
                       description=None, old_values=None, new_values=None, **kwargs):
        """Log a user action."""
        log_entry = cls(
            action=action,
            user_id=user.id if user else None,
            user_email=user.email if user else None,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            description=description,
            old_values=old_values,
            new_values=new_values,
            **kwargs
        )
        
        db.session.add(log_entry)
        db.session.commit()
        return log_entry
    
    @classmethod
    def log_system_event(cls, action, description=None, details=None, status='success', 
                        error_message=None, **kwargs):
        """Log a system event."""
        log_entry = cls(
            action=action,
            resource_type='system',
            description=description,
            details=details,
            status=status,
            error_message=error_message,
            **kwargs
        )
        
        db.session.add(log_entry)
        db.session.commit()
        return log_entry
    
    @classmethod
    def log_order_action(cls, action, order, user=None, description=None, 
                        old_values=None, new_values=None, **kwargs):
        """Log an order-related action."""
        log_entry = cls(
            action=action,
            user_id=user.id if user else None,
            user_email=user.email if user else None,
            resource_type='order',
            resource_id=str(order.id),
            order_id=order.id,
            order_service_id=order.service_id,
            description=description,
            old_values=old_values,
            new_values=new_values,
            **kwargs
        )
        
        db.session.add(log_entry)
        db.session.commit()
        return log_entry
    
    @classmethod
    def log_manifest_processed(cls, manifest_email, services_processed, services_failed, 
                              duration_ms=None, **kwargs):
        """Log manifest processing completion."""
        log_entry = cls(
            action='manifest_processed',
            resource_type='manifest',
            resource_id=str(manifest_email.id),
            description=f"Processed {services_processed} services, {services_failed} failed",
            details={
                'email_subject': manifest_email.email_subject,
                'email_sender': manifest_email.email_sender,
                'services_found': manifest_email.services_found,
                'services_processed': services_processed,
                'services_failed': services_failed
            },
            duration_ms=duration_ms,
            status='success' if services_failed == 0 else 'warning',
            **kwargs
        )
        
        db.session.add(log_entry)
        db.session.commit()
        return log_entry
    
    def to_dict(self):
        """Convert audit log to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_email': self.user_email,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'order_id': self.order_id,
            'order_service_id': self.order_service_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'request_method': self.request_method,
            'request_path': self.request_path,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'description': self.description,
            'details': self.details,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'duration_ms': self.duration_ms
        }
    
    def __repr__(self):
        return f'<AuditLog {self.id}: {self.action} by {self.user_email or "system"}>'
