# scripts/odoo_approval_handler.py
import os
import time
import json
import re
from pathlib import Path
import shutil
import logging
from .audit_logger import logger
from mcp.odoo.scripts.odoo_client import OdooClient

VAULT_PATH = Path("AI_Employee_Vault")
APPROVED = VAULT_PATH / "Approved"
DONE = VAULT_PATH / "Done"
LOGS = VAULT_PATH / "Logs"

class OdooApprovalHandler:
    def __init__(self):
        self.client = OdooClient()
        self.logger = logger
        self.logger.info("Odoo Approval Handler Initialized.")

    def scan_approved(self):
        """Scans the /Approved folder for Odoo actions."""
        files = list(APPROVED.glob("APPROVAL_*.md"))
        for file_path in files:
            self.logger.info(f"Processing approved Odoo action: {file_path.name}")
            
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Extract action and details from YAML front matter
            match = re.search(r'---
(.*?)
---', content, re.DOTALL)
            if not match:
                self.logger.error(f"No YAML metadata in {file_path.name}")
                continue
            
            try:
                # Manual parsing for simplicity in this script
                metadata = {}
                for line in match.group(1).split('
'):
                    if ':' in line:
                        k, v = line.split(':', 1)
                        metadata[k.strip()] = v.strip()
                
                action = metadata.get('action')
                details = json.loads(metadata.get('details', '{}'))
                
                if action == "post_invoice":
                    invoice_id = details.get("invoice_id")
                    result = self.client.post_invoice(invoice_id)
                    self.logger.log_action("post_invoice", "human", f"invoice_{invoice_id}", result)

                elif action == "record_payment":
                    invoice_id = details.get("invoice_id")
                    amount = details.get("amount")
                    # Assuming journal_id = 1 for now
                    result = self.client.record_payment(invoice_id, amount, journal_id=1)
                    self.logger.log_action("record_payment", "human", f"invoice_{invoice_id}", result)
                
                # Move to Done
                shutil.move(file_path, DONE / file_path.name)
                self.logger.info(f"Odoo action {action} completed for {file_path.name}")
                
            except Exception as e:
                self.logger.error(f"Error executing approved Odoo action: {e}", exc_info=True)

    def run(self, interval=30):
        self.logger.info("Odoo Approval Handler started (polling mode).")
        while True:
            try:
                self.scan_approved()
            except Exception as e:
                self.logger.error(f"Error in approval scanner loop: {e}")
            time.sleep(interval)

if __name__ == "__main__":
    handler = OdooApprovalHandler()
    handler.run()
