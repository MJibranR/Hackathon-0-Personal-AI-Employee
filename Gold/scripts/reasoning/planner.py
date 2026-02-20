# scripts/reasoning/planner.py
import json
import logging
from typing import List, Dict, Any
from datetime import datetime
import os
import shutil
from pathlib import Path
from .intent_classifier import IntentClassifier

VAULT_PATH = Path("AI_Employee_Vault")
PLANS_DIR = VAULT_PATH / "Plans"
DONE_DIR = VAULT_PATH / "Done"
ACCOUNTING_DIR = VAULT_PATH / "Accounting"
LOGS_DIR = VAULT_PATH / "Logs"

class Planner:
    """
    Orchestrates the reasoning process:
    1. Scans `Needs_Action`.
    2. Uses `IntentClassifier` to analyze tasks.
    3. Groups related tasks (cross-domain correlation).
    4. Generates a multi-step execution plan.
    5. Writes plan files to `Plans/`.
    """
    
    def __init__(self):
        self.classifier = IntentClassifier()
        self.logger = logging.getLogger("ReasoningEngine")
        
        # Ensure directories exist
        PLANS_DIR.mkdir(parents=True, exist_ok=True)
        ACCOUNTING_DIR.mkdir(parents=True, exist_ok=True)
        LOGS_DIR.mkdir(parents=True, exist_ok=True)

    def scan_and_plan(self, files: List[Path]) -> List[Dict[str, Any]]:
        """
        Scans a list of files from `Needs_Action`, classifies them, and generates plans.
        """
        intents = []
        file_map = {}

        # 1. Classification Phase
        for file_path in files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                classification = self.classifier.classify(content)
                classification["source_file"] = str(file_path)
                classification["content_preview"] = content[:100].replace('\n', ' ') + "..."
                
                intents.append(classification)
                file_map[file_path] = classification
                
                self.logger.info(f"Classified {file_path.name}: {classification['intent']} ({classification['confidence']*100:.0f}%)")
            except Exception as e:
                self.logger.error(f"Failed to process {file_path}: {e}")

        # 2. Cross-Domain Correlation Phase (The "Unified Logic")
        grouped_intents = self._group_intents(intents)

        plans = []
        for group_id, group in grouped_intents.items():
            plan = self._generate_multi_step_plan(group)
            if plan:
                plans.append(plan)
                self._write_plan_file(plan)

        return plans

    def _group_intents(self, intents: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Groups intents that should be handled together.
        Simple logic: Group by Client if possible, or handle 'finance' and 'communication' together if time-correlated.
        """
        groups = {}
        
        # Specific Scenario: Invoice Request AND Late Fee
        # Let's look for this specific combination across ALL pending tasks
        invoice_reqs = [i for i in intents if i['intent'] == 'invoice_request']
        late_fees = [i for i in intents if i['intent'] == 'late_fee_notice']
        
        if invoice_reqs and late_fees:
            # We found the cross-domain trigger!
            # Let's bundle them into a high-priority "Financial Health" plan
            combined_group = invoice_reqs + late_fees
            groups["urgent_financial_health"] = combined_group
            
            # Remove from general pool so they aren't processed twice
            for i in combined_group:
                if i in intents:
                    intents.remove(i)
        
        # Handle remaining intents individually or by simple type grouping
        for i, intent in enumerate(intents):
            groups[f"task_{i}"] = [intent]
            
        return groups

    def _generate_multi_step_plan(self, group: List[Dict]) -> Dict[str, Any]:
        """
        Generates a structured plan based on a group of intents.
        """
        if not group:
            return None

        # Check for our specific cross-domain scenario
        intents = [i['intent'] for i in group]
        if 'invoice_request' in intents and 'late_fee_notice' in intents:
            return self._create_financial_recovery_plan(group)
        
        # Fallback for single items
        if len(group) == 1:
            intent = group[0]
            if intent['intent'] == 'invoice_request':
                return self._create_invoice_plan(intent)
            elif intent['intent'] == 'late_fee_notice':
                return self._create_late_fee_plan(intent)
        
        return None

    def _create_financial_recovery_plan(self, group: List[Dict]) -> Dict[str, Any]:
        client_intent = next((i for i in group if i['intent'] == 'invoice_request'), {})
        fee_intent = next((i for i in group if i['intent'] == 'late_fee_notice'), {})
        
        client_name = client_intent.get('entities', {}).get('client', 'Client')
        amount = client_intent.get('entities', {}).get('amount', 0.0)
        fee_amount = fee_intent.get('entities', {}).get('amount', 0.0)

        plan = {
            "title": f"Financial Recovery: Invoice {client_name} & Handle Late Fee",
            "priority": "Critical",
            "intent": "cross_domain_recovery",
            "steps": [
                {
                    "step": 1,
                    "action": "generate_invoice",
                    "details": f"Create invoice for {client_name} amount ${amount}",
                    "tool": "odoo.create_draft_invoice"
                },
                {
                    "step": 2,
                    "action": "request_approval",
                    "details": "Submit invoice for approval before sending",
                    "tool": "human_approval"
                },
                {
                    "step": 3,
                    "action": "log_accounting",
                    "details": f"Log late fee of ${fee_amount} in Odoo expense ledger",
                    "tool": "odoo.record_expense"
                },
                {
                    "step": 4,
                    "action": "update_dashboard",
                    "details": "Update Dashboard.md with new financial status",
                    "tool": "vault_writer.update_dashboard"
                },
                {
                    "step": 5,
                    "action": "proactive_suggestion",
                    "details": "Draft suggestion to negotiate net-30 terms to net-15 to avoid future fees",
                    "tool": "llm.generate_text"
                }
            ],
            "context": group
        }
        return plan

    def _create_invoice_plan(self, intent: Dict) -> Dict[str, Any]:
        client = intent.get('entities', {}).get('client', 'Client')
        return {
            "title": f"Invoice Request: {client}",
            "priority": "High",
            "steps": [
                {"step": 1, "action": "generate_invoice", "tool": "odoo.create_draft_invoice"},
                {"step": 2, "action": "send_email", "tool": "gmail.send"}
            ],
            "context": [intent]
        }

    def _create_late_fee_plan(self, intent: Dict) -> Dict[str, Any]:
        amount = intent.get('entities', {}).get('amount', 'Unknown')
        return {
            "title": f"Process Late Fee: ${amount}",
            "priority": "Medium",
            "steps": [
                {"step": 1, "action": "log_expense", "tool": "odoo.record_expense"},
                {"step": 2, "action": "update_dashboard", "tool": "vault_writer.update_dashboard"}
            ],
            "context": [intent]
        }

    def _write_plan_file(self, plan: Dict[str, Any]):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"PLAN_{timestamp}_{plan['intent']}.md"
        filepath = PLANS_DIR / filename
        
        content = []
        content.append("---")
        content.append(f"title: {plan['title']}")
        content.append(f"priority: {plan['priority']}")
        content.append(f"created: {datetime.now().isoformat()}")
        content.append("status: pending")
        content.append("type: plan")
        content.append("---")
        content.append("")
        content.append(f"# {plan['title']}")
        content.append("")
        content.append("## Objectives")
        content.append("This plan addresses the following detected events:")
        
        for item in plan['context']:
            # Sanitize content for markdown list
            preview = item.get('content_preview', '').replace('\n', ' ')
            content.append(f"- **{item['intent']}**: {preview}")

        content.append("")
        content.append("## Execution Steps")
        for step in plan['steps']:
            content.append(f"{step['step']}. **{step['action']}**: {step['details']} (Tool: `{step['tool']}`)")

        content.append("")
        content.append("## Success Criteria")
        content.append("- [ ] All steps marked complete")
        content.append("- [ ] Dashboard updated")
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(content))
            
        self.logger.info(f"Generated Plan: {filepath}")
