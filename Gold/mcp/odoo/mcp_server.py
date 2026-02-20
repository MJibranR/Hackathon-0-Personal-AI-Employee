# mcp/odoo/mcp_server.py
import sys
import json
import os
import argparse
from scripts.odoo_client import OdooClient
from pathlib import Path

# Paths to Vault folders
VAULT_PATH = Path("AI_Employee_Vault")
PENDING_APPROVAL = VAULT_PATH / "Pending_Approval"
APPROVED = VAULT_PATH / "Approved"
REJECTED = VAULT_PATH / "Rejected"

class OdooMCPServer:
    def __init__(self):
        self.client = OdooClient()

    def handle_tool_call(self, name: str, params: dict):
        """MCP style tool handling."""
        try:
            if name == "create_draft_invoice":
                partner_id = params.get("partner_id")
                invoice_line_ids = params.get("invoice_line_ids")
                return self.client.create_draft_invoice(partner_id, invoice_line_ids)

            elif name == "post_invoice":
                # Create approval request file instead of direct action
                invoice_id = params.get("invoice_id")
                return self._request_approval("post_invoice", {"invoice_id": invoice_id})

            elif name == "record_payment":
                # Create approval request file instead of direct action
                invoice_id = params.get("invoice_id")
                amount = params.get("amount")
                return self._request_approval("record_payment", {"invoice_id": invoice_id, "amount": amount})

            elif name == "fetch_revenue_summary":
                date_from = params.get("date_from", "2026-01-01")
                date_to = params.get("date_to", "2026-12-31")
                return self.client.fetch_revenue_summary(date_from, date_to)

            elif name == "fetch_overdue_invoices":
                return self.client.fetch_overdue_invoices()

            else:
                return {"error": f"Unknown tool: {name}"}
        except Exception as e:
            return {"error": str(e)}

    def _request_approval(self, action: str, details: dict):
        """Creates a markdown file in Pending_Approval for human-in-the-loop."""
        PENDING_APPROVAL.mkdir(parents=True, exist_ok=True)
        timestamp = os.popen('date /t').read().strip().replace('/', '') # Simple win32 timestamp
        filename = f"APPROVAL_{action}_{timestamp}.md"
        file_path = PENDING_APPROVAL / filename
        
        content = f"""---
action: {action}
details: {json.dumps(details)}
status: pending
---

# Approval Required: {action}

The AI Employee is requesting permission to perform the following action in Odoo:

**Action:** {action}
**Details:**
{json.dumps(details, indent=2)}

## Instructions
- To **APPROVE**: Move this file to `AI_Employee_Vault/Approved/`.
- To **REJECT**: Move this file to `AI_Employee_Vault/Rejected/`.
"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return {"status": "approval_required", "file": str(file_path), "message": "Action requires human approval."}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("tool_name", help="The name of the tool to call")
    parser.add_argument("params", help="JSON string of parameters")
    args = parser.parse_args()

    server = OdooMCPServer()
    params = json.loads(args.params)
    result = server.handle_tool_call(args.tool_name, params)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
