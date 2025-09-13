"""
Database seed data for roles and permissions initialization.
"""
from datetime import datetime
from app import db
from app.models.rbac import Role, Permission

def create_default_permissions():
    """Create default permissions for the application."""
    
    # Define all permissions with resource and action
    default_permissions = [
        # Dashboard permissions
        ('dashboard', 'view', 'View dashboard'),
        ('dashboard', 'analytics', 'View analytics dashboard'),
        
        # User management permissions
        ('users', 'create', 'Create new users'),
        ('users', 'read', 'View users'),
        ('users', 'update', 'Update users'),
        ('users', 'delete', 'Delete users'),
        ('users', 'manage_roles', 'Manage user roles'),
        ('users', 'reset_password', 'Reset user passwords'),
        
        # Order management permissions
        ('orders', 'create', 'Create new orders'),
        ('orders', 'read', 'View orders'),
        ('orders', 'update', 'Update orders'),
        ('orders', 'delete', 'Delete orders'),
        ('orders', 'export', 'Export orders'),
        ('orders', 'assign', 'Assign orders to users'),
        
        # Manifest management permissions
        ('manifests', 'upload', 'Upload manifest files'),
        ('manifests', 'read', 'View manifests'),
        ('manifests', 'update', 'Update manifests'),
        ('manifests', 'delete', 'Delete manifests'),
        ('manifests', 'parse', 'Parse manifest files'),
        ('manifests', 'approve', 'Approve manifest processing'),
        ('manifests', 'export', 'Export manifest data'),
        
        # System administration permissions
        ('system', 'logs', 'View system logs'),
        ('system', 'settings', 'Manage system settings'),
        ('system', 'backup', 'Perform system backups'),
        ('system', 'maintenance', 'System maintenance mode'),
        
        # Reporting permissions
        ('reports', 'view', 'View reports'),
        ('reports', 'create', 'Create custom reports'),
        ('reports', 'export', 'Export reports'),
        ('reports', 'schedule', 'Schedule automated reports'),
        
        # API permissions
        ('api', 'access', 'Access API endpoints'),
        ('api', 'admin', 'Administrative API access'),
    ]
    
    created_permissions = []
    
    for resource, action, description in default_permissions:
        # Check if permission already exists
        existing_permission = Permission.query.filter_by(
            resource=resource, 
            action=action
        ).first()
        
        if not existing_permission:
            permission = Permission(
                name=f"{resource}.{action}",
                resource=resource,
                action=action,
                description=description
            )
            db.session.add(permission)
            created_permissions.append(permission)
    
    db.session.commit()
    return created_permissions

def create_default_roles():
    """Create default roles with appropriate permissions."""
    
    # Ensure permissions exist first
    create_default_permissions()
    
    # Define roles with their permissions
    role_permissions = {
        'admin': {
            'name': 'Administrator',
            'description': 'Full system access with all permissions',
            'permissions': [
                # Full access to everything
                'dashboard.view', 'dashboard.analytics',
                'users.create', 'users.read', 'users.update', 'users.delete', 
                'users.manage_roles', 'users.reset_password',
                'orders.create', 'orders.read', 'orders.update', 'orders.delete', 
                'orders.export', 'orders.assign',
                'manifests.upload', 'manifests.read', 'manifests.update', 
                'manifests.delete', 'manifests.parse', 'manifests.approve', 'manifests.export',
                'system.logs', 'system.settings', 'system.backup', 'system.maintenance',
                'reports.view', 'reports.create', 'reports.export', 'reports.schedule',
                'api.access', 'api.admin'
            ]
        },
        'manager': {
            'name': 'Manager',
            'description': 'Management access with most permissions except system administration',
            'permissions': [
                'dashboard.view', 'dashboard.analytics',
                'users.read', 'users.update', 'users.reset_password',
                'orders.create', 'orders.read', 'orders.update', 'orders.delete', 
                'orders.export', 'orders.assign',
                'manifests.upload', 'manifests.read', 'manifests.update', 
                'manifests.delete', 'manifests.parse', 'manifests.approve', 'manifests.export',
                'reports.view', 'reports.create', 'reports.export', 'reports.schedule',
                'api.access'
            ]
        },
        'operator': {
            'name': 'Operator',
            'description': 'Standard operational access for daily tasks',
            'permissions': [
                'dashboard.view',
                'orders.create', 'orders.read', 'orders.update', 'orders.export',
                'manifests.upload', 'manifests.read', 'manifests.update', 'manifests.parse', 'manifests.export',
                'reports.view', 'reports.export',
                'api.access'
            ]
        },
        'viewer': {
            'name': 'Viewer',
            'description': 'Read-only access to view data',
            'permissions': [
                'dashboard.view',
                'orders.read',
                'manifests.read',
                'reports.view',
                'api.access'
            ]
        }
    }
    
    created_roles = []
    
    for role_key, role_data in role_permissions.items():
        # Check if role already exists
        existing_role = Role.query.filter_by(name=role_key).first()
        
        if not existing_role:
            role = Role(
                name=role_key,
                display_name=role_data['name'],
                description=role_data['description']
            )
            
            # Add permissions to role
            for permission_name in role_data['permissions']:
                permission = Permission.query.filter_by(name=permission_name).first()
                if permission:
                    role.permissions.append(permission)
            
            db.session.add(role)
            created_roles.append(role)
    
    db.session.commit()
    return created_roles

def seed_rbac_data():
    """Initialize the database with default RBAC data."""
    print("Creating default permissions...")
    permissions = create_default_permissions()
    print(f"Created {len(permissions)} permissions")
    
    print("Creating default roles...")
    roles = create_default_roles()
    print(f"Created {len(roles)} roles")
    
    print("RBAC data seeding completed successfully!")
    return {
        'permissions': len(permissions),
        'roles': len(roles)
    }

def assign_user_role(user, role_name):
    """Assign a role to a user."""
    role = Role.query.filter_by(name=role_name).first()
    if role:
        user.role_id = role.id
        user.role = role_name  # Keep legacy field in sync
        db.session.commit()
        return True
    return False

def get_role_hierarchy():
    """Get role hierarchy for permission checking."""
    return {
        'admin': 4,
        'manager': 3,
        'operator': 2,
        'viewer': 1
    }

def user_has_higher_role(user, target_role):
    """Check if user has higher role than target role."""
    hierarchy = get_role_hierarchy()
    user_level = hierarchy.get(user.role_obj.name if user.role_obj else user.role, 0)
    target_level = hierarchy.get(target_role, 0)
    return user_level > target_level
