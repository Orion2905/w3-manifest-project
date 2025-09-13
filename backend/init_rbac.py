#!/usr/bin/env python
"""
Script per inizializzare permessi e ruoli di default nel database
"""
import sys
import os

# Aggiungi il percorso del backend al Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.seeds import create_default_permissions, create_default_roles
from app.models.rbac import Role, Permission
from app.models.user import User

def init_rbac_system():
    """Inizializza il sistema RBAC con permessi e ruoli di default."""
    app = create_app()
    
    with app.app_context():
        print("🚀 Inizializzazione sistema RBAC...")
        
        # Step 1: Crea i permessi di default
        print("\n📋 Creazione permessi di default...")
        created_permissions = create_default_permissions()
        print(f"   ✅ Creati {len(created_permissions)} permessi")
        
        # Step 2: Crea i ruoli di default con i permessi assegnati
        print("\n🏷️  Creazione ruoli di default...")
        created_roles = create_default_roles()
        print(f"   ✅ Creati {len(created_roles)} ruoli")
        
        # Step 3: Verifica che il nostro utente admin abbia il ruolo corretto
        print("\n👤 Verifica utente admin...")
        admin_user = User.query.filter_by(email='orion.stanchieri@gmail.com').first()
        admin_role = Role.query.filter_by(name='admin').first()
        
        if admin_user and admin_role:
            admin_user.role_id = admin_role.id
            db.session.commit()
            print(f"   ✅ Utente {admin_user.username} assegnato al ruolo {admin_role.display_name}")
        
        # Step 4: Riepilogo sistema
        print("\n📊 RIEPILOGO SISTEMA RBAC:")
        
        total_permissions = Permission.query.count()
        total_roles = Role.query.count()
        
        print(f"   Permessi totali: {total_permissions}")
        print(f"   Ruoli totali: {total_roles}")
        
        # Mostra permessi per ruolo admin
        if admin_role:
            print(f"\n🔑 Permessi ruolo {admin_role.display_name}:")
            for permission in admin_role.permissions:
                print(f"   - {permission.name}: {permission.description}")
        
        print("\n✅ Inizializzazione RBAC completata!")

if __name__ == '__main__':
    init_rbac_system()
