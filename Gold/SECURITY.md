# 🛡️ AI Employee Security & Privacy (Gold Tier)

Security is non-negotiable for an autonomous system handling banking, email, and social communications.

## 1. Credential Management
Credentials must **NEVER** be stored in plain text or within the Obsidian vault.
- **Environment Variables**: Sensitive keys (API tokens, Odoo passwords, WhatsApp session paths) are stored in a local `.env` file.
- **Git Safety**: The `.env` file is explicitly added to `.gitignore`.
- **Sandbox Accounts**: Development should always use test accounts for Gmail, WhatsApp, and banking.

## 2. Permission Boundaries
A robust security model defines what the AI can do autonomously and what requires a human.

| Action Category | Auto-Approve Threshold | Always Require Approval |
|-----------------|-------------------------|-------------------------|
| **Email**       | Triage, drafts, known   | New contacts, bulk sends|
| **Odoo/Finance**| Read-only summaries     | **ALL** payments, invoices|
| **Social Media**| Fetch engagement stats  | **ALL** posts, replies, DMs|
| **File System** | Create, read, move      | Delete, external moves  |

## 3. Human-in-the-Loop (HITL) Safety
The AI Employee is designed with a **Hard Approval Gate**.
- **The Approval File**: The reasoning engine writes a structured Markdown file with a YAML metadata payload to `/Pending_Approval`.
- **The Human Gate**: The orchestrator **STOPS** until the human moves this file to `/Approved`.
- **The Audit Trail**: Every approval, rejection, and final action is logged with the `approved_by` (Human) actor tag in the audit trail.

## 4. Error Recovery & Quarantine
- **Banking Safety**: The system **NEVER** auto-retries a banking or payment action. All financial errors generate an immediate `FAILURE_REPORT.md` and stop.
- **Quarantine**: Any corrupted or suspicious file is moved to `/Quarantine/` and isolated with a metadata report.
- **Auth Detection**: Critical authentication or permission errors trigger a system-wide `CRITICAL_ALERT.md` and pause related services.

## 5. Enterprise Audit Logging
- **Structured Schema**: Every action (action_type, actor, target, parameters, approval_status, result) is logged in JSONL format.
- **Immutability**: Daily logs are archived and monitored by a built-in validator.
- **90-Day Retention**: Automated rotation ensures a 90-day history for all AI actions.

## 6. Privacy: Local-First Principle
- **Data Residency**: All task content, plans, and long-term memory stay in your local Obsidian vault.
- **Minimal Data Exfiltration**: Only the minimum necessary data is sent to external APIs (Claude/Gmail/Odoo).
- **No Cloud Sync for Secrets**: The `.env` file and session tokens must never be synced to external cloud services.

---
*Built for the 2026 Personal AI Employee Hackathon.*
