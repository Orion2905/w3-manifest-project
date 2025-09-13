#!/usr/bin/env python
"""
Script per visualizzare tutti gli utenti registrati e i loro ruoli
"""
import sys
import os

# Aggiungi il percorso del backend al Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.rbac import Role, Permission, UserPermission
from datetime import datetime

def list_all_users():
    """Visualizza tutti gli utenti registrati con i loro ruoli."""
    app = create_app()
    
    with app.app_context():
        print("=" * 80)
        print("ELENCO UTENTI REGISTRATI")
        print("=" * 80)
        
        users = User.query.all()
        
        if not users:
            print("Nessun utente trovato nel database.")
            return
        
        for user in users:
            print(f"\n👤 UTENTE #{user.id}")
            print(f"   Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Nome Completo: {user.first_name} {user.last_name}")
            print(f"   Ruolo Legacy: {user.role}")
            
            # Ruolo RBAC
            if user.role_obj:
                print(f"   Ruolo RBAC: {user.role_obj.display_name} ({user.role_obj.name})")
                print(f"   Descrizione Ruolo: {user.role_obj.description}")
            else:
                print(f"   Ruolo RBAC: Nessuno assegnato")
            
            # Status account
            status_icons = {
                'active': '✅' if user.is_active else '❌',
                'verified': '✅' if user.is_verified else '❌', 
                'locked': '🔒' if user.is_locked else '🔓'
            }
            
            print(f"   Status: Attivo {status_icons['active']} | Verificato {status_icons['verified']} | Bloccato {status_icons['locked']}")
            print(f"   Dipartimento: {user.department or 'Non specificato'}")
            print(f"   Telefono: {user.phone or 'Non specificato'}")
            print(f"   Timezone: {user.timezone}")
            print(f"   Lingua: {user.language}")
            print(f"   Creato il: {user.created_at.strftime('%d/%m/%Y %H:%M')}")
            print(f"   Ultimo login: {user.last_login.strftime('%d/%m/%Y %H:%M') if user.last_login else 'Mai'}")
            
            # Tentativi di login falliti
            if user.failed_login_attempts > 0:
                print(f"   ⚠️  Tentativi login falliti: {user.failed_login_attempts}")
            
            if user.locked_until:
                print(f"   🔒 Bloccato fino a: {user.locked_until.strftime('%d/%m/%Y %H:%M')}")
            
            # Permessi individuali
            user_permissions = UserPermission.query.filter_by(user_id=user.id).all()
            if user_permissions:
                print(f"   📋 Permessi Individuali:")
                for up in user_permissions:
                    status = "✅ Concesso" if up.granted else "❌ Revocato"
                    expires = f" (scade: {up.expires_at.strftime('%d/%m/%Y')})" if up.expires_at else ""
                    print(f"      - {up.permission.display_name}: {status}{expires}")
                    if up.reason:
                        print(f"        Motivo: {up.reason}")
            
            print("-" * 60)
        
        print(f"\n📊 RIEPILOGO:")
        total_users = len(users)
        active_users = len([u for u in users if u.is_active])
        verified_users = len([u for u in users if u.is_verified])
        locked_users = len([u for u in users if u.is_locked])
        
        print(f"   Totale utenti: {total_users}")
        print(f"   Utenti attivi: {active_users}")
        print(f"   Utenti verificati: {verified_users}")
        print(f"   Utenti bloccati: {locked_users}")
        
        # Riepilogo per ruoli
        print(f"\n🏷️  DISTRIBUZIONE RUOLI:")
        roles_count = {}
        for user in users:
            role_name = user.role_obj.display_name if user.role_obj else user.role
            roles_count[role_name] = roles_count.get(role_name, 0) + 1
        
        for role, count in roles_count.items():
            print(f"   {role}: {count} utenti")

def list_all_roles():
    """Visualizza tutti i ruoli disponibili."""
    app = create_app()
    
    with app.app_context():
        print("\n" + "=" * 80)
        print("RUOLI DISPONIBILI NEL SISTEMA")
        print("=" * 80)
        
        roles = Role.query.all()
        
        if not roles:
            print("Nessun ruolo RBAC configurato.")
            return
        
        for role in roles:
            print(f"\n🏷️  RUOLO: {role.display_name}")
            print(f"   Nome sistema: {role.name}")
            print(f"   Descrizione: {role.description}")
            print(f"   Creato il: {role.created_at.strftime('%d/%m/%Y %H:%M')}")
            
            # Conteggio utenti con questo ruolo
            users_with_role = User.query.filter_by(role_id=role.id).count()
            print(f"   👥 Utenti assegnati: {users_with_role}")
            
            # Permessi del ruolo
            if role.permissions:
                print(f"   📋 Permessi del ruolo:")
                for permission in role.permissions:
                    print(f"      - {permission.display_name} ({permission.name})")
                    print(f"        Risorsa: {permission.resource}")
                    if permission.description:
                        print(f"        Descrizione: {permission.description}")
            else:
                print(f"   📋 Nessun permesso assegnato")
            
            print("-" * 60)

if __name__ == '__main__':
    list_all_users()
    list_all_roles()
