"""
Autonomous Insurance Claims Processing Agent - Colab Ready
Single-file version for easy testing in Google Colab

Just paste this entire file into a Colab cell and run!
"""

# Step 1: Install dependencies (run this first in Colab)
# !pip install pdfplumber -q

import json
import re
from typing import Dict, List, Any

# ============================================================================
# CLAIMS PROCESSING AGENT
# ============================================================================

class ClaimsProcessingAgent:
    """Agent for processing First Notice of Loss (FNOL) documents"""
    
    MANDATORY_FIELDS = [
        'policy_number', 'policyholder_name', 'incident_date',
        'incident_location', 'claim_type', 'estimated_damage'
    ]
    
    FAST_TRACK_THRESHOLD = 25000
    FRAUD_KEYWORDS = ['fraud', 'inconsistent', 'staged', 'suspicious', 'fabricated']
    INJURY_CLAIM_TYPES = ['injury', 'personal injury', 'bodily injury', 'medical']
    
    def extract_from_txt(self, txt_path: str) -> str:
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading TXT: {e}")
            return ""
    
    def extract_fields(self, text: str) -> Dict[str, Any]:
        fields = {}
        
        # Policy Information
        policy_number = re.search(r'policy\s*(?:number|#|no\.?)[\s:]*([A-Z0-9\-]+)', text, re.IGNORECASE)
        if policy_number:
            fields['policy_number'] = policy_number.group(1).strip()
        
        policyholder = re.search(r'policyholder\s*(?:name)?[\s:]*([A-Za-z\s]+?)(?:\n|Date|Policy)', text, re.IGNORECASE)
        if policyholder:
            fields['policyholder_name'] = policyholder.group(1).strip()
        
        # Incident Information
        incident_date = re.search(r'(?:incident|accident|loss)\s*date[\s:]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text, re.IGNORECASE)
        if incident_date:
            fields['incident_date'] = incident_date.group(1).strip()
        
        location = re.search(r'(?:incident\s*)?location[\s:]*([^\n]+)', text, re.IGNORECASE)
        if location:
            fields['incident_location'] = location.group(1).strip()
        
        description = re.search(r'(?:incident\s*)?description[\s:]*([^\n]+(?:\n(?!\w+:)[^\n]+)*)', text, re.IGNORECASE)
        if description:
            fields['incident_description'] = description.group(1).strip()
        
        # Damage estimate
        damage_patterns = [
            r'estimated\s*damage[\s:]*\$?([\d,]+(?:\.\d{2})?)',
            r'damage\s*estimate[\s:]*\$?([\d,]+(?:\.\d{2})?)',
        ]
        
        for pattern in damage_patterns:
            damage = re.search(pattern, text, re.IGNORECASE)
            if damage:
                damage_value = damage.group(1).replace(',', '')
                fields['estimated_damage'] = float(damage_value)
                break
        
        # Claim Type
        claim_type = re.search(r'claim\s*type[\s:]*([^\n]+)', text, re.IGNORECASE)
        if claim_type:
            fields['claim_type'] = claim_type.group(1).strip()
        
        return fields
    
    def identify_missing_fields(self, extracted_fields: Dict[str, Any]) -> List[str]:
        missing = []
        for field in self.MANDATORY_FIELDS:
            if field not in extracted_fields or not extracted_fields[field]:
                missing.append(field)
        return missing
    
    def route_claim(self, extracted_fields: Dict[str, Any], missing_fields: List[str]) -> tuple:
        reasons = []
        
        if missing_fields:
            return "Manual Review", f"Missing mandatory fields: {', '.join(missing_fields)}"
        
        description = extracted_fields.get('incident_description', '').lower()
        fraud_detected = any(keyword in description for keyword in self.FRAUD_KEYWORDS)
        
        if fraud_detected:
            return "Investigation Queue", "Potential fraud indicators detected"
        
        claim_type = extracted_fields.get('claim_type', '').lower()
        is_injury = any(injury_type in claim_type for injury_type in self.INJURY_CLAIM_TYPES)
        
        if is_injury:
            return "Specialist Queue", "Claim involves personal injury"
        
        estimated_damage = extracted_fields.get('estimated_damage', float('inf'))
        if estimated_damage < self.FAST_TRACK_THRESHOLD:
            return "Fast-Track", f"Damage (${estimated_damage:,.2f}) below ${self.FAST_TRACK_THRESHOLD:,} threshold"
        
        return "Standard Processing", f"Standard claim (damage: ${estimated_damage:,.2f})"
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        text = self.extract_from_txt(file_path)
        
        if not text:
            return {
                "error": "Failed to extract text",
                "extractedFields": {},
                "missingFields": [],
                "recommendedRoute": "Error",
                "reasoning": "Could not read document"
            }
        
        extracted_fields = self.extract_fields(text)
        missing_fields = self.identify_missing_fields(extracted_fields)
        recommended_route, reasoning = self.route_claim(extracted_fields, missing_fields)
        
        return {
            "extractedFields": extracted_fields,
            "missingFields": missing_fields,
            "recommendedRoute": recommended_route,
            "reasoning": reasoning
        }


# ============================================================================
# SAMPLE DATA
# ============================================================================

SAMPLE_FNOL_1 = """FIRST NOTICE OF LOSS (FNOL)
================================

POLICY INFORMATION
------------------
Policy Number: AUTO-2024-78901
Policyholder Name: Sarah Johnson

INCIDENT INFORMATION
--------------------
Incident Date: 02/03/2026
Location: 123 Main Street, Springfield, IL
Description: Minor fender bender in parking lot. Vehicle backing out hit a shopping cart.

ASSET DETAILS
-------------
Estimated Damage: $1,200.00

OTHER INFORMATION
-----------------
Claim Type: Property Damage
"""

SAMPLE_FNOL_2 = """FIRST NOTICE OF LOSS (FNOL)
================================

POLICY INFORMATION
------------------
Policy Number: AUTO-2024-55432
Policyholder Name: Michael Chen

INCIDENT INFORMATION
--------------------
Incident Date: 02/01/2026
Location: Highway 101 Northbound, Mile Marker 45
Description: Rear-end collision. Both drivers complained of neck pain. Airbags deployed.

ASSET DETAILS
-------------
Estimated Damage: $18,500.00

OTHER INFORMATION
-----------------
Claim Type: Personal Injury
"""

SAMPLE_FNOL_3 = """FIRST NOTICE OF LOSS (FNOL)
================================

POLICY INFORMATION
------------------
Policy Number: AUTO-2025-99234
Policyholder Name: Robert Williams

INCIDENT INFORMATION
--------------------
Incident Date: 01/28/2026
Location: Remote parking lot on Oak Street
Description: Witness statements are inconsistent. Damage pattern suggests staged incident.

ASSET DETAILS
-------------
Estimated Damage: $8,900.00

OTHER INFORMATION
-----------------
Claim Type: Property Damage
"""


# ============================================================================
# DEMO FUNCTION
# ============================================================================

def run_demo():
    """Run a demonstration of the claims processing agent"""
    
    print("="*80)
    print("AUTONOMOUS INSURANCE CLAIMS PROCESSING AGENT - DEMO")
    print("="*80)
    
    # Create sample files
    samples = {
        'sample_1.txt': SAMPLE_FNOL_1,
        'sample_2.txt': SAMPLE_FNOL_2,
        'sample_3.txt': SAMPLE_FNOL_3
    }
    
    for filename, content in samples.items():
        with open(filename, 'w') as f:
            f.write(content)
    
    print("\n Sample FNOL documents created\n")
    
    # Initialize agent
    agent = ClaimsProcessingAgent()
    
    # Process each sample
    test_cases = [
        ('sample_1.txt', 'Low-Value Damage'),
        ('sample_2.txt', 'Personal Injury'),
        ('sample_3.txt', 'Potential Fraud')
    ]
    
    for filename, description in test_cases:
        print(f"\n{'─'*80}")
        print(f" {description}")
        print(f"{'─'*80}")
        
        result = agent.process_document(filename)
        
        # Display results
        print("\n Extracted Fields:")
        for key, value in result['extractedFields'].items():
            if key in ['policy_number', 'policyholder_name', 'incident_date', 'estimated_damage', 'claim_type']:
                print(f"  • {key.replace('_', ' ').title()}: {value}")
        
        route_icons = {
            "Fast-Track": " ",
            "Specialist Queue": " ",
            "Investigation Queue": " "
        }
        
        route = result['recommendedRoute']
        icon = route_icons.get(route, " ")
        
        print(f"\n Routing Decision:")
        print(f"  {icon} {route}")
        print(f"   {result['reasoning']}")
    
    print(f"\n{'='*80}")
    print(" Demo completed successfully!")
    print("="*80)
    
    # Show JSON output example
    print("\n\nExample JSON Output:")
    print("="*80)
    result = agent.process_document('sample_1.txt')
    print(json.dumps(result, indent=2))


# ============================================================================
# RUN THE DEMO
# ============================================================================

if __name__ == "__main__":
    run_demo()
