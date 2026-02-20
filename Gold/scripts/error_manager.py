import os
import time
import shutil
import functools
import logging
from pathlib import Path
from datetime import datetime
from typing import Callable, Any

VAULT_PATH = Path("AI_Employee_Vault")
QUARANTINE_DIR = VAULT_PATH / "Quarantine"
ALERTS_DIR = VAULT_PATH / "Alerts"
LOGS_DIR = VAULT_PATH / "Logs"
FAILED_QUEUE_FILE = ALERTS_DIR / "Failed_Actions_Queue.md"

# Configure logging for errors
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ErrorManager")

class ErrorManager:
    @staticmethod
    def is_auth_error(error: Exception) -> bool:
        """Determines if the error is related to authentication or permissions."""
        err_msg = str(error).lower()
        return any(term in err_msg for term in ["auth", "permission", "unauthorized", "login", "credentials", "401", "403"])

    @staticmethod
    def with_backoff(max_retries: int = 3, base_delay: float = 1.0, exceptions: tuple = (Exception,)):
        """
        Decorator for exponential backoff.
        """
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Banking safety check
                func_name_lower = func.__name__.lower()
                if any(term in func_name_lower for term in ["bank", "payment", "odoo", "invoice", "transfer"]):
                    logger.warning(f"Safety: Skipping auto-retry for banking-related function '{func.__name__}'")
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        ErrorManager.handle_failure(func.__name__, e, args, kwargs)
                        raise

                delay = base_delay
                for attempt in range(max_retries):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        if ErrorManager.is_auth_error(e):
                            logger.error(f"Critical Authentication Error in {func.__name__}: {e}")
                            ErrorManager.handle_critical(func.__name__, e)
                            raise e
                        
                        if attempt == max_retries - 1:
                            logger.error(f"Function {func.__name__} failed after {max_retries} attempts.")
                            ErrorManager.handle_failure(func.__name__, e, args, kwargs)
                            raise e
                        
                        logger.warning(f"Attempt {attempt+1} failed for {func.__name__}: {e}. Retrying in {delay}s...")
                        time.sleep(delay)
                        delay *= 2
            return wrapper
        return decorator

    @staticmethod
    def update_failure_queue(timestamp: str, func_name: str, error: str, report_link: str):
        """Appends a failure entry to the central queue file."""
        if not FAILED_QUEUE_FILE.exists():
            FAILED_QUEUE_FILE.write_text("# 📋 Failed Actions Queue\n\n| Timestamp | Function | Error | Status | Report Link |\n|-----------|----------|-------|--------|-------------|\n")
        
        entry = f"| {timestamp} | {func_name} | {error} | 🔴 Failed | [View Report](./{report_link}) |\n"
        with open(FAILED_QUEUE_FILE, "a", encoding="utf-8") as f:
            f.write(entry)

    @staticmethod
    def handle_failure(func_name: str, error: Exception, args: tuple = None, kwargs: dict = None):
        """
        Handles non-critical failures by logging and creating a failure report.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ts_filename = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"FAILURE_{func_name}_{ts_filename}.md"
        report_path = ALERTS_DIR / report_filename
        
        content = f"""---
type: failure_report
severity: medium
timestamp: {datetime.now().isoformat()}
function: {func_name}
---

# ❌ Task Failure: {func_name}

## Error Details
**Message:** `{str(error)}`

## Context
- **Arguments:** `{args}`
- **Keyword Args:** `{kwargs}`

## Recovery Steps
1. Check network connectivity.
2. Verify external API status.
3. Manually retry the task if critical.
"""
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        ErrorManager.update_failure_queue(timestamp, func_name, str(error), report_filename)
        logger.info(f"Created failure report: {report_path}")

    @staticmethod
    def handle_critical(func_name: str, error: Exception):
        """
        Handles critical errors (Auth/Permission) that require immediate human intervention.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        alert_path = ALERTS_DIR / f"CRITICAL_ALERT_{timestamp}.md"
        
        content = f"""---
type: critical_alert
severity: high
timestamp: {datetime.now().isoformat()}
---

# 🚨 CRITICAL SYSTEM ALERT

**Function:** `{func_name}`
**Error:** `AUTHENTICATION_FAILED`

## Details
The system encountered an authentication or permission error and has paused related operations.

**Log Message:** `{str(error)}`

## Required Action
- [ ] Update API keys in `.env`
- [ ] Re-authenticate manually
- [ ] Restart the AI Employee Watchdog
"""
        with open(alert_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.error(f"CRITICAL ALERT CREATED: {alert_path}")

    @staticmethod
    def quarantine_file(file_path: Path, reason: str):
        """
        Moves a corrupted or unprocessable file to the Quarantine folder.
        """
        if not file_path.exists():
            return

        QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)
        dest_path = QUARANTINE_DIR / file_path.name
        shutil.move(file_path, dest_path)
        
        # Create metadata report
        report_path = dest_path.with_suffix(".md.report")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"Quarantined on: {datetime.now().isoformat()}
Reason: {reason}
Original Path: {file_path}")
        
        logger.warning(f"File quarantined: {file_path.name}. Reason: {reason}")
