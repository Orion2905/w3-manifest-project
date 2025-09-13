#!/usr/bin/env python
"""
Script per creare un utente di test
"""
import sys
import os

# Aggiungi il percorso del backend al Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.rbac import Role, Permission

def create_test_user():
    """Crea un utente di test per il login."""
    app = create_app()
    
    with app.app_context():
        # Controlla se l'utente esiste già
        existing_user = User.query.filter_by(email='orion.stanchieri@gmail.com').first()
        if existing_user:
            print("Utente già esistente!")
            return
        
        # Crea ruolo admin se non esiste
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(
                name='admin',
                display_name='Administrator',
                description='Full system access'
            )
            db.session.add(admin_role)
            db.session.commit()
        
        # Crea l'utente di test
        test_user = User(
            username='orion.stanchieri',
            email='orion.stanchieri@gmail.com',
            password='password123',  # Password di test
            first_name='Orion',
            last_name='Stanchieri',
            role='admin'
        )
        test_user.role_id = admin_role.id
        test_user.is_verified = True
        
        db.session.add(test_user)
        db.session.commit()
        
        print(f"Utente di test creato: {test_user.email}")
        print(f"Username: {test_user.username}")
        print("Password: password123")

if __name__ == '__main__':
    create_test_user()
