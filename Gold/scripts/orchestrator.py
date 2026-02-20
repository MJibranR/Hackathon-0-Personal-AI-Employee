# scripts/orchestrator.py
import os
import sys
import time
import logging
import subprocess
import schedule
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Import Core Systems
from scripts.reasoning.reasoning_engine import ReasoningEngine
from scripts.odoo_approval_handler import OdooApprovalHandler
from scripts.social_approval_handler import SocialApprovalHandler
from scripts.ceo_briefing import CEOBriefingGenerator
from scripts.utils.audit_logger import audit_logger
from scripts.error_manager import ErrorManager

# Load Environment
load_dotenv()
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Setup Logging
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("AI_Employee_Vault/Logs/orchestrator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Orchestrator")

class Orchestrator:
    """
    The Central Nervous System of the AI Employee.
    - Manages Subprocesses (Watchers)
    - Triggers Reasoning (Brain)
    - Handles Approvals (Hands)
    - schedules Audits (conscience)
    """

    def __init__(self):
        self.running = True
        self.watchers = {}
        self.watcher_scripts = {
            "gmail": ["python", "-m", "scripts.gmail_watcher"],
            "whatsapp": ["python", "-m", "scripts.whatsapp_watcher"],
            "finance": ["python", "-m", "scripts.finance_watcher"]
        }
        
        # Initialize Subsystems
        self.reasoning = ReasoningEngine()
        self.odoo_handler = OdooApprovalHandler()
        self.social_handler = SocialApprovalHandler()
        self.briefing_generator = CEOBriefingGenerator()
        
        # Scheduler
        schedule.every().monday.at("08:00").do(self.run_weekly_audit)
        schedule.every(10).seconds.do(self.health_check)

    def start_watchers(self):
        """Starts all perception agents (watchers) as subprocesses."""
        logger.info("Starting Perception Layer (Watchers)...")
        for name, cmd in self.watcher_scripts.items():
            self._start_process(name, cmd)

    def _start_process(self, name, cmd):
        try:
            # Use separate process groups
            proc = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            self.watchers[name] = proc
            logger.info(f"Started {name} (PID: {proc.pid})")
            audit_logger.log("system_start", name, {"pid": proc.pid}, result="success")
        except Exception as e:
            logger.error(f"Failed to start {name}: {e}")
            ErrorManager.handle_failure(f"start_{name}", e)

    def health_check(self):
        """Monitors watcher processes and restarts them if they fail."""
        for name, proc in list(self.watchers.items()):
            if proc.poll() is not None:
                # Process has died
                stdout, stderr = proc.communicate()
                logger.warning(f"Watcher died: {name} (Exit Code: {proc.returncode})")
                if stderr:
                    logger.error(f"{name} Error Output: {stderr}")
                
                # Log failure
                audit_logger.log("process_crash", name, {"exit_code": proc.returncode}, result="failure")
                
                # Restart
                logger.info(f"Restarting {name}...")
                self._start_process(name, self.watcher_scripts[name])

    @ErrorManager.with_backoff(max_retries=3)
    def run_reasoning_cycle(self):
        """Triggers the Reasoning Engine to process Needs_Action -> Plans."""
        try:
            self.reasoning.process()
        except Exception as e:
            logger.error(f"Reasoning Cycle Failed: {e}")
            raise e

    def run_approval_workflows(self):
        """Scans for approved tasks and executes them (MCP Layer)."""
        # Odoo (Accounting)
        try:
            self.odoo_handler.scan_approved()
        except Exception as e:
            logger.error(f"Odoo Handler Failed: {e}")
            ErrorManager.handle_failure("odoo_approval", e)

        # Social Media
        try:
            self.social_handler.scan_approved()
        except Exception as e:
            logger.error(f"Social Handler Failed: {e}")
            ErrorManager.handle_failure("social_approval", e)

    def run_weekly_audit(self):
        """Generates the CEO Briefing."""
        logger.info("Running Weekly CEO Audit...")
        try:
            report_path = self.briefing_generator.generate_report()
            audit_logger.log("generate_briefing", "system", {"path": str(report_path)}, result="success")
            logger.info(f"CEO Briefing generated: {report_path}")
        except Exception as e:
            logger.error(f"Weekly Audit Failed: {e}")
            ErrorManager.handle_failure("weekly_audit", e)

    def run(self):
        """Main Orchestration Loop."""
        logger.info(f"Orchestrator Started (DRY_RUN={DRY_RUN})")
        
        self.start_watchers()
        
        while self.running:
            try:
                # 1. Perception Health Check
                schedule.run_pending()
                
                # 2. Reasoning (Brain)
                self.run_reasoning_cycle()
                
                # 3. Action (Hands)
                self.run_approval_workflows()
                
                # Pace the loop
                time.sleep(5)
                
            except KeyboardInterrupt:
                logger.info("Stopping Orchestrator...")
                self.stop()
            except Exception as e:
                logger.critical(f"Unhandled Orchestrator Exception: {e}", exc_info=True)
                time.sleep(10) # Prevent tight loop on critical fail

    def stop(self):
        """Graceful Shutdown."""
        self.running = False
        for name, proc in self.watchers.items():
            if proc.poll() is None:
                logger.info(f"Terminating {name}...")
                proc.terminate()
        sys.exit(0)

if __name__ == "__main__":
    orchestrator = Orchestrator()
    orchestrator.run()
