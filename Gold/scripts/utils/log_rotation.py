import os
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import json

VAULT_PATH = Path("AI_Employee_Vault")
LOGS_DIR = VAULT_PATH / "Logs"
ARCHIVE_DIR = LOGS_DIR / "Archive"
BRIEFINGS_DIR = VAULT_PATH / "Briefings"

class LogRotation:
    """
    Handles daily rotation, 90-day retention, and weekly summaries.
    """
    
    def __init__(self, retention_days: int = 90):
        self.retention_days = retention_days
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    def rotate_logs(self):
        """
        Moves yesterday's log to Archive/ and deletes files older than retention_days.
        """
        print("Starting Log Rotation (90-day retention policy)...")
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # 1. Archive yesterday's completed logs
        for file_path in LOGS_DIR.glob("*.jsonl"):
            if yesterday in file_path.name:
                dest_path = ARCHIVE_DIR / file_path.name
                shutil.move(file_path, dest_path)
                print(f"Archived: {file_path.name} -> Archive/")

        # 2. Enforce Retention Policy
        for file_path in ARCHIVE_DIR.glob("*.jsonl"):
            # Extract date from YYYY-MM-DD_audit.jsonl
            try:
                date_str = file_path.name.split('_')[0]
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                if file_date < cutoff:
                    print(f"Deleting expired log (>{self.retention_days} days): {file_path.name}")
                    file_path.unlink()
            except (ValueError, IndexError):
                continue

    def generate_weekly_summary(self):
        """
        Processes the last 7 days of logs and generates a markdown summary.
        """
        print("Generating Weekly Audit Summary...")
        summary = {
            "period": f"{(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}",
            "total_actions": 0,
            "actions_by_type": {},
            "failures": 0,
            "approvals": 0
        }
        
        # Scan Archive for the last 7 days
        for i in range(1, 8):
            day_str = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            log_path = ARCHIVE_DIR / f"{day_str}_audit.jsonl"
            
            if not log_path.exists():
                # Check current Logs dir as well in case rotation hasn't run
                log_path = LOGS_DIR / f"{day_str}_audit.jsonl"

            if log_path.exists():
                with open(log_path, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            entry = json.loads(line)
                            summary["total_actions"] += 1
                            action_type = entry.get("action_type", "unknown")
                            summary["actions_by_type"][action_type] = summary["actions_by_type"].get(action_type, 0) + 1
                            
                            if entry.get("result") == "failure":
                                summary["failures"] += 1
                            
                            if entry.get("approval_status") == "approved":
                                summary["approvals"] += 1
                        except json.JSONDecodeError:
                            continue

        # Write to Briefings folder
        report_path = BRIEFINGS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}_Weekly_Audit_Summary.md"
        BRIEFINGS_DIR.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# Weekly System Audit Summary

")
            f.write(f"**Period:** {summary['period']}
")
            f.write(f"**Total Actions Executed:** {summary['total_actions']}
")
            f.write(f"**Total Approvals:** {summary['approvals']}
")
            f.write(f"**Failures Detected:** {summary['failures']}

")
            
            f.write("## 📊 Action Distribution
")
            for a_type, count in summary["actions_by_type"].items():
                f.write(f"- **{a_type.replace('_', ' ').capitalize()}**: {count}
")
            
            f.write("
---
*Verified by Enterprise Audit Engine v1.0*")
            
        print(f"Weekly Summary Exported: {report_path}")

if __name__ == "__main__":
    rotation = LogRotation()
    rotation.rotate_logs()
    rotation.generate_weekly_summary()
