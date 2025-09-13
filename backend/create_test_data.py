#!/usr/bin/env python
"""
Script per creare dati di test per manifest e ordini
"""
import sys
import os

# Aggiungi il percorso del backend al Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.manifest_email import ManifestEmail
from app.models.order import Order
from datetime import datetime, date, time

def create_test_data():
    """Crea dati di test per manifest e ordini."""
    app = create_app()
    
    with app.app_context():
        print("📊 CREAZIONE DATI DI TEST")
        print("=" * 50)
        
        # Crea alcuni manifest email di test
        test_manifests = [
            {
                'email_subject': 'Test Manifest 1 - Tour 01.07',
                'email_sender': 'orders@test.com',
                'email_date': datetime(2025, 9, 10, 10, 0),
                'email_message_id': 'test001@manifest.system',
                'processing_status': 'completed',
                'processing_completed_at': datetime(2025, 9, 10, 10, 30),
                'services_found': 5,
                'services_processed': 5
            },
            {
                'email_subject': 'Test Manifest 2 - Transfer 02.07',
                'email_sender': 'bookings@test.com',
                'email_date': datetime(2025, 9, 11, 14, 15),
                'email_message_id': 'test002@manifest.system',
                'processing_status': 'completed',
                'processing_completed_at': datetime(2025, 9, 11, 14, 45),
                'services_found': 3,
                'services_processed': 3
            },
            {
                'email_subject': 'Test Manifest 3 - Pending',
                'email_sender': 'reservations@test.com',
                'email_date': datetime(2025, 9, 12, 9, 0),
                'email_message_id': 'test003@manifest.system',
                'processing_status': 'received',
                'services_found': 0,
                'services_processed': 0
            }
        ]
        
        created_manifests = []
        for manifest_data in test_manifests:
            manifest = ManifestEmail(**manifest_data)
            db.session.add(manifest)
            created_manifests.append(manifest)
        
        db.session.flush()  # Per ottenere gli ID
        
        # Crea alcuni ordini di test
        test_orders = [
            {
                'service_id': 'TEST001-20250910001',
                'action': 'New',
                'service_date': date(2025, 9, 15),
                'service_type': 'Arrival Transfer',
                'description': 'Airport transfer from FCO to Hotel',
                'vehicle_model': 'Mercedes E-Class',
                'vehicle_capacity': '1-3',
                'passenger_count_adults': 2,
                'passenger_count_children': 0,
                'passenger_names': ['John Doe', 'Jane Doe'],
                'contact_phone': '+39 123 456 7890',
                'pickup_location': 'FCO Airport Terminal 3',
                'pickup_time': time(10, 30),
                'status': 'pending',
                'source_manifest_id': created_manifests[0].id
            },
            {
                'service_id': 'TEST002-20250910002',
                'action': 'New',
                'service_date': date(2025, 9, 16),
                'service_type': 'Departure Transfer',
                'description': 'Hotel to airport transfer',
                'vehicle_model': 'BMW 5 Series',
                'vehicle_capacity': '1-3',
                'passenger_count_adults': 1,
                'passenger_count_children': 1,
                'passenger_names': ['Alice Smith', 'Bob Smith'],
                'contact_phone': '+39 987 654 3210',
                'pickup_location': 'Hotel Excelsior Rome',
                'pickup_time': time(8, 0),
                'status': 'approved',
                'approved_at': datetime(2025, 9, 12, 11, 0),
                'source_manifest_id': created_manifests[1].id
            },
            {
                'service_id': 'TEST003-20250910003',
                'action': 'Change',
                'service_date': date(2025, 9, 17),
                'service_type': 'Tour Service',
                'description': 'Rome city tour - Modified pickup time',
                'vehicle_model': 'Mercedes V-Class',
                'vehicle_capacity': '1-7',
                'passenger_count_adults': 4,
                'passenger_count_children': 2,
                'passenger_names': ['Family Group Johnson'],
                'contact_phone': '+39 555 123 456',
                'pickup_location': 'Hotel Forum Rome',
                'pickup_time': time(9, 30),
                'status': 'completed',
                'source_manifest_id': created_manifests[1].id
            }
        ]
        
        for order_data in test_orders:
            order = Order(**order_data)
            db.session.add(order)
        
        # Salva tutti i dati
        db.session.commit()
        
        print(f"✅ Creati {len(created_manifests)} manifest di test")
        print(f"✅ Creati {len(test_orders)} ordini di test")
        
        # Riepilogo dei dati creati
        print(f"\n📊 RIEPILOGO DATI CREATI:")
        print(f"   Manifest totali: {ManifestEmail.query.count()}")
        print(f"   Ordini totali: {Order.query.count()}")
        print(f"   Ordini pending: {Order.query.filter_by(status='pending').count()}")
        print(f"   Ordini approved: {Order.query.filter_by(status='approved').count()}")
        print(f"   Ordini completed: {Order.query.filter_by(status='completed').count()}")

if __name__ == '__main__':
    create_test_data()
