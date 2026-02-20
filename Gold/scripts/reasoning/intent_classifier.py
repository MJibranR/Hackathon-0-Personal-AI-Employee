# scripts/reasoning/intent_classifier.py
import re
import json
from pathlib import Path
from typing import Dict, Any, List

class IntentClassifier:
    """
    Simulates an NLU intent classification system using advanced pattern matching.
    In a real system, this would call an LLM or a model like BERT.
    """
    
    PATTERNS = {
        "invoice_request": {
            "keywords": [r"invoice", r"bill", r"payment.*details", r"how.*pay"],
            "domain": "finance",
            "action": "generate_invoice"
        },
        "late_fee_notice": {
            "keywords": [r"late.*fee", r"overdue", r"penalty", r"insufficient.*funds"],
            "domain": "finance",
            "action": "log_expense"
        },
        "payment_received": {
            "keywords": [r"payment.*received", r"transfer.*complete", r"paid"],
            "domain": "finance",
            "action": "record_payment"
        },
        "meeting_request": {
            "keywords": [r"schedule", r"meet", r"calendar", r"availability"],
            "domain": "communication",
            "action": "schedule_meeting"
        }
    }

    def classify(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        intent = "unknown"
        domain = "general"
        action = "review"
        confidence = 0.0

        for intent_key, config in self.PATTERNS.items():
            for pattern in config["keywords"]:
                if re.search(pattern, text_lower):
                    intent = intent_key
                    domain = config["domain"]
                    action = config["action"]
                    confidence = 0.9 # High confidence match
                    break
            if intent != "unknown":
                break

        # Extract basic entities (mock logic)
        entities = self._extract_entities(text)

        return {
            "intent": intent,
            "domain": domain,
            "action": action,
            "confidence": confidence,
            "entities": entities
        }

    def _extract_entities(self, text: str) -> Dict[str, Any]:
        entities = {}
        
        # Simple amount extraction
        amount_match = re.search(r'\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', text)
        if amount_match:
            entities["amount"] = float(amount_match.group(1).replace(',', ''))

        # Simple client name extraction (heuristic: "Client X" or capitalized words after "from")
        # Just a placeholder for robust NER
        if "Client" in text:
            entities["client"] = "Client A" # Defaulting for demo
            
        return entities
