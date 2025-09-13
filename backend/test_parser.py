#!/usr/bin/env python3
"""
Test script to analyze manifest files and understand their structure.
This script helps us develop and refine the manifest parser.
"""

import os
import sys
import json
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.services.manifest_parser import ManifestParser

def analyze_manifest_files():
    """Analyze several manifest files to understand patterns."""
    
    # Path to manifest files
    manifest_dir = Path(__file__).parent.parent.parent / "Manifest Datarockers"
    
    if not manifest_dir.exists():
        print(f"Manifest directory not found: {manifest_dir}")
        return
    
    # Get some sample files for analysis
    sample_files = [
        "01.07 TRF.docx",
        "02.07 Tour.docx", 
        "03.07 trf.docx",
        "08.07 specialty.docx",
        "Cax manifest via mail 07.07.docx"
    ]
    
    parser = ManifestParser()
    
    for filename in sample_files:
        file_path = manifest_dir / filename
        
        if not file_path.exists():
            print(f"File not found: {filename}")
            continue
        
        print(f"\n{'='*60}")
        print(f"ANALYZING: {filename}")
        print(f"{'='*60}")
        
        try:
            # Read raw content first
            print("\n--- RAW CONTENT (first 1000 chars) ---")
            raw_content = parser.read_docx_file(str(file_path))
            print(raw_content[:1000])
            print("..." if len(raw_content) > 1000 else "")
            
            # Parse services
            print("\n--- PARSED SERVICES ---")
            services = parser.parse_manifest_file(str(file_path))
            
            if services:
                for i, service in enumerate(services, 1):
                    print(f"\nService {i}:")
                    print(f"  Action: {service.action}")
                    print(f"  Service ID: {service.service_id}")
                    print(f"  Date: {service.service_date}")
                    print(f"  Type: {service.service_type}")
                    print(f"  Description: {service.description[:100]}...")
                    print(f"  Vehicle: {service.vehicle_model} ({service.vehicle_capacity})")
                    print(f"  Passengers: {service.passenger_count_adults} adults, {service.passenger_count_children} children")
                    print(f"  Names: {service.passenger_names}")
                    print(f"  Phone: {service.contact_phone}")
                    print(f"  Pickup Location: {service.pickup_location}")
                    print(f"  Pickup Time: {service.pickup_time}")
                    print(f"  Missing Data: {service.missing_data_flags}")
            else:
                print("No services found!")
            
            # Show errors and warnings
            if parser.get_errors():
                print(f"\n--- ERRORS ---")
                for error in parser.get_errors():
                    print(f"  ERROR: {error}")
            
            if parser.get_warnings():
                print(f"\n--- WARNINGS ---")
                for warning in parser.get_warnings():
                    print(f"  WARNING: {warning}")
                    
        except Exception as e:
            print(f"ERROR analyzing {filename}: {str(e)}")
            import traceback
            traceback.print_exc()

def test_specific_patterns():
    """Test specific regex patterns on sample text."""
    
    print("\n" + "="*60)
    print("TESTING REGEX PATTERNS")
    print("="*60)
    
    # Sample text patterns to test
    test_texts = [
        "[New] 10-Jul-25",
        "[Change] 15-Aug-25", 
        "[Cancel] 20-Sep-25",
        "Booking #: 12871711-DI23278963153",
        "by Mercedes E for 1-2",
        "Adult 1: Mrs. ELLEN BERRY",
        "Child 1: Master JOHN DOE",
        "Cell Phone #: +19494022905",
        "pick up 3:30 am",
        "pu@ 14:15",
        "Hotel Name: Hotel Eden Roc",
        "Address : Via Pasitea 207, Positano",
        "Flight#: LH 5686",
        "Comments#: UPGRADED DUE TO LUGGAGE"
    ]
    
    parser = ManifestParser()
    
    # Test action patterns
    print("\n--- Action Patterns ---")
    for text in test_texts[:3]:
        for action, pattern in parser.ACTION_PATTERNS.items():
            import re
            if re.search(pattern, text, re.IGNORECASE):
                print(f"'{text}' -> Action: {action}")
    
    # Test date pattern
    print("\n--- Date Patterns ---")
    import re
    for text in test_texts[:3]:
        match = re.search(parser.DATE_PATTERN, text)
        if match:
            print(f"'{text}' -> Date parts: {match.groups()}")
    
    # Test booking pattern
    print("\n--- Booking Patterns ---")
    for text in test_texts:
        match = re.search(parser.BOOKING_PATTERN, text, re.IGNORECASE)
        if match:
            print(f"'{text}' -> Booking: {match.group(1)}")
    
    # Test vehicle pattern
    print("\n--- Vehicle Patterns ---")
    for text in test_texts:
        match = re.search(parser.VEHICLE_PATTERN, text, re.IGNORECASE)
        if match:
            print(f"'{text}' -> Vehicle: {match.group(1)}, Capacity: {match.group(2)}")

if __name__ == "__main__":
    print("W3 Manifest Parser - Analysis Tool")
    print("=" * 50)
    
    # Test patterns first
    test_specific_patterns()
    
    # Then analyze actual files
    analyze_manifest_files()
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
