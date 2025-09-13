from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import text

class Order(db.Model):
    """Order model representing parsed manifest services."""
    
    __tablename__ = 'orders'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # ServiceID - Unique identifier from manifest (e.g., 12871711-DI23278963153)
    service_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    # Basic order information
    action = db.Column(db.String(20), nullable=False)  # 'New', 'Change', 'Cancel'
    service_date = db.Column(db.Date, nullable=False, index=True)
    service_type = db.Column(db.String(100), nullable=False)  # 'Arrival Transfers', 'Departure', etc.
    description = db.Column(db.Text)
    
    # Vehicle information
    vehicle_model = db.Column(db.String(100))
    vehicle_capacity = db.Column(db.String(50))  # e.g., "1-2", "3-4"
    
    # Passenger information
    passenger_count_adults = db.Column(db.Integer, default=0)
    passenger_count_children = db.Column(db.Integer, default=0)
    passenger_names = db.Column(db.JSON)  # Array of passenger names
    
    # Contact information
    contact_phone = db.Column(db.String(50))
    contact_email = db.Column(db.String(120))
    
    # Location information
    pickup_location = db.Column(db.String(200))
    dropoff_location = db.Column(db.String(200))
    pickup_address = db.Column(db.Text)
    dropoff_address = db.Column(db.Text)
    
    # Critical timing information
    pickup_time = db.Column(db.Time)
    pickup_time_confirmed = db.Column(db.Boolean, default=False)
    
    # Flight/Transport details
    flight_number = db.Column(db.String(20))
    flight_departure_time = db.Column(db.DateTime)
    flight_arrival_time = db.Column(db.DateTime)
    train_details = db.Column(db.String(200))
    
    # Comments and notes
    operator_comments = db.Column(db.Text)
    supplier_comments = db.Column(db.Text)
    internal_notes = db.Column(db.Text)
    
    # Status and processing
    status = db.Column(db.String(50), nullable=False, default='pending')
    # Possible statuses: 'pending', 'approved', 'modified', 'cancelled', 'error', 'requires_attention'
    
    # Flags for issues
    missing_data_flags = db.Column(db.JSON)  # Array of missing data types
    has_errors = db.Column(db.Boolean, default=False)
    requires_attention = db.Column(db.Boolean, default=False)
    
    # Processing metadata
    processed_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime)
    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Integration with external system
    exported_to_external = db.Column(db.Boolean, default=False)
    exported_at = db.Column(db.DateTime)
    external_id = db.Column(db.String(100))  # ID in the external management system
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Source information
    source_manifest_id = db.Column(db.Integer, db.ForeignKey('manifest_emails.id'))
    raw_manifest_data = db.Column(db.JSON)  # Original parsed data for reference
    
    # Relationships
    approved_by = db.relationship('User', backref='approved_orders')
    source_manifest = db.relationship('ManifestEmail', backref='orders')
    audit_logs = db.relationship('AuditLog', backref='order', lazy='dynamic')
    
    def __init__(self, service_id, action, service_date, service_type, **kwargs):
        self.service_id = service_id
        self.action = action
        self.service_date = service_date
        self.service_type = service_type
        
        # Set other attributes from kwargs
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Initialize missing data flags
        self.missing_data_flags = []
        self.check_missing_data()
    
    def check_missing_data(self):
        """Check for missing critical data and update flags."""
        missing = []
        
        # Critical fields check
        if not self.pickup_time:
            missing.append('pickup_time')
        if not self.pickup_location:
            missing.append('pickup_location')
        if not self.contact_phone:
            missing.append('contact_phone')
        if not self.passenger_names:
            missing.append('passenger_names')
        if not self.vehicle_model:
            missing.append('vehicle_model')
        
        self.missing_data_flags = missing
        self.requires_attention = len(missing) > 0
        
        return missing
    
    @property
    def total_passengers(self):
        """Calculate total number of passengers."""
        return (self.passenger_count_adults or 0) + (self.passenger_count_children or 0)
    
    @property
    def status_display(self):
        """Human-readable status."""
        status_map = {
            'pending': 'In Attesa di Approvazione',
            'approved': 'Approvato',
            'modified': 'Modificato',
            'cancelled': 'Cancellato',
            'error': 'Errore',
            'requires_attention': 'Richiede Attenzione'
        }
        return status_map.get(self.status, self.status.title())
    
    def approve(self, user_id):
        """Approve the order."""
        self.status = 'approved'
        self.approved_at = datetime.utcnow()
        self.approved_by_id = user_id
        self.requires_attention = False
        db.session.commit()
    
    def cancel(self):
        """Cancel the order."""
        self.status = 'cancelled'
        db.session.commit()
    
    def mark_error(self, error_message=None):
        """Mark order as having errors."""
        self.status = 'error'
        self.has_errors = True
        self.requires_attention = True
        if error_message:
            self.internal_notes = f"{self.internal_notes or ''}\nERROR: {error_message}"
        db.session.commit()
    
    def update_data(self, **kwargs):
        """Update order data and check for missing fields."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.check_missing_data()
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self, include_raw_data=False):
        """Convert order to dictionary."""
        data = {
            'id': self.id,
            'service_id': self.service_id,
            'action': self.action,
            'service_date': self.service_date.isoformat() if self.service_date else None,
            'service_type': self.service_type,
            'description': self.description,
            'vehicle_model': self.vehicle_model,
            'vehicle_capacity': self.vehicle_capacity,
            'passenger_count_adults': self.passenger_count_adults,
            'passenger_count_children': self.passenger_count_children,
            'total_passengers': self.total_passengers,
            'passenger_names': self.passenger_names,
            'contact_phone': self.contact_phone,
            'contact_email': self.contact_email,
            'pickup_location': self.pickup_location,
            'dropoff_location': self.dropoff_location,
            'pickup_address': self.pickup_address,
            'dropoff_address': self.dropoff_address,
            'pickup_time': self.pickup_time.strftime('%H:%M') if self.pickup_time else None,
            'pickup_time_confirmed': self.pickup_time_confirmed,
            'flight_number': self.flight_number,
            'flight_departure_time': self.flight_departure_time.isoformat() if self.flight_departure_time else None,
            'flight_arrival_time': self.flight_arrival_time.isoformat() if self.flight_arrival_time else None,
            'train_details': self.train_details,
            'operator_comments': self.operator_comments,
            'supplier_comments': self.supplier_comments,
            'internal_notes': self.internal_notes,
            'status': self.status,
            'status_display': self.status_display,
            'missing_data_flags': self.missing_data_flags,
            'has_errors': self.has_errors,
            'requires_attention': self.requires_attention,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'approved_by_id': self.approved_by_id,
            'exported_to_external': self.exported_to_external,
            'exported_at': self.exported_at.isoformat() if self.exported_at else None,
            'external_id': self.external_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'source_manifest_id': self.source_manifest_id
        }
        
        if include_raw_data:
            data['raw_manifest_data'] = self.raw_manifest_data
        
        return data
    
    def __repr__(self):
        return f'<Order {self.service_id}: {self.service_type} on {self.service_date}>'
