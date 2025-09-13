#!/usr/bin/env python
"""
Script per forzare l'aggiornamento dei permessi del ruolo admin
"""
import sys
import os

# Aggiungi il percorso del backend al Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.rbac import Role, Permission

def fix_admin_permissions():
    """Corregge i permessi del ruolo admin."""
    app = create_app()
    
    with app.app_context():
        print("🔧 CORREZIONE PERMESSI RUOLO ADMIN")
        print("=" * 50)
        
        # Trova il ruolo admin
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            print("❌ Ruolo admin non trovato!")
            return
        
        print(f"🏷️  Ruolo trovato: {admin_role.display_name}")
        print(f"📋 Permessi attuali: {len(admin_role.permissions)}")
        
        # Lista di tutti i permessi che l'admin dovrebbe avere
        admin_permissions = [
            # Dashboard
            'dashboard.view', 'dashboard.analytics',
            # Users
            'users.create', 'users.read', 'users.update', 'users.delete', 
            'users.manage_roles', 'users.reset_password',
            # Orders
            'orders.create', 'orders.read', 'orders.update', 'orders.delete', 
            'orders.export', 'orders.assign',
            # Manifests
            'manifests.upload', 'manifests.read', 'manifests.update', 
            'manifests.delete', 'manifests.parse', 'manifests.approve', 'manifests.export',
            # System
            'system.logs', 'system.settings', 'system.backup', 'system.maintenance',
            # Reports
            'reports.view', 'reports.create', 'reports.export', 'reports.schedule',
            # API
            'api.access', 'api.admin'
        ]
        
        print(f"🎯 Permessi da assegnare: {len(admin_permissions)}")
        
        # Pulisci i permessi esistenti
        admin_role.permissions.clear()
        print("🧹 Permessi esistenti rimossi")
        
        # Aggiungi tutti i permessi
        added_permissions = 0
        for perm_name in admin_permissions:
            permission = Permission.query.filter_by(name=perm_name).first()
            if permission:
                admin_role.permissions.append(permission)
                added_permissions += 1
                print(f"   ✅ Aggiunto: {perm_name}")
            else:
                print(f"   ❌ Permesso non trovato: {perm_name}")
        
        # Salva le modifiche
        db.session.commit()
        
        print(f"\n📊 RISULTATO:")
        print(f"   Permessi aggiunti: {added_permissions}")
        print(f"   Permessi totali ruolo admin: {len(admin_role.permissions)}")
        
        # Verifica finale
        print(f"\n🔍 VERIFICA FINALE:")
        for perm in admin_role.permissions:
            print(f"   - {perm.name}")

if __name__ == '__main__':
    fix_admin_permissions()
