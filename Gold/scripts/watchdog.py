# scripts/watchdog.py
import subprocess
import time
import os
import signal
import sys
# import psutil
from .audit_logger import logger
from datetime import datetime

class Watchdog:
    def __init__(self, check_interval=60):
        self.check_interval = check_interval
        self.processes = {}
        self.process_info = {
            "orchestrator": {"cmd": ["python", "-m", "scripts.orchestrator"], "restart": True},
            "gmail_watcher": {"cmd": ["python", "-m", "scripts.gmail_watcher"], "restart": True},
            "whatsapp_watcher": {"cmd": ["python", "-m", "scripts.whatsapp_watcher"], "restart": True},
            "finance_watcher": {"cmd": ["python", "-m", "scripts.finance_watcher"], "restart": True},
            "odoo_approval": {"cmd": ["python", "-m", "scripts.odoo_approval_handler"], "restart": True},
            "social_approval": {"cmd": ["python", "-m", "scripts.social_approval_handler"], "restart": True}
        }
    
    def start_process(self, name):
        try:
            cmd = self.process_info[name]["cmd"]
            logger.info(f"Starting process: {name} (Command: {' '.join(cmd)})")
            
            # Use subprocess.Popen for non-blocking execution
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
            self.processes[name] = proc
            logger.info(f"Started {name} with PID: {proc.pid}")
        except Exception as e:
            logger.error(f"Failed to start process {name}: {e}")

    def monitor(self):
        logger.info("Starting Watchdog Monitor...")
        # Start all defined processes initially
        for name in self.process_info:
            self.start_process(name)
            
        while True:
            for name, proc in list(self.processes.items()):
                # Check if process is still running
                if proc.poll() is not None:
                    # Process has terminated
                    exit_code = proc.returncode
                    stdout, stderr = proc.communicate()
                    
                    logger.warning(f"Process {name} exited with code {exit_code}")
                    if stdout: logger.info(f"{name} stdout: {stdout.decode()}")
                    if stderr: logger.error(f"{name} stderr: {stderr.decode()}")
                    
                    del self.processes[name]
                    
                    if self.process_info[name]["restart"]:
                        logger.info(f"Restarting {name}...")
                        self.start_process(name)
                    else:
                        logger.info(f"Not restarting {name} based on configuration.")
            
            time.sleep(self.check_interval)

    def stop_all(self):
        logger.info("Stopping all managed processes...")
        for name, proc in self.processes.items():
            if proc.poll() is None:
                logger.info(f"Terminating {name} (PID: {proc.pid})")
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning(f"Force killing {name} (PID: {proc.pid})")
                    proc.kill()
        sys.exit(0)

if __name__ == "__main__":
    watchdog = Watchdog()
    signal.signal(signal.SIGINT, lambda s, f: watchdog.stop_all())
    signal.signal(signal.SIGTERM, lambda s, f: watchdog.stop_all())
    
    try:
        watchdog.monitor()
    except KeyboardInterrupt:
        watchdog.stop_all()
