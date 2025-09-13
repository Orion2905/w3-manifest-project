#!/usr/bin/env python3
"""
Simple test script to analyze manifest files without Flask dependencies.
"""

import os
import sys
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

# Simple parser without Flask dependencies
@dataclass
class ParsedService:
    """Data class for parsed service information."""
    action: str = ""
    service_id: str = ""
    service_date: Optional[str] = None
    service_type: str = ""
    description: str = ""
    
    # Vehicle info
    vehicle_model: str = ""
    vehicle_capacity: str = ""
    
    # Passenger info
    passenger_count_adults: int = 0
    passenger_count_children: int = 0
    passenger_names: List[str] = None
    
    # Contact info
    contact_phone: str = ""
    contact_email: str = ""
    
    # Location info
    pickup_location: str = ""
    pickup_time: str = ""
    dropoff_location: str = ""
    
    # Flight info
    flight_number: str = ""
    
    # Comments and special requirements
    comments: str = ""
    
    # Validation flags
    missing_data_flags: List[str] = None
    
    def __post_init__(self):
        if self.passenger_names is None:
            self.passenger_names = []
        if self.missing_data_flags is None:
            self.missing_data_flags = []

class SimpleManifestParser:
    """Simplified manifest parser for testing."""
    
    def __init__(self):
        # Regex patterns for parsing
        self.SERVICE_SEPARATOR = r'-{10,}|_{10,}|={10,}'
        
        self.ACTION_PATTERNS = {
            'new': r'\[new\]|\bnew\b',
            'change': r'\[change\]|\bchange\b',
            'cancel': r'\[cancel\]|\bcancel\b'
        }
        
        self.DATE_PATTERN = r'(\d{1,2})-(\w{3})-(\d{2})'
        self.BOOKING_PATTERN = r'Booking\s*#?:?\s*([A-Z0-9\-]+)'
        self.VEHICLE_PATTERN = r'by\s+(\w+\s+\w+)\s+for\s+(\d+(?:-\d+)?)'
        self.PASSENGER_PATTERN = r'(Adult|Child)\s+(\d+):\s*(.*?)(?=\n|$)'
        self.PHONE_PATTERN = r'(?:Cell\s+)?Phone\s*#?:?\s*([\+\d\s\-\(\)]+)'
        self.PICKUP_PATTERN = r'(?:pick\s*up|pu@)\s*(\d{1,2}:\d{2}(?:\s*[ap]m)?)'
        self.FLIGHT_PATTERN = r'Flight\s*#?:?\s*([A-Z0-9\s]+)'
        
        self.errors = []
        self.warnings = []
    
    def read_docx_file(self, file_path: str) -> str:
        """Read text content from a .docx file."""
        try:
            from docx import Document
            doc = Document(file_path)
            
            text_content = []
            for paragraph in doc.paragraphs:
                text_content.append(paragraph.text)
            
            return '\n'.join(text_content)
        
        except Exception as e:
            self.errors.append(f"Error reading file {file_path}: {str(e)}")
            return ""
    
    def split_into_services(self, content: str) -> List[str]:
        """Split content into individual service blocks."""
        # Split by separator patterns
        blocks = re.split(self.SERVICE_SEPARATOR, content)
        
        # Filter out empty blocks
        service_blocks = []
        for block in blocks:
            block = block.strip()
            if len(block) > 50:  # Minimum content length
                service_blocks.append(block)
        
        return service_blocks
    
    def parse_service_block(self, block: str) -> ParsedService:
        """Parse a single service block."""
        service = ParsedService()
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        
        # Extract action and date from first few lines
        for line in lines[:3]:
            # Check for action
            for action, pattern in self.ACTION_PATTERNS.items():
                if re.search(pattern, line, re.IGNORECASE):
                    service.action = action
                    break
            
            # Check for date
            date_match = re.search(self.DATE_PATTERN, line)
            if date_match:
                day, month, year = date_match.groups()
                service.service_date = f"{day}-{month}-{year}"
        
        # Parse the full content
        full_text = '\n'.join(lines)
        
        # Extract booking ID
        booking_match = re.search(self.BOOKING_PATTERN, full_text, re.IGNORECASE)
        if booking_match:
            service.service_id = booking_match.group(1)
        
        # Extract vehicle info
        vehicle_match = re.search(self.VEHICLE_PATTERN, full_text, re.IGNORECASE)
        if vehicle_match:
            service.vehicle_model = vehicle_match.group(1)
            service.vehicle_capacity = vehicle_match.group(2)
        
        # Extract passenger info
        passenger_matches = re.findall(self.PASSENGER_PATTERN, full_text, re.IGNORECASE)
        for passenger_type, number, name in passenger_matches:
            if passenger_type.lower() == 'adult':
                service.passenger_count_adults += 1
            else:
                service.passenger_count_children += 1
            service.passenger_names.append(name.strip())
        
        # Extract phone
        phone_match = re.search(self.PHONE_PATTERN, full_text, re.IGNORECASE)
        if phone_match:
            service.contact_phone = phone_match.group(1).strip()
        
        # Extract pickup time
        pickup_match = re.search(self.PICKUP_PATTERN, full_text, re.IGNORECASE)
        if pickup_match:
            service.pickup_time = pickup_match.group(1).strip()
        
        # Extract flight
        flight_match = re.search(self.FLIGHT_PATTERN, full_text, re.IGNORECASE)
        if flight_match:
            service.flight_number = flight_match.group(1).strip()
        
        # Store description (first 200 chars)
        service.description = full_text[:200]
        
        return service
    
    def parse_manifest_file(self, file_path: str) -> List[ParsedService]:
        """Parse a complete manifest file."""
        content = self.read_docx_file(file_path)
        if not content:
            return []
        
        service_blocks = self.split_into_services(content)
        services = []
        
        for block in service_blocks:
            service = self.parse_service_block(block)
            services.append(service)
        
        return services

