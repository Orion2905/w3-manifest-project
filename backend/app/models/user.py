from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from app import db

class User(db.Model):
    """User model for authentication and authorization."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    
    # Role-based access control
    role = db.Column(db.String(20), nullable=False, default='user')  # Legacy field
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))  # New RBAC role
    
    # Account status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    is_locked = db.Column(db.Boolean, default=False, nullable=False)
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)  # For soft deletes
    
    # Additional profile information
    department = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    timezone = db.Column(db.String(50), default='UTC')
    language = db.Column(db.String(10), default='en')
    must_change_password = db.Column(db.Boolean, default=False)  # Force password change
    
    # Relationships
    role_obj = db.relationship('Role', back_populates='users')
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic')
    user_permissions = db.relationship('UserPermission', foreign_keys='UserPermission.user_id')
    
    def __init__(self, username, email, password, first_name, last_name, role='user'):
        self.username = username
        self.email = email
        self.set_password(password)
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
    
    def set_password(self, password):
        """Set hashed password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash."""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update last login timestamp."""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def has_permission(self, permission_name, resource=None):
        """Check if user has a specific permission."""
        # Check role permissions
        if self.role_obj:
            for permission in self.role_obj.permissions:
                if permission.name == permission_name:
                    if not resource or permission.resource == resource:
                        return True
        
        # Check individual user permissions
        for user_perm in self.user_permissions:
            permission = user_perm.permission
            if permission.name == permission_name:
                if not resource or permission.resource == resource:
                    return user_perm.granted
        
        return False
    
    def has_role(self, role_name):
        """Check if user has a specific role."""
        return self.role_obj and self.role_obj.name == role_name
    
    def get_permissions(self):
        """Get all permissions for this user."""
        permissions = set()
        
        # Add role permissions
        if self.role_obj:
            for permission in self.role_obj.permissions:
                permissions.add(f"{permission.resource}.{permission.action}")
        
        # Apply individual user permissions (overrides)
        for user_perm in self.user_permissions:
            permission = user_perm.permission
            perm_name = f"{permission.resource}.{permission.action}"
            if user_perm.granted:
                permissions.add(perm_name)
            else:
                permissions.discard(perm_name)
        
        return list(permissions)
    
    def can_access_resource(self, resource):
        """Check if user can access any action on a resource."""
        # Check role permissions
        if self.role_obj:
            for permission in self.role_obj.permissions:
                if permission.resource == resource:
                    return True
        
        # Check individual permissions
        for user_perm in self.user_permissions:
            if user_perm.permission.resource == resource and user_perm.granted:
                return True
        
        return False
    
    def is_admin(self):
        """Check if user has admin role."""
        return self.has_role('admin') or self.role == 'admin'  # Backward compatibility
    
    def is_manager(self):
        """Check if user has manager role or higher."""
        return self.has_role('admin') or self.has_role('manager')
    
    def lock_account(self, until=None):
        """Lock user account."""
        self.is_locked = True
        self.locked_until = until
        db.session.commit()
    
    def unlock_account(self):
        """Unlock user account."""
        self.is_locked = False
        self.locked_until = None
        self.failed_login_attempts = 0
        db.session.commit()
    
    def increment_failed_login(self):
        """Increment failed login attempts."""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            # Lock account for 30 minutes after 5 failed attempts
            from datetime import timedelta
            self.lock_account(datetime.utcnow() + timedelta(minutes=30))
        db.session.commit()
    
    def reset_failed_login(self):
        """Reset failed login attempts."""
        self.failed_login_attempts = 0
        db.session.commit()
    
    @property
    def full_name(self):
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def display_role(self):
        """Get display-friendly role name."""
        if self.role_obj:
            return self.role_obj.display_name
        return self.role.title()  # Fallback to legacy role
    
    def to_dict(self, include_permissions=False):
        """Convert user to dictionary representation."""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'role': self.role,  # Legacy field
            'role_name': self.role_obj.name if self.role_obj else self.role,
            'role_display': self.display_role,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'is_locked': self.is_locked,
            'department': self.department,
            'phone': self.phone,
            'timezone': self.timezone,
            'language': self.language,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
        }
        
        if include_permissions:
            data['permissions'] = self.get_permissions()
        
        return data
    
    def __repr__(self):
        return f'<User {self.username}>'
