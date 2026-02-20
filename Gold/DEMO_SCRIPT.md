# 📺 AI Employee Gold Tier Demo Walkthrough Script

This script provides a step-by-step walkthrough of the **AI Employee Gold Tier** features, from perception to autonomous cross-domain reasoning and action.

---

## 🕒 Scenario
A client sends a WhatsApp message requesting an invoice, while the bank notifies of a late fee. The AI must correlate these events and handle both.

---

## 🚶 Step 1: Perception (The Trigger)
*Show the `AI_Employee_Vault/Needs_Action/` folder.*

1.  **WhatsApp Request**: A new file `WHATSAPP_ClientA_Invoice.md` arrives.
    - Content: *"Hey, can you send over the invoice for the last project? I need to pay it today."*
2.  **Bank Late Fee**: A new file `BANK_LateFee.md` arrives.
    - Content: *"Transaction Alert: Late Fee - Overdue Payment. Amount: $35.00"*

---

## 🚶 Step 2: Reasoning (The Brain)
*Run `python -m scripts.reasoning.reasoning_engine` (or show the orchestrator log).*

1.  **Intent Classification**: The engine classifies both intents as **finance** (invoice_request and late_fee_notice).
2.  **Cross-Domain Correlation**: The engine identifies a "Financial Health" cluster and generates a **Unified Plan**.
3.  **The Plan**: A new file `PLAN_YYYYMMDD_HHMMSS_cross_domain_recovery.md` appears in `AI_Employee_Vault/Plans/`.
    - **Step 1**: Generate invoice (Odoo).
    - **Step 2**: Request approval.
    - **Step 3**: Log late fee (Odoo).
    - **Step 4**: Update dashboard.
    - **Step 5**: Suggest proactive negotiation.

---

## 🚶 Step 3: Approval (Human-in-the-Loop)
*Open `AI_Employee_Vault/Pending_Approval/`.*

1.  **The Request**: A new file `APPROVAL_post_invoice_20260221.md` appears.
    - Content: Full YAML details of the Odoo invoice for Client A.
2.  **Human Action**: **Move** the file from `Pending_Approval/` to `Approved/`.

---

## 🚶 Step 4: Action (The Hands)
*Show the `logs/ai_employee.log` or orchestrator output.*

1.  **Odoo Integration**: The `OdooApprovalHandler` detects the approved file and calls the Odoo 19+ API (JSON-RPC) to post the invoice and log the late fee.
2.  **Audit Trail**: Open `AI_Employee_Vault/Logs/YYYY-MM-DD_audit.jsonl` to see the structured JSON log entry for the Odoo action (status: success).
3.  **Task Cleanup**: The plan and the approval files are moved to `AI_Employee_Vault/Done/`.

---

## 🚶 Step 5: Persistence (Ralph Wiggum)
*Run `python -m scripts.ralph.cli_wrapper "Analyze transactions" --completion-promise "DONE"`.*

1.  **Autonomous Loop**: Show how the AI iterates, checking its own previous output, until the task is fully completed or the promise is met.

---

## 🚶 Step 6: CEO Briefing (Advanced Analytics)
*Open `AI_Employee_Vault/Briefings/YYYY-MM-DD_Monday_Briefing.md`.*

1.  **Revenue Analytics**: Show the MTD revenue vs. target.
2.  **Subscription Audit**: Show the AI flagging **Notion** for inactivity (no login in 30 days).
3.  **Proactive Suggestion**: Show the suggestion to cancel unused subs to save $15/mo.

---

## 🚶 Step 7: Error Handling (Gold-Tier Safety)
*Simulate an error or show the `AI_Employee_Vault/Alerts/` folder.*

1.  **Quarantine**: Show a corrupted file in `AI_Employee_Vault/Quarantine/`.
2.  **Alert Report**: Open `FAILURE_REPORT_*.md` to see the diagnosis and recovery steps.
3.  **Queue**: Show `Failed_Actions_Queue.md` for a summary of all pending system issues.

---
*Built for the 2026 Personal AI Employee Hackathon.*
