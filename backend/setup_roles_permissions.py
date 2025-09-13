#!/usr/bin/env python3
"""
Script per creare ruoli e autorizzazioni iniziali nel database Azure.
Crea i ruoli: admin, manager, viewer con le relative autorizzazioni.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from app import create_app, db
from app.models.user import User
from app.models.rbac import Role, Permission, UserPermission, role_permissions

def create_permissions():
    """Crea tutte le autorizzazioni necessarie"""
    permissions_data = [
        # Dashboard
        ('dashboard.view', 'dashboard', 'view', 'View dashboard'),
        ('dashboard.analytics', 'dashboard', 'analytics', 'View dashboard analytics'),
        
        # Users - Admin only
        ('users.create', 'users', 'create', 'Create users'),
        ('users.read', 'users', 'read', 'Read users'),
        ('users.update', 'users', 'update', 'Update users'),
        ('users.delete', 'users', 'delete', 'Delete users'),
        ('users.manage_roles', 'users', 'manage_roles', 'Manage user roles'),
        ('users.reset_password', 'users', 'reset_password', 'Reset user passwords'),
        
        # Orders - Manager and above
        ('orders.create', 'orders', 'create', 'Create orders'),
        ('orders.read', 'orders', 'read', 'Read orders'),
        ('orders.update', 'orders', 'update', 'Update orders'),
        ('orders.delete', 'orders', 'delete', 'Delete orders'),
        ('orders.export', 'orders', 'export', 'Export orders'),
        ('orders.assign', 'orders', 'assign', 'Assign orders'),
        
        # Manifests - Manager and above
        ('manifests.upload', 'manifests', 'upload', 'Upload manifests'),
        ('manifests.read', 'manifests', 'read', 'Read manifests'),
        ('manifests.update', 'manifests', 'update', 'Update manifests'),
        ('manifests.delete', 'manifests', 'delete', 'Delete manifests'),
        ('manifests.process', 'manifests', 'process', 'Process manifests'),
        ('manifests.export', 'manifests', 'export', 'Export manifests'),
        
        # Email Management - Admin only
        ('email.configure', 'email', 'configure', 'Configure email settings'),
        ('email.monitor', 'email', 'monitor', 'Monitor email'),
        ('email.manage', 'email', 'manage', 'Manage email'),
        
        # System Settings - Admin only
        ('system.configure', 'system', 'configure', 'Configure system settings'),
        ('system.backup', 'system', 'backup', 'System backup'),
        ('system.logs', 'system', 'logs', 'View system logs'),
        
        # Reports - All can view, Manager+ can generate
        ('reports.view', 'reports', 'view', 'View reports'),
        ('reports.generate', 'reports', 'generate', 'Generate reports'),
        ('reports.export', 'reports', 'export', 'Export reports'),
        
        # API Access
        ('api.access', 'api', 'access', 'API access'),
        ('api.admin', 'api', 'admin', 'Admin API access'),
    ]
    
    created_permissions = []
    for name, resource, action, description in permissions_data:
        permission = Permission.query.filter_by(name=name).first()
        if not permission:
            permission = Permission(
                name=name, 
                resource=resource, 
                action=action, 
                description=description
            )
            db.session.add(permission)
            print(f"✅ Created permission: {name}")
        else:
            print(f"📋 Permission exists: {name}")
        created_permissions.append(permission)
    
    db.session.commit()
    return created_permissions

def create_roles_and_assign_permissions():
    """Crea i ruoli e assegna le autorizzazioni"""
    
    # Definizione dei ruoli e delle loro autorizzazioni
    roles_data = {
        'admin': {
            'display_name': 'Administrator',
            'description': 'Administrator with full access to all features',
            'permissions': [
                # Full access to everything
                'dashboard.view', 'dashboard.analytics',
                'users.create', 'users.read', 'users.update', 'users.delete', 
                'users.manage_roles', 'users.reset_password',
                'orders.create', 'orders.read', 'orders.update', 'orders.delete', 
                'orders.export', 'orders.assign',
                'manifests.upload', 'manifests.read', 'manifests.update', 
                'manifests.delete', 'manifests.process', 'manifests.export',
                'email.configure', 'email.monitor', 'email.manage',
                'system.configure', 'system.backup', 'system.logs',
                'reports.view', 'reports.generate', 'reports.export',
                'api.access', 'api.admin'
            ]
        },
        'manager': {
            'display_name': 'Manager',
            'description': 'Manager with access to all functions except admin-only features',
            'permissions': [
                # Dashboard
                'dashboard.view', 'dashboard.analytics',
                # Users - can read but not manage roles or system users
                'users.read',
                # Orders - full access
                'orders.create', 'orders.read', 'orders.update', 'orders.delete', 
                'orders.export', 'orders.assign',
                # Manifests - full access
                'manifests.upload', 'manifests.read', 'manifests.update', 
                'manifests.delete', 'manifests.process', 'manifests.export',
                # Email - can monitor but not configure
                'email.monitor',
                # Reports - full access
                'reports.view', 'reports.generate', 'reports.export',
                # API - basic access
                'api.access'
            ]
        },
        'viewer': {
            'display_name': 'Viewer',
            'description': 'Viewer with read-only access to visualization features',
            'permissions': [
                # Dashboard - view only
                'dashboard.view',
                # Orders - read only
                'orders.read',
                # Manifests - read only
                'manifests.read',
                # Reports - view only
                'reports.view',
                # API - basic access
                'api.access'
            ]
        }
    }
    
    created_roles = []
    
    for role_name, role_info in roles_data.items():
        # Crea o trova il ruolo
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            role = Role(
                name=role_name, 
                display_name=role_info['display_name'],
                description=role_info['description']
            )
            db.session.add(role)
            db.session.flush()  # Per ottenere l'ID
            print(f"✅ Created role: {role_name}")
        else:
            print(f"📋 Role exists: {role_name}")
        
        created_roles.append(role)
        
        # Assegna le autorizzazioni al ruolo usando la relazione many-to-many
        for permission_name in role_info['permissions']:
            permission = Permission.query.filter_by(name=permission_name).first()
            if permission:
                # Verifica se l'autorizzazione è già assegnata al ruolo
                if permission not in role.permissions:
                    role.permissions.append(permission)
                    print(f"  ➕ Added permission '{permission_name}' to role '{role_name}'")
                else:
                    print(f"  📋 Permission '{permission_name}' already assigned to role '{role_name}'")
            else:
                print(f"  ❌ Permission not found: {permission_name}")
    
    db.session.commit()
    return created_roles

def update_admin_user():
    """Aggiorna l'utente admin esistente con il ruolo admin"""
    admin_user = User.query.filter_by(username='admin').first()
    if admin_user:
        admin_role = Role.query.filter_by(name='admin').first()
        if admin_role:
            admin_user.role_id = admin_role.id
            db.session.commit()
            print(f"✅ Updated user 'admin' with admin role")
        else:
            print(f"❌ Admin role not found")
    else:
        print(f"❌ Admin user not found")

