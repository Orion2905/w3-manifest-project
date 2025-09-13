#!/usr/bin/env python
"""
Script per debug permessi utente admin
"""
import sys
import os

# Aggiungi il percorso del backend al Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.rbac import Role, Permission

def debug_admin_permissions():
    """Debug dei permessi dell'utente admin."""
    app = create_app()
    
    with app.app_context():
        print("🔍 DEBUG PERMESSI UTENTE ADMIN")
        print("=" * 50)
        
        # Trova l'utente admin
        admin_user = User.query.filter_by(email='orion.stanchieri@gmail.com').first()
        if not admin_user:
            print("❌ Utente admin non trovato!")
            return
        
        print(f"👤 Utente: {admin_user.username}")
        print(f"📧 Email: {admin_user.email}")
        print(f"🏷️  Ruolo legacy: {admin_user.role}")
        print(f"🆔 Role ID: {admin_user.role_id}")
        
        # Controlla il ruolo RBAC
        print(f"\n🔍 RUOLO RBAC:")
        if admin_user.role_obj:
            role = admin_user.role_obj
            print(f"   Nome: {role.name}")
            print(f"   Display: {role.display_name}")
            print(f"   Descrizione: {role.description}")
            print(f"   Permessi collegati: {len(role.permissions)}")
            
            if role.permissions:
                print(f"\n📋 PERMESSI DEL RUOLO {role.display_name}:")
                for perm in role.permissions:
                    print(f"   - {perm.name} ({perm.resource}.{perm.action})")
            else:
                print(f"   ⚠️  NESSUN PERMESSO TROVATO PER IL RUOLO!")
        else:
            print("   ❌ Nessun ruolo RBAC assegnato!")
        
        # Testa il metodo get_permissions()
        print(f"\n🧪 TEST get_permissions():")
        permissions = admin_user.get_permissions()
        print(f"   Permessi restituiti: {len(permissions)}")
        for perm in permissions:
            print(f"   - {perm}")
        
        # Controlla tutti i ruoli disponibili
        print(f"\n📊 TUTTI I RUOLI NEL DATABASE:")
        all_roles = Role.query.all()
        for role in all_roles:
            print(f"   {role.id}: {role.name} ({role.display_name}) - {len(role.permissions)} permessi")
        
        # Controlla tutti i permessi disponibili
        print(f"\n📋 TUTTI I PERMESSI NEL DATABASE:")
        all_permissions = Permission.query.all()
        for perm in all_permissions:
            print(f"   {perm.id}: {perm.name} - {perm.description}")

if __name__ == '__main__':
    debug_admin_permissions()
