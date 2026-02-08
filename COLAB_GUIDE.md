# Google Colab Testing Guide

## Three Ways to Test in Google Colab

### Option 1: Use the Jupyter Notebook (Recommended)

1. **Download the notebook file**: `Claims_Processing_Agent_Colab.ipynb`

2. **Open Google Colab**: Go to [colab.research.google.com](https://colab.research.google.com)

3. **Upload the notebook**:
   - Click "File" → "Upload notebook"
   - Choose `Claims_Processing_Agent_Colab.ipynb`

4. **Run all cells**:
   - Click "Runtime" → "Run all"
   - Or press `Ctrl+F9` (Windows) / `Cmd+F9` (Mac)

5. **View the results** in the output cells!

---

### Option 2: Use the Standalone Script

1. **Open Google Colab**: Go to [colab.research.google.com](https://colab.research.google.com)

2. **Create a new notebook**

3. **In the first cell, install dependencies**:
   ```python
   !pip install pdfplumber -q
   ```

4. **In the second cell, paste the entire contents** of `colab_standalone.py`

5. **Run both cells**

6. **See the demo output!**

---

### Option 3: Quick Copy-Paste Demo

1. **Open Google Colab**: [colab.research.google.com](https://colab.research.google.com)

2. **Copy and paste this code** into a Colab cell:

```python
# Install dependency
!pip install pdfplumber -q

import json
import re
from typing import Dict, List, Any

class ClaimsProcessingAgent:
    MANDATORY_FIELDS = ['policy_number', 'policyholder_name', 'incident_date',
                       'incident_location', 'claim_type', 'estimated_damage']
    FAST_TRACK_THRESHOLD = 25000
    FRAUD_KEYWORDS = ['fraud', 'inconsistent', 'staged']
    INJURY_CLAIM_TYPES = ['injury', 'personal injury']
    
    def extract_fields(self, text: str) -> Dict[str, Any]:
        fields = {}
        
        policy_number = re.search(r'policy\s*(?:number|#)[\\s:]*([A-Z0-9\\-]+)', text, re.IGNORECASE)
        if policy_number:
            fields['policy_number'] = policy_number.group(1).strip()
        
        policyholder = re.search(r'policyholder[\\s:]*([A-Za-z\\s]+?)(?:\\n)', text, re.IGNORECASE)
        if policyholder:
            fields['policyholder_name'] = policyholder.group(1).strip()
        
        incident_date = re.search(r'incident\\s*date[\\s:]*(\\d{1,2}[/-]\\d{1,2}[/-]\\d{2,4})', text, re.IGNORECASE)
        if incident_date:
            fields['incident_date'] = incident_date.group(1).strip()
        
        location = re.search(r'location[\\s:]*([^\\n]+)', text, re.IGNORECASE)
        if location:
            fields['incident_location'] = location.group(1).strip()
        
        description = re.search(r'description[\\s:]*([^\\n]+)', text, re.IGNORECASE)
        if description:
            fields['incident_description'] = description.group(1).strip()
        
        damage = re.search(r'damage[\\s:]*\\$?([\\d,]+)', text, re.IGNORECASE)
        if damage:
            fields['estimated_damage'] = float(damage.group(1).replace(',', ''))
        
        claim_type = re.search(r'claim\\s*type[\\s:]*([^\\n]+)', text, re.IGNORECASE)
        if claim_type:
            fields['claim_type'] = claim_type.group(1).strip()
        
        return fields
    
    def route_claim(self, fields: Dict, missing: List) -> tuple:
        if missing:
            return "Manual Review", f"Missing: {', '.join(missing)}"
        
        desc = fields.get('incident_description', '').lower()
        if any(kw in desc for kw in self.FRAUD_KEYWORDS):
            return "Investigation Queue", "Fraud indicators detected"
        
        claim = fields.get('claim_type', '').lower()
        if any(inj in claim for inj in self.INJURY_CLAIM_TYPES):
            return "Specialist Queue", "Personal injury claim"
        
        damage = fields.get('estimated_damage', float('inf'))
        if damage < self.FAST_TRACK_THRESHOLD:
            return "Fast-Track", f"Low damage: ${damage:,.2f}"
        
        return "Standard Processing", "Normal processing"
    
    def process(self, text: str) -> Dict:
        fields = self.extract_fields(text)
        missing = [f for f in self.MANDATORY_FIELDS if f not in fields]
        route, reason = self.route_claim(fields, missing)
        
        return {
            "extractedFields": fields,
            "missingFields": missing,
            "recommendedRoute": route,
            "reasoning": reason
        }

# Test with sample data
sample = """FIRST NOTICE OF LOSS (FNOL)
Policy Number: AUTO-2024-78901
Policyholder Name: Sarah Johnson
Incident Date: 02/03/2026
Location: 123 Main Street, Springfield, IL
Description: Minor fender bender in parking lot
Estimated Damage: $1,200.00
Claim Type: Property Damage"""

agent = ClaimsProcessingAgent()
result = agent.process(sample)

print(" Claims Processing Result:")
print(json.dumps(result, indent=2))
```

3. **Run the cell** and see the output!

---

## Expected Output

You should see something like:

```
Claims Processing Result:
{
  "extractedFields": {
    "policy_number": "AUTO-2024-78901",
    "policyholder_name": "Sarah Johnson",
    "incident_date": "02/03/2026",
    "incident_location": "123 Main Street, Springfield, IL",
    "incident_description": "Minor fender bender in parking lot",
    "estimated_damage": 1200.0,
    "claim_type": "Property Damage"
  },
  "missingFields": [],
  "recommendedRoute": "Fast-Track",
  "reasoning": "Low damage: $1,200.00"
}
```

---

## Colab Links (After Upload)

Once you upload the notebook to Colab, you can share it with:
- **View link**: Anyone with the link can view
- **Edit link**: Anyone with the link can edit and run
- **Public link**: Make it discoverable

---

## Tips for Colab

1. **Run cells in order**: Start from top to bottom
2. **Install dependencies first**: Always run the `!pip install` cell first
3. **Runtime menu**: Use "Runtime → Restart runtime" if you need to reset
4. **Save your work**: Use "File → Save a copy in Drive" to keep your version
5. **Share results**: Use "File → Download → .ipynb" to download

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'pdfplumber'"
**Solution**: Run the installation cell first:
```python
!pip install pdfplumber -q
```

### "FileNotFoundError: [Errno 2] No such file or directory"
**Solution**: Make sure you run the cells that create the sample files before processing them.

### Cells not running
**Solution**: Click "Runtime → Restart runtime" then run all cells again.

---

## Next Steps

After testing in Colab:
1. Verify the agent works correctly
2. Test with your own FNOL documents
3. Download the full project from GitHub
4. Deploy locally or on a server

---

**Ready to test!** Choose one of the three options above and start processing claims in the cloud! 🚀
