# scripts/social_approval_handler.py
import os
import time
import json
import re
import shutil
from pathlib import Path
from .utils.audit_logger import audit_logger
from mcp.social.scripts.meta_client import MetaClient
from mcp.social.scripts.x_client import XClient

VAULT_PATH = Path("AI_Employee_Vault")
APPROVED = VAULT_PATH / "Approved"
DONE = VAULT_PATH / "Done"
ACCOUNTING = VAULT_PATH / "Accounting"

import yaml

class SocialApprovalHandler:
    def __init__(self):
        self.meta_client = MetaClient()
        self.x_client = XClient()
        self.audit = audit_logger

    def scan_approved(self):
        """Processes approved social media posts."""
        files = list(APPROVED.glob("APPROVAL_post_*.md"))
        for file_path in files:
            print(f"Processing approved social post: {file_path.name}")
            
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Extract action and details from YAML metadata
            match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
            if not match:
                continue
            
            try:
                metadata = yaml.safe_load(match.group(1))
                action = metadata.get('action')
                details = metadata.get('details')
                
                if isinstance(details, str):
                    details = json.loads(details)
                
                if not details:
                    details = {}
            except json.JSONDecodeError:
                continue

            result = {}
            if action == "post_facebook":
                result = self.meta_client.post_to_facebook(details.get("content", ""))
            elif action == "post_instagram":
                result = self.meta_client.post_to_instagram(details.get("image_url", ""), details.get("content", ""))
            elif action == "post_twitter":
                result = self.x_client.post_tweet(details.get("content", ""))

            # Audit and Move to Done
            self.audit.log(
                action_type=action,
                target=action.replace("post_", ""),
                parameters=details,
                result="success" if result.get("status") in ["success", "dry_run"] else "failure",
                approval_status="approved",
                approved_by="human"
            )
            
            shutil.move(file_path, DONE / file_path.name)
            print(f"Social post {action} completed for {file_path.name}")

    def run(self, interval=30):
        print("Social Approval Handler started.")
        while True:
            try:
                self.scan_approved()
            except Exception as e:
                print(f"Error in social approval scanner: {e}")
            time.sleep(interval)

if __name__ == "__main__":
    handler = SocialApprovalHandler()
    handler.run()
