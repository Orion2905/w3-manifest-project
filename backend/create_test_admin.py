#!/usr/bin/env python3
"""
Script per creare un utente admin di test con credenziali semplici per testare le API.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user import User
from app.models.rbac import Role
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_test_admin():
    """Crea un utente admin di test."""
    app = create_app('production')
    
    with app.app_context():
        try:
            # Trova il ruolo admin
            admin_role = Role.query.filter_by(name='admin').first()
            if not admin_role:
                print("❌ Ruolo admin non trovato!")
                return False
            
            # Controlla se l'utente admin esiste già
            existing_admin = User.query.filter_by(username='admin').first()
            if existing_admin:
                print("✅ Utente admin già esistente")
                # Aggiorna la password per sicurezza
                existing_admin.password_hash = generate_password_hash('admin123')
                existing_admin.role_id = admin_role.id
                existing_admin.is_active = True
                existing_admin.is_verified = True
                existing_admin.is_locked = False
                db.session.commit()
                print("🔄 Password e ruolo admin aggiornati")
                return True
            
            # Crea nuovo utente admin
            admin_user = User(
                username='admin',
                email='admin@w3manifest.com',
                password_hash=generate_password_hash('admin123'),
                first_name='System',
                last_name='Administrator',
                role_id=admin_role.id,
                is_active=True,
                is_verified=True,
                is_locked=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.session.add(admin_user)
            db.session.commit()
            
            print("✅ Utente admin creato con successo!")
            print(f"   Username: admin")
            print(f"   Password: admin123")
            print(f"   Email: admin@w3manifest.com")
            print(f"   Ruolo: {admin_role.display_name}")
            
            return True
            
        except Exception as e:
            print(f"❌ Errore durante la creazione dell'admin: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    success = create_test_admin()
    if success:
        print("\n🎉 Pronto per testare le API admin!")
        print("Usa le credenziali: admin / admin123")
    else:
        print("\n💥 Creazione admin fallita!")
        sys.exit(1)
