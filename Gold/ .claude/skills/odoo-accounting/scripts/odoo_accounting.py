import json
import os
import requests
import sys

# Odoo 19+ External JSON-RPC API logic (simulated)
# https://www.odoo.com/documentation/19.0/developer/reference/external_api.html
def call_odoo(url, service, method, *args):
    """Call Odoo API using JSON-RPC."""
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": service,
            "method": method,
            "args": args
        },
        "id": 1
    }
    
    # In a real environment, we'd make a POST request.
    # response = requests.post(f"{url}/jsonrpc", json=payload)
    # return response.json()['result']
    
    # For hackathon, we simulate a successful invoice creation or payment log.
    print(f"Odoo call: service={service}, method={method}, args={args}")
    return {"status": "success", "id": 1234}

def create_invoice(client_id, amount):
    # Simulated invoice creation
    return call_odoo("http://localhost:8069", "object", "execute_kw", "db", 1, "password", "account.move", "create", {
        "partner_id": client_id,
        "amount_total": amount,
        "type": "out_invoice"
    })

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python odoo_accounting.py <client_id> <amount>")
        sys.exit(1)
    
    client_id = int(sys.argv[1])
    amount = float(sys.argv[2])
    print(create_invoice(client_id, amount))
