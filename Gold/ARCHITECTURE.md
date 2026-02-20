# 🏗️ AI Employee Architecture (Gold Tier)

The system follows a modular **Perception → Memory → Reasoning → Approval → Action** pipeline.

## 1. Perception Layer (Watchers)
Lightweight Python processes that poll external sources for triggers.
- **GmailWatcher**: Monitors unread emails using the Gmail API.
- **WhatsAppWatcher**: Uses Playwright for browser-based session monitoring of WhatsApp Web.
- **FinanceWatcher**: Connects to banking APIs (simulated) and Odoo ledgers.
- **FileSystemWatcher**: Monitors local "drops" into the vault.

## 2. Long-Term Memory & GUI (Obsidian Vault)
A local Markdown-based filesystem serving as the AI's state and history.
- **State Folders**: `/Needs_Action`, `/In_Progress`, `/Done`.
- **Reasoning Folders**: `/Plans`, `/Updates`.
- **Governance Folders**: `/Pending_Approval`, `/Approved`, `/Rejected`.
- **Records**: `/Accounting`, `/Logs`, `/Briefings`.

## 3. Reasoning Layer (Claude Code)
The logic hub that processes tasks using the **Intent Classifier** and **Multi-Step Planner**.
- **Cross-Domain Correlation**: Identifies relationships between different triggers (e.g., an invoice request on WhatsApp vs. a bank late fee).
- **Plan Generation**: Creates structured markdown plans in `/Plans` with defined steps and tools.
- **Ralph Wiggum Loop**: An autonomous persistence hook that forces Claude to re-evaluate and iterate until the `completion_promise` is met or the `target_file` reaches `/Done`.

## 4. Approval Layer (Human-in-the-Loop)
A hard safety boundary for sensitive actions.
- **Mechanism**: The AI writes a `APPROVAL_*.md` file with a YAML payload in `/Pending_Approval`.
- **Intervention**: The human moves the file to `/Approved` to greenlight the action.
- **Odoo/Social**: All payments, invoice postings, and social posts MUST pass through this layer.

## 5. Action Layer (MCP Servers)
Claude's "Hands" for interacting with the outside world via the **Model Context Protocol**.
- **Odoo MCP**: JSON-RPC client for Odoo 19+ Community Edition.
- **Social MCP**: Meta Graph API and X API v2 clients for posting and auditing.
- **FileSystem MCP**: Direct vault manipulation tools.

## 6. Orchestration Layer (Nervous System)
The `scripts/orchestrator.py` manages all system health.
- **Process Supervisor**: Monitors the health of all watchers and restarts crashed processes.
- **Scheduler**: Triggers the `Weekly Business Audit` every Monday morning.
- **Execution Loop**: Periodically triggers the reasoning cycle and executes approved actions.

## 7. Audit & Analytics (Enterprise Logs)
Every action is recorded in a structured JSON schema.
- **Retention**: 90-day automated log rotation and archiving.
- **Validation**: Built-in log validator ensures the audit trail is untampered.
- **CEO Briefing**: Aggregates all logs and accounting data into a weekly ROI summary.

---
*Built for the 2026 Personal AI Employee Hackathon.*