def main():
    """Funzione principale"""
    print("🚀 Setting up Roles and Permissions for W3 Manifest Project")
    print("=" * 60)
    
    try:
        app = create_app()
        with app.app_context():
            print("\n📋 Creating permissions...")
            permissions = create_permissions()
            print(f"✅ Total permissions: {len(permissions)}")
            
            print("\n👥 Creating roles and assigning permissions...")
            roles = create_roles_and_assign_permissions()
            print(f"✅ Total roles: {len(roles)}")
            
            print("\n👤 Updating admin user...")
            update_admin_user()
            
            print("\n📊 Final Summary:")
            print("-" * 40)
            
            # Mostra il riepilogo
            for role in roles:
                # Usa la relazione many-to-many per ottenere le autorizzazioni del ruolo
                role_permissions = role.permissions
                
                print(f"🔐 Role: {role.name}")
                print(f"   Display Name: {role.display_name}")
                print(f"   Description: {role.description}")
                print(f"   Permissions: {len(role_permissions)}")
                
                # Mostra alcune autorizzazioni chiave
                key_permissions = [p.name for p in role_permissions[:5]]
                if len(role_permissions) > 5:
                    key_permissions.append(f"... and {len(role_permissions) - 5} more")
                print(f"   Key permissions: {', '.join(key_permissions)}")
                print()
            
            print("🎉 SUCCESS: Roles and permissions setup completed!")
            print("\n📋 Created roles:")
            print("   • admin: Full access to everything")
            print("   • manager: All functions except admin-only features")
            print("   • viewer: Read-only access to visualization features")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
