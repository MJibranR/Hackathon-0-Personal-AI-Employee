# mcp/social/social_mcp.py
import sys
import json
import os
import argparse
from pathlib import Path
from datetime import datetime
from scripts.meta_client import MetaClient
from scripts.x_client import XClient

VAULT_PATH = Path("AI_Employee_Vault")
PENDING_APPROVAL = VAULT_PATH / "Pending_Approval"
ACCOUNTING = VAULT_PATH / "Accounting"

class SocialMCPServer:
    def __init__(self):
        self.meta_client = MetaClient()
        self.x_client = XClient()

    def handle_tool_call(self, name: str, params: dict):
        """MCP Tool Handler for Social Media."""
        try:
            if name == "draft_facebook_post":
                return self._request_approval("post_facebook", params)
            
            elif name == "draft_instagram_post":
                return self._request_approval("post_instagram", params)
            
            elif name == "draft_twitter_post":
                return self._request_approval("post_twitter", params)
            
            elif name == "fetch_social_engagement":
                meta_stats = self.meta_client.fetch_engagement()
                x_stats = self.x_client.fetch_engagement()
                all_stats = {**meta_stats, **x_stats}
                self._log_to_accounting(all_stats)
                return all_stats

            elif name == "generate_social_summary":
                stats = {**self.meta_client.fetch_engagement(), **self.x_client.fetch_engagement()}
                summary = self._create_summary_markdown(stats)
                return {"status": "success", "summary": summary}
            
            else:
                return {"error": f"Unknown tool: {name}"}
        except Exception as e:
            return {"error": str(e)}

    def _request_approval(self, action: str, params: dict):
        """Creates an approval request for a social media post."""
        PENDING_APPROVAL.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"APPROVAL_{action}_{timestamp}.md"
        file_path = PENDING_APPROVAL / filename
        
        content = f"""---
action: {action}
details: {json.dumps(params)}
status: pending
---

# 📝 Approval Required: {action.replace('_', ' ').capitalize()}

**Platform:** {action.replace('post_', '').capitalize()}
**Content:**
{params.get('content', params.get('message', params.get('text', 'No content provided.')))}

## Instructions
- To **APPROVE**: Move this file to `AI_Employee_Vault/Approved/`.
- To **REJECT**: Move this file to `AI_Employee_Vault/Rejected/`.
"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return {"status": "approval_required", "file": str(file_path), "message": "Social media post requires human approval."}

    def _log_to_accounting(self, stats: dict):
        """Logs social media reach/engagement to the Accounting/Engagement_Log.md."""
        ACCOUNTING.mkdir(parents=True, exist_ok=True)
        log_file = ACCOUNTING / "Social_Engagement_Audit.md"
        
        today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not log_file.exists():
            with open(log_file, "w", encoding="utf-8") as f:
                f.write("# Social Media Engagement Audit

| Timestamp | Platform | Reach | Likes/Engagement |
|---|---|---|---|
")
        
        with open(log_file, "a", encoding="utf-8") as f:
            for platform, data in stats.items():
                reach = data.get("reach", data.get("impressions", "n/a"))
                likes = data.get("likes", "n/a")
                f.write(f"| {today} | {platform.capitalize()} | {reach} | {likes} |
")

    def _create_summary_markdown(self, stats: dict) -> str:
        """Generates a markdown summary of recent social performance."""
        summary = f"# Weekly Social Media Engagement Summary

Generated: {datetime.now().strftime('%Y-%m-%d')}

"
        for platform, data in stats.items():
            summary += f"### {platform.capitalize()}
"
            for k, v in data.items():
                summary += f"- **{k.replace('_', ' ').capitalize()}**: {v}
"
            summary += "
"
        return summary

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("tool_name", help="Tool to call")
    parser.add_argument("params", help="JSON string of params")
    args = parser.parse_args()

    server = SocialMCPServer()
    params = json.loads(args.params)
    result = server.handle_tool_call(args.tool_name, params)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
