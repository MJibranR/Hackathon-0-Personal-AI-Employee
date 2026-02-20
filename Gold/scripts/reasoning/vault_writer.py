# scripts/reasoning/vault_writer.py
import os
import datetime
from pathlib import Path
from typing import Dict, Any

VAULT_PATH = Path("AI_Employee_Vault")
PLANS = VAULT_PATH / "Plans"
DASHBOARD = VAULT_PATH / "Dashboard.md"
ACCOUNTING = VAULT_PATH / "Accounting"

class VaultWriter:
    """
    Handles file I/O for the reasoning engine.
    Ensures safe writes and cross-domain updates.
    """
    
    @staticmethod
    def write_plan(plan: Dict[str, Any]) -> str:
        """
        Writes a structured Plan markdown file.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"PLAN_{timestamp}_{plan['intent']}.md"
        filepath = PLANS / filename
        
        content = f"""---
title: {plan['title']}
priority: {plan['priority']}
created: {datetime.now().isoformat()}
status: pending
type: plan
---

# {plan['title']}

## Context
"""
        for item in plan.get('context', []):
            content += f"- **{item.get('intent', 'event')}**: {item.get('content_preview', '')}
"

        content += "
## Execution Steps
"
        for i, step in enumerate(plan['steps'], 1):
            content += f"{i}. **{step['action']}**: {step['details']} (Tool: `{step['tool']}`)
"
            
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
            
        return str(filepath)

    @staticmethod
    def update_dashboard(summary: str):
        """
        Appends a status update to the Dashboard.
        """
        if not DASHBOARD.exists():
            with open(DASHBOARD, "w", encoding="utf-8") as f:
                f.write("# Executive Dashboard

## Recent Updates
")
        
        with open(DASHBOARD, "a", encoding="utf-8") as f:
            f.write(f"- [{datetime.now().strftime('%H:%M')}] {summary}
")

    @staticmethod
    def log_accounting(entry: Dict[str, Any]):
        """
        Logs a financial event to the daily ledger.
        """
        today = datetime.now().strftime("%Y-%m-%d")
        ledger_file = ACCOUNTING / f"{today}_Ledger.md"
        
        if not ledger_file.exists():
            with open(ledger_file, "w", encoding="utf-8") as f:
                f.write("| Time | Description | Amount | Category |
|---|---|---|---|
")
        
        with open(ledger_file, "a", encoding="utf-8") as f:
            f.write(f"| {datetime.now().strftime('%H:%M')} | {entry['description']} | {entry['amount']} | {entry['category']} |
")
