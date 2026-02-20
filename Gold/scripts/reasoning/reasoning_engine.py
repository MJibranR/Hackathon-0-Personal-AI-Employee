# scripts/reasoning/reasoning_engine.py
import logging
import time
import os
import shutil
from pathlib import Path
from .planner import Planner

VAULT_PATH = Path("AI_Employee_Vault")
NEEDS_ACTION = VAULT_PATH / "Needs_Action"
IN_PROGRESS = VAULT_PATH / "In_Progress"

class ReasoningEngine:
    """
    Main entry point for the cross-domain reasoning system.
    Scans `Needs_Action`, correlates events, and triggers planning.
    """
    
    def __init__(self):
        self.planner = Planner()
        self.logger = logging.getLogger("ReasoningEngine")
        
        # Ensure directories exist
        NEEDS_ACTION.mkdir(parents=True, exist_ok=True)
        IN_PROGRESS.mkdir(parents=True, exist_ok=True)

    def process(self):
        """
        Main reasoning cycle.
        """
        self.logger.info("Scanning for new tasks...")
        files = list(NEEDS_ACTION.glob("*.md"))
        
        if not files:
            self.logger.debug("No new tasks found.")
            return

        self.logger.info(f"Found {len(files)} new tasks.")
        
        # 1. Analyze and Plan (Cross-Domain)
        plans = self.planner.scan_and_plan(files)
        
        if plans:
            self.logger.info(f"Generated {len(plans)} plans.")
            
            # 2. Move processed files to In_Progress to prevent re-scanning
            # In a real system, we'd only move files that were *part of a plan*.
            # Here, we assume the planner consumed them.
            for plan in plans:
                for item in plan['context']:
                    src_path = Path(item['source_file'])
                    if src_path.exists():
                        dest_path = IN_PROGRESS / src_path.name
                        shutil.move(src_path, dest_path)
                        self.logger.info(f"Moved {src_path.name} to In_Progress")
        else:
            self.logger.info("No actionable plans generated.")

    def run(self):
        self.logger.info("Starting Reasoning Engine Loop...")
        while True:
            try:
                self.process()
            except Exception as e:
                self.logger.error(f"Reasoning Engine Error: {e}", exc_info=True)
            
            time.sleep(10) # Poll every 10 seconds

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    engine = ReasoningEngine()
    engine.run()