def analyze_manifest_files():
    """Analyze several manifest files to understand patterns."""
    
    # Path to manifest files
    manifest_dir = Path(__file__).parent.parent / "Manifest Datarockers"
    
    if not manifest_dir.exists():
        print(f"Manifest directory not found: {manifest_dir}")
        return
    
    # Get all .docx files
    docx_files = list(manifest_dir.glob("*.docx"))
    
    # Select first 5 files for testing
    sample_files = docx_files[:5]
    
    parser = SimpleManifestParser()
    
    for file_path in sample_files:
        print(f"\n{'='*60}")
        print(f"ANALYZING: {file_path.name}")
        print(f"{'='*60}")
        
        try:
            # Read raw content first
            print("\n--- RAW CONTENT (first 500 chars) ---")
            raw_content = parser.read_docx_file(str(file_path))
            print(raw_content[:500])
            print("..." if len(raw_content) > 500 else "")
            
            # Parse services
            print("\n--- PARSED SERVICES ---")
            services = parser.parse_manifest_file(str(file_path))
            
            if services:
                for i, service in enumerate(services, 1):
                    print(f"\nService {i}:")
                    print(f"  Action: {service.action}")
                    print(f"  Service ID: {service.service_id}")
                    print(f"  Date: {service.service_date}")
                    print(f"  Vehicle: {service.vehicle_model} ({service.vehicle_capacity})")
                    print(f"  Passengers: {service.passenger_count_adults} adults, {service.passenger_count_children} children")
                    print(f"  Names: {service.passenger_names}")
                    print(f"  Phone: {service.contact_phone}")
                    print(f"  Pickup Time: {service.pickup_time}")
                    print(f"  Flight: {service.flight_number}")
            else:
                print("No services found!")
                    
        except Exception as e:
            print(f"ERROR analyzing {file_path.name}: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("W3 Manifest Parser - Simple Analysis Tool")
    print("=" * 50)
    
    analyze_manifest_files()
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
