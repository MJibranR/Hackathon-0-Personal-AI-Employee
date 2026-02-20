import os
import time
import datetime
import glob
import sys
import logging
import shutil # Added for shutil.move
from logging.handlers import RotatingFileHandler

# Configure logging
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
log_file_path = os.path.join(LOG_DIR, 'ai_employee.log')
log_handler = RotatingFileHandler(log_file_path, maxBytes=1*1024*1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)


# Assume project root is the directory where this script is run from
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VAULT_PATH = os.path.join(PROJECT_ROOT, "vault")
INBOX_PATH = os.path.join(VAULT_PATH, "Inbox")
NEEDS_ACTION_PATH = os.path.join(VAULT_PATH, "Needs_Action")
DONE_PATH = os.path.join(VAULT_PATH, "Done")

# Use a file-based ledger to keep track of processed files
LEDGER_FILE = os.path.join(PROJECT_ROOT, "vault_watcher_ledger")

def get_processed_tasks():
    if not os.path.exists(LEDGER_FILE):
        return set()
    with open(LEDGER_FILE, 'r') as f:
        return set(line.strip() for line in f)

def add_to_processed_tasks(task_file):
    with open(LEDGER_FILE, 'a') as f:
        f.write(task_file + '\n')

def read_task_content(task_file_path):
    """Reads the content of a task file."""
    try:
        with open(task_file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading task file {task_file_path}: {e}")
        print(f"CRITICAL ERROR reading task file {task_file_path}: {e}") # Added print
        return None

def create_plan_file(original_task_content, original_task_filename):
    """
    Creates a structured plan file in the Needs_Action directory.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    plan_filename = f"Plan_{timestamp}_{original_task_filename.replace('.md', '')}.md" # Fixed unique filename
    plan_file_path = os.path.join(NEEDS_ACTION_PATH, plan_filename)

    plan_content = f"""Title: Task Plan

Original Task:
---
{original_task_content}
---

Objective:
- To analyze the user's request and create an actionable, step-by-step plan.

Step-by-Step Plan:
1. [ ] TBD by AI Processor

Priority: Medium
Requires Human Approval?: Yes
Suggested Output:
- TBD by AI Processor
"""

    try:
        os.makedirs(NEEDS_ACTION_PATH, exist_ok=True)
        with open(plan_file_path, 'w', encoding='utf-8') as f:
            f.write(plan_content)
        logger.info(f"Created plan file: {plan_file_path}")
        print(f"Created plan file: {plan_file_path}")
        return True
    except Exception as e:
        logger.error(f"Error creating plan file {plan_file_path}: {e}")
        print(f"CRITICAL ERROR creating plan file {plan_file_path}: {e}") # Added print
        return False

def move_to_done(task_file_path):
    """Moves a file to the DONE directory."""
    if not os.path.exists(task_file_path):
        logger.warning(f"Attempted to move non-existent file: {task_file_path}")
        print(f"Warning: Attempted to move non-existent file: {task_file_path}") # Added print
        return
    try:
        done_file_path = os.path.join(DONE_PATH, os.path.basename(task_file_path))
        os.makedirs(DONE_PATH, exist_ok=True) # Ensure DONE_PATH exists
        shutil.move(task_file_path, done_file_path) # Use shutil.move for robustness
        logger.info(f"Moved task {os.path.basename(task_file_path)} to Done.")
        print(f"Moved task {os.path.basename(task_file_path)} to Done.") # Added print
    except Exception as e:
        logger.error(f"Error moving file {task_file_path} to Done: {e}")
        print(f"CRITICAL ERROR moving file {task_file_path} to Done: {e}") # Added print


def scan_inbox_and_process():
    """Scans the Inbox for new tasks and triggers planning."""
    processed_tasks = get_processed_tasks()
    logger.info(f"Scanning inbox: {INBOX_PATH}")

    new_tasks_found = False
    for task_file in glob.glob(os.path.join(INBOX_PATH, "*.md")):
        # Only process files that haven't been recorded as processed
        task_filename_only = os.path.basename(task_file)
        if task_filename_only not in processed_tasks: # Check against basename only
            logger.info(f"New task found: {task_file}")
            new_tasks_found = True
            
            task_content = read_task_content(task_file)
            if task_content:
                if create_plan_file(task_content, os.path.basename(task_file)):
                    add_to_processed_tasks(task_filename_only) # Add basename to ledger
                    move_to_done(task_file)
                else:
                    logger.error(f"Failed to create plan for {task_file}")
            else:
                logger.error(f"Could not read content for {task_file}, skipping.")

    if not new_tasks_found:
        logger.info("No new tasks found.")

def main():
    """Main loop for the AI Employee planner."""
    os.makedirs(INBOX_PATH, exist_ok=True)
    os.makedirs(NEEDS_ACTION_PATH, exist_ok=True)
    os.makedirs(DONE_PATH, exist_ok=True)
    
    while True:
        scan_inbox_and_process()
        logger.info(f"Waiting for {30} seconds before next scan...")
        time.sleep(30)

if __name__ == "__main__":
    main()
