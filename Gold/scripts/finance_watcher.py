# scripts/finance_watcher.py
import os
import csv
import logging
from pathlib import Path
from datetime import datetime
from .base_watcher import BaseWatcher

VAULT_PATH = Path("AI_Employee_Vault")
TRANSACTIONS_FILE = VAULT_PATH / "Accounting" / "Bank_Transactions.csv"

class FinanceWatcher(BaseWatcher):
    def __init__(self, check_interval=60):
        super().__init__(check_interval)
        self.processed_rows = set()
        # Ensure accounting directory exists
        (VAULT_PATH / "Accounting").mkdir(parents=True, exist_ok=True)
        
        # Initialize CSV if it doesn't exist
        if not TRANSACTIONS_FILE.exists():
            with open(TRANSACTIONS_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "Description", "Amount", "Status"])

    def check_for_updates(self):
        updates = []
        try:
            if not TRANSACTIONS_FILE.exists():
                return []

            with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Create a unique ID for the transaction to avoid duplicates
                    txn_id = f"{row['Date']}_{row['Description']}_{row['Amount']}"
                    
                    if txn_id not in self.processed_rows:
                        # Only process "Pending" or new transactions
                        updates.append(row)
                        self.processed_rows.add(txn_id)
        except Exception as e:
            self.logger.error(f"Error reading Bank_Transactions.csv: {e}")
        
        return updates

    def process_update(self, update):
        desc = update['Description']
        amount = update['Amount']
        date = update['Date']
        
        title = f"Bank Alert: {desc} (${amount})"
        content = f"""**Transaction Detected**
**Date:** {date}
**Description:** {desc}
**Amount:** ${amount}

---
**Actions Required:**
- [ ] Log in Odoo
- [ ] Categorize as Expense/Income
"""
        # Flag priority if it's a late fee
        priority = "High" if "fee" in desc.lower() or "penalty" in desc.lower() else "Medium"
        
        return self.create_task_file(title, content, priority=priority, tags=["finance", "bank"])

if __name__ == "__main__":
    watcher = FinanceWatcher(check_interval=60)
    watcher.run()
