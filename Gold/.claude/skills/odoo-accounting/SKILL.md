# Odoo Accounting Integration Skill

## Objective
Enable Claude to interact with Odoo Community (self-hosted, local) via JSON-RPC APIs for business accounting and financial reporting.

## Key Capabilities
- Create and post invoices.
- Log payments and reconcile accounts.
- Generate financial summaries (Profit & Loss, Balance Sheet).
- Audit recurring subscriptions.

## Usage
- Trigger: Claude detects an invoice request or a payment from /Inbox.
- Action: Claude creates a plan, drafts the invoice in Odoo, and requests human approval.
- Final: Upon approval, Claude posts the invoice in Odoo.

## Security
- Odoo credentials must be stored in `@.env`.
- **NEVER** post a payment or invoice over $500 without manual human approval.
- All actions must be logged in `logs/actions.log`.

## Implementation Details
- JSON-RPC API calls to local Odoo 19+ instance.
- Scripts in `/scripts/odoo_accounting.py`.
