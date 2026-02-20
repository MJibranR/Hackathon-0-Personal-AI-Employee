# scripts/init_vault.py
import os
import shutil
import json
from pathlib import Path

# Required Project Structure
DIRECTORIES = [
    "AI_Employee_Vault/Inbox",
    "AI_Employee_Vault/Needs_Action",
    "AI_Employee_Vault/Plans",
    "AI_Employee_Vault/Done",
    "AI_Employee_Vault/Logs/Archive",
    "AI_Employee_Vault/Pending_Approval",
    "AI_Employee_Vault/Approved",
    "AI_Employee_Vault/Rejected",
    "AI_Employee_Vault/Accounting/Invoices",
    "AI_Employee_Vault/Accounting/Payments",
    "AI_Employee_Vault/Briefings",
    "AI_Employee_Vault/In_Progress/Agent_Local",
    "AI_Employee_Vault/In_Progress/Agent_Cloud",
    "AI_Employee_Vault/Updates",
    "AI_Employee_Vault/Alerts",
    "AI_Employee_Vault/Quarantine",
    "logs/screenshots",
    "lockfiles"
]

def bootstrap():
    """Bootstraps the entire Gold Tier system in one click."""
    print("🚀 Initializing AI Employee (Gold Tier)...")
    
    # 1. Create Folder Structure
    for dir_path in DIRECTORIES:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"Created: {dir_path}")

    # 2. Check for .env
    env_file = Path(".env")
    if not env_file.exists():
        if Path(".env.example").exists():
            shutil.copy(".env.example", ".env")
            print("Created .env from example. Please edit it with your keys!")
        else:
            print("⚠️ Warning: .env.example not found.")

    # 3. Create initial Company Handbook
    handbook = Path("AI_Employee_Vault/Company_Handbook.md")
    if not handbook.exists():
        handbook.write_text("# 📖 Company Handbook\n\n- Be polite.\n- Require approval for payments > $500.\n- Local-first only.")

    print("
✅ Initialization Complete. You are ready to run!")
    print("👉 Next Step: Open AI_Employee_Vault in Obsidian.")

if __name__ == "__main__":
    bootstrap()
