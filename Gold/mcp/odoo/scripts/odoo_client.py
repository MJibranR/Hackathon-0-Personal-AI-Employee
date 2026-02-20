# mcp/odoo/scripts/odoo_client.py
import requests
import json
import os
import logging
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

class OdooClient:
    def __init__(self):
        self.url = os.getenv("ODOO_URL", "http://localhost:8069")
        self.db = os.getenv("ODOO_DB")
        self.username = os.getenv("ODOO_USER")
        self.password = os.getenv("ODOO_PASSWORD")
        self.dry_run = os.getenv("DRY_RUN", "true").lower() == "true"
        self.uid = None
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("OdooClient")

    def _json_rpc(self, url: str, method: str, params: Dict[str, Any]) -> Any:
        data = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1,
        }
        try:
            response = requests.post(f"{self.url}/jsonrpc", json=data, timeout=10)
            response.raise_for_status()
            result = response.json()
            if "error" in result:
                raise Exception(f"Odoo RPC Error: {result['error']}")
            return result.get("result")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"HTTP Request failed: {e}")
            raise

    def authenticate(self):
        if self.uid:
            return self.uid
        self.logger.info(f"Authenticating with Odoo at {self.url}...")
        self.uid = self._json_rpc(self.url, "common/login", {
            "db": self.db,
            "login": self.username,
            "password": self.password
        })
        if not self.uid:
            raise Exception("Authentication failed: Invalid credentials or database name.")
        self.logger.info(f"Authenticated with UID: {self.uid}")
        return self.uid

    def execute_kw(self, model: str, method: str, *args, **kwargs) -> Any:
        uid = self.authenticate()
        return self._json_rpc(self.url, "object/execute_kw", {
            "db": self.db,
            "uid": uid,
            "password": self.password,
            "model": model,
            "method": method,
            "args": args,
            "kwargs": kwargs
        })

    def create_draft_invoice(self, partner_id: int, invoice_line_ids: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Creates a draft invoice (account.move) in Odoo."""
        self.logger.info(f"Creating draft invoice for partner {partner_id}")
        
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': partner_id,
            'invoice_date': os.getenv("CURRENT_DATE", "2026-02-21"),
            'invoice_line_ids': [(0, 0, line) for line in invoice_line_ids]
        }

        if self.dry_run:
            self.logger.info("[DRY RUN] Skipping invoice creation.")
            return {"status": "dry_run", "data": invoice_vals}

        invoice_id = self.execute_kw('account.move', 'create', invoice_vals)
        return {"status": "success", "invoice_id": invoice_id}

    def post_invoice(self, invoice_id: int) -> Dict[str, Any]:
        """Posts (validates) a draft invoice. Requires human approval logic outside this client."""
        self.logger.info(f"Posting invoice {invoice_id}")
        
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Skipping posting of invoice {invoice_id}.")
            return {"status": "dry_run", "invoice_id": invoice_id}

        self.execute_kw('account.move', 'action_post', [invoice_id])
        return {"status": "success", "invoice_id": invoice_id}

    def record_payment(self, invoice_id: int, amount: float, journal_id: int) -> Dict[str, Any]:
        """Records a payment against an invoice."""
        self.logger.info(f"Recording payment of {amount} for invoice {invoice_id}")

        if self.dry_run:
            self.logger.info(f"[DRY RUN] Skipping payment recording.")
            return {"status": "dry_run", "invoice_id": invoice_id, "amount": amount}

        # Create payment
        payment_vals = {
            'amount': amount,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'journal_id': journal_id,
            'payment_method_line_id': 1, # Manual
        }
        payment_id = self.execute_kw('account.payment', 'create', payment_vals)
        self.execute_kw('account.payment', 'action_post', [payment_id])
        
        return {"status": "success", "payment_id": payment_id}

    def fetch_revenue_summary(self, date_from: str, date_to: str) -> Dict[str, Any]:
        """Fetches total revenue between two dates."""
        domain = [
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('invoice_date', '>=', date_from),
            ('invoice_date', '<=', date_to)
        ]
        invoices = self.execute_kw('account.move', 'search_read', domain, ['amount_total', 'currency_id'])
        total = sum(inv['amount_total'] for inv in invoices)
        return {"total_revenue": total, "count": len(invoices), "currency": "USD"}

    def fetch_overdue_invoices(self) -> List[Dict[str, Any]]:
        """Fetches invoices where payment state is not paid and due date has passed."""
        today = os.getenv("CURRENT_DATE", "2026-02-21")
        domain = [
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', '!=', 'paid'),
            ('invoice_date_due', '<', today)
        ]
        fields = ['name', 'partner_id', 'amount_total', 'amount_residual', 'invoice_date_due']
        return self.execute_kw('account.move', 'search_read', domain, fields)
