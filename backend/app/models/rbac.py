from datetime import datetime
from app import db

class Role(db.Model):
    """Role model for role-based access control."""
    
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    permissions = db.relationship('Permission', secondary='role_permissions', back_populates='roles')
    users = db.relationship('User', back_populates='role_obj')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'is_active': self.is_active,
            'permissions': [p.to_dict() for p in self.permissions],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Role {self.name}>'


class Permission(db.Model):
    """Permission model for granular access control."""
    
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    resource = db.Column(db.String(50), nullable=False)  # 'orders', 'manifests', 'users', 'system'
    action = db.Column(db.String(50), nullable=False)    # 'create', 'read', 'update', 'delete', 'approve', 'export'
    description = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    roles = db.relationship('Role', secondary='role_permissions', back_populates='permissions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'resource': self.resource,
            'action': self.action,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Permission {self.name}>'


# Association table for many-to-many relationship between roles and permissions
role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)


class UserPermission(db.Model):
    """Individual user permissions (overrides or additional permissions)."""
    
    __tablename__ = 'user_permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), nullable=False)
    granted = db.Column(db.Boolean, default=True, nullable=False)  # True = granted, False = revoked
    granted_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    granted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime)  # Optional expiration
    reason = db.Column(db.String(255))  # Reason for granting/revoking
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], overlaps="user_permissions")
    permission = db.relationship('Permission')
    granter = db.relationship('User', foreign_keys=[granted_by])
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'permission': self.permission.to_dict(),
            'granted': self.granted,
            'granted_by': self.granted_by,
            'granted_at': self.granted_at.isoformat() if self.granted_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'reason': self.reason
        }
    
    def __repr__(self):
        return f'<UserPermission {self.user_id}:{self.permission_id}>'
