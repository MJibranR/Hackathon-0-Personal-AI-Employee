# scripts/audit_logger.py
import logging
import json
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

LOG_DIR = Path("AI_Employee_Vault/Logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

class AuditLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))
        
        # Create a file handler for JSON logs
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = LOG_DIR / f"{today}_audit.jsonl"
        
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        # Also log to console for debugging
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(console_handler)

    def log_action(self, action_type, actor, target, details=None, status="success"):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "actor": actor,
            "target": str(target),
            "status": status,
            "details": details or {}
        }
        self.logger.info(json.dumps(entry))

    def info(self, message):
        self.logger.info(json.dumps({"level": "INFO", "message": message, "timestamp": datetime.now().isoformat()}))

    def error(self, message, exc_info=None):
        self.logger.error(json.dumps({"level": "ERROR", "message": message, "timestamp": datetime.now().isoformat()}), exc_info=exc_info)

# Singleton instance
logger = AuditLogger("AI_Employee")
