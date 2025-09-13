#!/usr/bin/env python3
"""
Script di test per il monitoraggio continuo IMAP integrato nell'API.
Simula la logica dello script dell'utente con controllo ogni 5 secondi.
"""
import requests
import time
import json

class ContinuousMonitoringTester:
    """Tester per il monitoraggio continuo IMAP."""
    
    def __init__(self, base_url="http://localhost:5000", auth_token=None):
        self.base_url = base_url
        self.auth_token = auth_token
        self.headers = {}
        if auth_token:
            self.headers['Authorization'] = f'Bearer {auth_token}'
    
    def test_continuous_monitoring_api(self):
        """Test delle API per il monitoraggio continuo."""
        print("🧪 Testing Continuous IMAP Monitoring API")
        print("=" * 60)
        
        # Test 1: Start continuous monitoring
        print("\n1. 🚀 Starting Continuous Monitoring (5 second interval)")
        response = self._start_continuous_monitoring(5)
        if response:
            print(f"   ✅ Started: {response.get('message')}")
        else:
            print("   ❌ Failed to start")
            return
        
        # Test 2: Check status
        print("\n2. 📊 Checking Status")
        status = self._get_continuous_status()
        if status:
            print(f"   📈 Continuous Active: {status.get('continuous_monitoring_active')}")
            print(f"   📈 Regular Active: {status.get('regular_monitoring_active')}")
            print(f"   🔄 Thread Alive: {status.get('continuous_thread_alive')}")
        
        # Test 3: Wait and observe (simulate running)
        print("\n3. ⏱️ Observing for 30 seconds...")
        print("   (In real implementation, you would see logs in backend console)")
        print("   Expected logs:")
        print("   - ✅ NUOVA MAIL APPROVATA | Account: xxx | Subject: 'xxx' | Keyword: 'xxx' found")
        print("   - ❌ NUOVA MAIL NON APPROVATA | Account: xxx | Subject: 'xxx' | Keyword: 'xxx' not found")
        
        time.sleep(30)
        
        # Test 4: Stop continuous monitoring
        print("\n4. 🛑 Stopping Continuous Monitoring")
        response = self._stop_continuous_monitoring()
        if response:
            print(f"   ✅ Stopped: {response.get('message')}")
        
        print("\n✅ Continuous monitoring test completed!")
    
    def _start_continuous_monitoring(self, interval_seconds=5):
        """Start continuous monitoring via API."""
        try:
            url = f"{self.base_url}/api/email-config/monitor/continuous/start"
            data = {"interval_seconds": interval_seconds}
            
            response = requests.post(url, json=data, headers=self.headers)
            if response.status_code == 200:
                return response.json().get('data', {})
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
            return None
    
    def _stop_continuous_monitoring(self):
        """Stop continuous monitoring via API."""
        try:
            url = f"{self.base_url}/api/email-config/monitor/continuous/stop"
            
            response = requests.post(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
            return None
    
    def _get_continuous_status(self):
        """Get continuous monitoring status via API."""
        try:
            url = f"{self.base_url}/api/email-config/monitor/continuous/status"
            
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json().get('data', {})
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
            return None

def show_implementation_details():
    """Show implementation details and expected behavior."""
    print("\n📋 Implementation Details")
    print("=" * 60)
    
    print("🔧 Key Features Implemented:")
    print("  • ⚡ Continuous monitoring every 5 seconds (like your script)")
    print("  • 📧 Gets latest 10 emails per check (like your script)")
    print("  • 🔍 Full email search with 'ALL' command (like your script)")
    print("  • 📝 Body and subject keyword checking")
    print("  • 📊 'NUOVA MAIL APPROVATA' / 'NUOVA MAIL NON APPROVATA' logging")
    print("  • 🎯 No duplicate processing (tracks processed email IDs)")
    print("  • 🛡️ User context tracking for all operations")
    
    print("\n📡 API Endpoints:")
    print("  POST /api/email-config/monitor/continuous/start")
    print("  POST /api/email-config/monitor/continuous/stop") 
    print("  GET  /api/email-config/monitor/continuous/status")
    
    print("\n📊 Expected Log Output (Backend Console):")
    print("  🚀 IMAP Continuous - Started successfully | User: admin | Interval: 5s")
    print("  ✅ NUOVA MAIL APPROVATA | Account: manifests@company.com | From: sender@example.com | Subject: 'Manifest for shipment 123' | Keyword: 'manifest' found")
    print("  ❌ NUOVA MAIL NON APPROVATA | Account: manifests@company.com | From: other@example.com | Subject: 'Regular email' | Keyword: 'manifest' not found")
    print("  📊 IMAP Continuous Summary | Account: manifests@company.com | New emails: 2 | Approved: 1 | Rejected: 1")
    
    print("\n🎯 How to Use:")
    print("  1. Configure your IMAP account in the admin panel")
    print("  2. Set the 'Subject Filter' to your keyword (e.g., 'manifest')")
    print("  3. Start continuous monitoring via API or admin panel")
    print("  4. Watch backend console for real-time logs")
    print("  5. Approved emails will be logged and ready for dashboard")

def show_configuration_example():
    """Show configuration example for user's use case."""
    print("\n⚙️ Configuration Example for Your Use Case")
    print("=" * 60)
    
    config_example = {
        "name": "Hostinger Manifests",
        "imap_server": "imap.hostinger.com",
        "imap_port": 143,  # or 993 for SSL
        "email": "your-email@yourdomain.com",
        "password": "your-password",
        "use_ssl": False,  # True if using port 993
        "folder": "INBOX",
        "subject_filter": "manifest",  # Your keyword
        "is_active": True
    }
    
    print("Example configuration (create via admin panel):")
    print(json.dumps(config_example, indent=2))
    
    print("\n📧 Email Processing Logic:")
    print("  • Every 5 seconds: Check latest 10 emails")
    print("  • For each NEW email:")
    print("    - Check if 'manifest' is in subject OR body")
    print("    - If YES: ✅ NUOVA MAIL APPROVATA")
    print("    - If NO:  ❌ NUOVA MAIL NON APPROVATA")
    print("  • Save approval status for dashboard integration")

if __name__ == "__main__":
    print("🧪 Continuous IMAP Monitoring - Test Suite")
    print("=" * 60)
    
    # Show implementation details
    show_implementation_details()
    show_configuration_example()
    
    print("\n🚀 To Test with Real API:")
    print("1. Start your backend server")
    print("2. Configure an IMAP account in admin panel")
    print("3. Get an admin JWT token")
    print("4. Run this script with your token")
    print("5. Check backend console for continuous monitoring logs")
    
    # Uncomment below to test with real API (need auth token)
    # auth_token = "your-jwt-token-here"
    # tester = ContinuousMonitoringTester(auth_token=auth_token)
    # tester.test_continuous_monitoring_api()
    
    print("\n✅ Implementation complete and ready for testing!")
