import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

VAULT_PATH = Path("AI_Employee_Vault")
LOGS_DIR = VAULT_PATH / "Logs"

class AuditLogger:
    """
    Enterprise-grade structured audit logger.
    Ensures all AI actions are recorded in a consistent, verifiable format.
    """
    
    def __init__(self, agent_id: str = "AI_Employee_01"):
        self.agent_id = agent_id
        LOGS_DIR.mkdir(parents=True, exist_ok=True)

    def _get_log_file(self) -> Path:
        """Returns the path to today's log file."""
        today = datetime.now().strftime("%Y-%m-%d")
        return LOGS_DIR / f"{today}_audit.jsonl"

    def log(
        self,
        action_type: str,
        target: str,
        parameters: Dict[str, Any],
        result: str = "success",
        actor: Optional[str] = None,
        approval_status: str = "n/a",
        approved_by: str = "n/a"
    ):
        """
        Records a single audit entry.
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "actor": actor or self.agent_id,
            "target": target,
            "parameters": parameters,
            "approval_status": approval_status,
            "approved_by": approved_by,
            "result": result
        }
        
        log_file = self._get_log_file()
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            # Fallback to standard logging if file write fails
            import logging
            logging.error(f"Failed to write to audit log: {e}")

    def validate_log(self, log_path: Path) -> Dict[str, Any]:
        """
        Validates the integrity and schema of a log file.
        """
        stats = {"total_entries": 0, "errors": 0, "invalid_schema": 0}
        required_fields = {
            "timestamp", "action_type", "actor", "target", 
            "parameters", "approval_status", "approved_by", "result"
        }
        
        if not log_path.exists():
            return {"error": "File not found"}

        with open(log_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                stats["total_entries"] += 1
                try:
                    data = json.loads(line)
                    if not required_fields.issubset(data.keys()):
                        stats["invalid_schema"] += 1
                except json.JSONDecodeError:
                    stats["errors"] += 1
        
        return stats

# Global singleton for easy import
audit_logger = AuditLogger()
