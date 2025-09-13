import re
import os
import docx
from datetime import datetime, date
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

@dataclass
class ParsedService:
    """Data class representing a parsed service from manifest."""
    action: str  # 'New', 'Change', 'Cancel'
    service_id: str  # Booking number
    service_date: date
    service_type: str
    description: str
    vehicle_model: Optional[str] = None
    vehicle_capacity: Optional[str] = None
    passenger_count_adults: int = 0
    passenger_count_children: int = 0
    passenger_names: List[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    pickup_location: Optional[str] = None
    dropoff_location: Optional[str] = None
    pickup_address: Optional[str] = None
    dropoff_address: Optional[str] = None
    pickup_time: Optional[str] = None
    pickup_time_confirmed: bool = False
    flight_number: Optional[str] = None
    flight_departure_time: Optional[datetime] = None
    flight_arrival_time: Optional[datetime] = None
    train_details: Optional[str] = None
    operator_comments: Optional[str] = None
    supplier_comments: Optional[str] = None
    missing_data_flags: List[str] = None
    raw_data: Dict[str, Any] = None

    def __post_init__(self):
        if self.passenger_names is None:
            self.passenger_names = []
        if self.missing_data_flags is None:
            self.missing_data_flags = []
        if self.raw_data is None:
            self.raw_data = {}

class ManifestParser:
    """Parser for Classic Vacations manifest documents."""
    
    # Service separator pattern
    SERVICE_SEPARATOR = r'-{70,}'
    
    # Action patterns
    ACTION_PATTERNS = {
        'new': r'\[New\]',
        'change': r'\[Change\]',
        'cancel': r'\[Cancel\]'
    }
    
    # Date pattern (e.g., "10-Jul-25")
    DATE_PATTERN = r'(\d{1,2})-([A-Za-z]{3})-(\d{2})'
    
    # Booking number pattern (e.g., "12871711-DI23278963153")
    BOOKING_PATTERN = r'Booking\s*#?:?\s*([A-Z0-9\-]+)'
    
    # Vehicle pattern (e.g., "Mercedes E for 1-2", "by Mercedes Minivan for 3-7")
    VEHICLE_PATTERN = r'(?:by\s+)?([A-Za-z\s]+?)\s+for\s+(\d+(?:\-\d+)?)'
    
    # Alternative vehicle pattern for capacity
    VEHICLE_CAPACITY_PATTERN = r'([A-Za-z\s]+?)\s+\((\d+(?:\-\d+)?)\)'
    
    # Passenger patterns
    PASSENGER_PATTERN = r'(Adult|Child)\s+\d+:\s*(.*?)(?=\n|$)'
    
    # Phone pattern
    PHONE_PATTERNS = [
        r'Cell\s*Phone\s*#:\s*([+\d\s\-\(\)]+)',
        r'Phone:\s*([+\d\s\-\(\)]+)',
        r'Tel:\s*([+\d\s\-\(\)]+)'
    ]
    
    # Pick-up time patterns
    PICKUP_TIME_PATTERNS = [
        r'pick\s*up\s*@?\s*(\d{1,2}:\d{2}\s*[apmAPM]*)',
        r'pu@?\s*(\d{1,2}:\d{2}\s*[apmAPM]*)',
        r'pickup\s*time:?\s*(\d{1,2}:\d{2}\s*[apmAPM]*)'
    ]
    
    # Flight patterns
    FLIGHT_PATTERNS = [
        r'Flight\s*#?:\s*([A-Z0-9\s]+)',
        r'Departure:\s*(\d{1,2}:\d{2}\s*[apmAPM]*)',
        r'Arrival:\s*(\d{1,2}:\d{2}\s*[apmAPM]*)'
    ]
    
    # Location patterns
    HOTEL_PATTERN = r'Hotel\s*Name:\s*(.*?)(?=\n|Address|$)'
    ADDRESS_PATTERN = r'Address\s*:\s*(.*?)(?=\n|$)'
    
    # Month mapping for date parsing
    MONTH_MAP = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def read_docx_file(self, file_path: str) -> str:
        """Read text content from a Word document."""
        try:
            doc = docx.Document(file_path)
            full_text = []
            
            for paragraph in doc.paragraphs:
                full_text.append(paragraph.text)
            
            return '\n'.join(full_text)
        
        except Exception as e:
            self.errors.append(f"Error reading document {file_path}: {str(e)}")
            return ""
    
    def parse_manifest_file(self, file_path: str) -> List[ParsedService]:
        """Parse a manifest file and return list of services."""
        content = self.read_docx_file(file_path)
        if not content:
            return []
        
        return self.parse_manifest_content(content)
    
    def parse_manifest_content(self, content: str) -> List[ParsedService]:
        """Parse manifest content and extract services."""
        services = []
        self.errors = []
        self.warnings = []
        
        # More intelligent splitting - look for action patterns that start new services
        lines = content.split('\n')
        service_blocks = []
        current_block = []
        
        for line in lines:
            line = line.strip()
            
            # Skip header/footer lines
            if ('CLASSIC VACATIONS' in line or 
                'Report Generation Date' in line or
                'From: Classic' in line or
                'To: W3' in line or
                'Email Address' in line or
                'Please send your response' in line or
                line.startswith('*') and len(line) > 40):
                continue
            
            # Check if this line starts a new service (with action and date)
            is_new_service = False
            for action_pattern in self.ACTION_PATTERNS.values():
                if re.search(action_pattern, line, re.IGNORECASE):
                    # Also check if there's a date pattern in the line
                    if re.search(self.DATE_PATTERN, line):
                        is_new_service = True
                        break
            
            # If new service and we have content in current block, save it
            if is_new_service and current_block:
                block_content = '\n'.join(current_block)
                if len(block_content.strip()) > 20:  # Minimum content
                    service_blocks.append(block_content)
                current_block = []
            
            # Add line to current block
            if line:  # Only add non-empty lines
                current_block.append(line)
        
        # Don't forget the last block
        if current_block:
            block_content = '\n'.join(current_block)
            if len(block_content.strip()) > 20:
                service_blocks.append(block_content)
        
        # Parse each service block
        for i, block in enumerate(service_blocks):
            try:
                service = self.parse_service_block(block.strip())
                if service:
                    services.append(service)
            except Exception as e:
                self.errors.append(f"Error parsing service block {i+1}: {str(e)}")
                continue
        
        return services
    
    def parse_service_block(self, block: str) -> Optional[ParsedService]:
        """Parse a single service block."""
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        
        if not lines:
            return None
        
        # Extract action and date from first line
        action, service_date = self.parse_action_and_date(lines[0])
        if not action or not service_date:
            return None
        
        # Extract booking number
        service_id = self.extract_booking_number(block)
        if not service_id:
            self.warnings.append(f"No booking number found in service block")
            return None
        
        # Extract service type and description
        service_type, description = self.extract_service_description(lines)
        
        # Create service object
        service = ParsedService(
            action=action,
            service_id=service_id,
            service_date=service_date,
            service_type=service_type,
            description=description,
            raw_data={'original_block': block}
        )
        
        # Extract additional details
        self.extract_vehicle_info(block, service)
        self.extract_passenger_info(block, service)
        self.extract_contact_info(block, service)
        self.extract_location_info(block, service)
        self.extract_timing_info(block, service)
        self.extract_flight_info(block, service)
        self.extract_comments(block, service)
        
        # Check for missing data
        self.check_missing_data(service)
        
        return service
    
    def parse_action_and_date(self, first_line: str) -> tuple:
        """Extract action and service date from first line."""
        action = None
        service_date = None
        
        # Find action
        for action_type, pattern in self.ACTION_PATTERNS.items():
            if re.search(pattern, first_line, re.IGNORECASE):
                action = action_type.title()
                break
        
        # Find date
        date_match = re.search(self.DATE_PATTERN, first_line)
        if date_match:
            day, month_str, year = date_match.groups()
            month = self.MONTH_MAP.get(month_str.lower())
            if month:
                year = 2000 + int(year)  # Convert 25 to 2025
                service_date = date(year, month, int(day))
        
        return action, service_date
    
    def extract_booking_number(self, block: str) -> Optional[str]:
        """Extract booking number from service block."""
        match = re.search(self.BOOKING_PATTERN, block, re.IGNORECASE)
        return match.group(1).strip() if match else None
    
    def extract_service_description(self, lines: List[str]) -> tuple:
        """Extract service type and description."""
        service_type = "Unknown"
        description = ""
        
        # Look for service type keywords in first few lines
        service_keywords = [
            'Arrival Transfers', 'Departure Transfers', 'City to City',
            'Tour', 'Specialty', 'Transfer'
        ]
        
        for line in lines[:5]:  # Check first 5 lines
            for keyword in service_keywords:
                if keyword.lower() in line.lower():
                    service_type = keyword
                    break
            if service_type != "Unknown":
                break
        
        # Join relevant lines for description
        description_lines = []
        for line in lines[1:10]:  # Skip first line, take next 9
            if not re.search(r'Booking\s*#:', line, re.IGNORECASE):
                description_lines.append(line)
        
        description = ' '.join(description_lines)
        
        return service_type, description
    
    def extract_vehicle_info(self, block: str, service: ParsedService):
        """Extract vehicle information."""
        # Try the first pattern: "by Mercedes E for 1-2"
        match = re.search(self.VEHICLE_PATTERN, block, re.IGNORECASE)
        if match:
            service.vehicle_model = match.group(1).strip()
            service.vehicle_capacity = match.group(2).strip()
            return
        
        # Try the second pattern: "Mercedes Minivan (3-7)"
        match = re.search(self.VEHICLE_CAPACITY_PATTERN, block, re.IGNORECASE)
        if match:
            service.vehicle_model = match.group(1).strip()
            service.vehicle_capacity = match.group(2).strip()
            return
    
    def extract_passenger_info(self, block: str, service: ParsedService):
        """Extract passenger information."""
        passengers = re.findall(self.PASSENGER_PATTERN, block, re.IGNORECASE)
        
        adults = 0
        children = 0
        names = []
        
        for passenger_type, name in passengers:
            if passenger_type.lower() == 'adult':
                adults += 1
            else:
                children += 1
            
            # Clean up name
            name = name.strip().replace(':', '').strip()
            if name:
                names.append(name)
        
        service.passenger_count_adults = adults
        service.passenger_count_children = children
        service.passenger_names = names
    
    def extract_contact_info(self, block: str, service: ParsedService):
        """Extract contact information."""
        for pattern in self.PHONE_PATTERNS:
            match = re.search(pattern, block, re.IGNORECASE)
            if match:
                service.contact_phone = match.group(1).strip()
                break
    
    def extract_location_info(self, block: str, service: ParsedService):
        """Extract pickup/dropoff location information."""
        # Hotel name
        hotel_match = re.search(self.HOTEL_PATTERN, block, re.IGNORECASE)
        if hotel_match:
            service.pickup_location = hotel_match.group(1).strip()
        
        # Address
        address_match = re.search(self.ADDRESS_PATTERN, block, re.IGNORECASE)
        if address_match:
            service.pickup_address = address_match.group(1).strip()
    
    def extract_timing_info(self, block: str, service: ParsedService):
        """Extract pickup time information."""
        for pattern in self.PICKUP_TIME_PATTERNS:
            match = re.search(pattern, block, re.IGNORECASE)
            if match:
                service.pickup_time = match.group(1).strip()
                service.pickup_time_confirmed = True
                break
    
    def extract_flight_info(self, block: str, service: ParsedService):
        """Extract flight information."""
        for pattern in self.FLIGHT_PATTERNS:
            match = re.search(pattern, block, re.IGNORECASE)
            if match and 'flight' in pattern.lower():
                service.flight_number = match.group(1).strip()
                break
    
    def extract_comments(self, block: str, service: ParsedService):
        """Extract comments and notes."""
        # Look for comments sections
        comments_patterns = [
            r'Comments\s*#?:\s*(.*?)(?=\n|$)',
            r'Supplier\s*comments\s*#?:\s*(.*?)(?=\n|$)',
            r'Notes?:\s*(.*?)(?=\n|$)'
        ]
        
        all_comments = []
        for pattern in comments_patterns:
            matches = re.findall(pattern, block, re.IGNORECASE | re.DOTALL)
            all_comments.extend(matches)
        
        if all_comments:
            service.operator_comments = '; '.join([c.strip() for c in all_comments if c.strip()])
    
    def check_missing_data(self, service: ParsedService):
        """Check for missing critical data."""
        missing = []
        
        if not service.pickup_time:
            missing.append('pickup_time')
        if not service.pickup_location:
            missing.append('pickup_location')
        if not service.contact_phone:
            missing.append('contact_phone')
        if not service.passenger_names:
            missing.append('passenger_names')
        if not service.vehicle_model:
            missing.append('vehicle_model')
        
        service.missing_data_flags = missing
    
    def get_errors(self) -> List[str]:
        """Get parsing errors."""
        return self.errors
    
    def get_warnings(self) -> List[str]:
        """Get parsing warnings."""
        return self.warnings
