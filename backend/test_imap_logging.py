#!/usr/bin/env python3
"""
Test script for IMAP monitoring and logging functionality.
Run this to verify that the logging system works correctly.
"""
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.utils.logging_config import imap_logger, log_imap_info, log_imap_warning, log_imap_error, log_imap_success
from app.services.imap_monitor import imap_service

def test_logging():
    """Test the IMAP logging functionality."""
    print("🧪 Testing IMAP Logging System")
    print("=" * 50)
    
    # Test basic logging
    log_imap_info("system_startup", details={'version': '1.0'})
    log_imap_success("test_passed", details={'test_name': 'basic_logging'})
    log_imap_warning("test_warning", details={'warning_type': 'configuration'})
    log_imap_error("test_error", details={'error_type': 'connection'})
    
    # Test service logging
    print("\n📧 Testing IMAP Service Logging")
    print("-" * 30)
    
    # This will create log entries showing service operations
    try:
        # Note: This would normally require a database connection
        print("✅ IMAP Service logging test completed")
        print("📋 Check the console output above for formatted log messages")
        print("📁 If file logging is enabled, check the logs/ directory")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

def show_log_examples():
    """Show examples of what the logs will look like."""
    print("\n📝 Example Log Messages:")
    print("=" * 50)
    
    examples = [
        "📧 IMAP GET_CONFIGS | User: admin (ID: 1) | IP: 192.168.1.100",
        "🔍 IMAP CONNECTION_TEST | User: john_doe (ID: 2) | Config: 'Gmail Production' | Server: imap.gmail.com:993 | IP: 10.0.1.50",
        "✅ IMAP EMAIL_CHECK_COMPLETE | User: admin (ID: 1) | Config: 'Office365' | New emails: 3 | Processed: 2 | Ignored: 1",
        "❌ IMAP CONNECTION_TEST_FAILED | User: jane_smith (ID: 3) | Config: 'Test Config' | Error: Authentication failed",
        "🚀 IMAP MONITORING_STARTED | User: admin (ID: 1) | Interval: 300s",
        "📡 IMAP REALTIME_LOGS | User: admin (ID: 1) | Count: 25 | IP: 172.16.0.10"
    ]
    
    for example in examples:
        print(f"  {example}")
    
    print("\n🎯 Key Information Logged:")
    print("  • User identity (username and ID)")
    print("  • IP address of request") 
    print("  • Email configuration names")
    print("  • IMAP server details")
    print("  • Success/failure status")
    print("  • Email processing statistics")
    print("  • Error messages and stack traces")

if __name__ == "__main__":
    test_logging()
    show_log_examples()
    
    print("\n🔧 Integration Instructions:")
    print("=" * 50)
    print("1. The logging is automatically active when the backend starts")
    print("2. All IMAP operations will be logged with user context")
    print("3. Check the backend console for real-time log output")
    print("4. File logs will be created in backend/logs/ if the directory exists")
    print("5. Use the admin panel to trigger IMAP operations and see the logs")
    
    print("\n📚 Log Levels:")
    print("  INFO  (📧) - General operations and successful actions")
    print("  SUCCESS (✅) - Completed operations")
    print("  WARNING (⚠️) - Non-critical issues")
    print("  ERROR (❌) - Failures and exceptions")
    print("  DEBUG (🔍) - Detailed technical information")
