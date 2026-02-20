import os
import datetime
import glob
import logging
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

# Project paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VAULT_PATH = os.path.join(PROJECT_ROOT, "vault")
INBOX_PATH = os.path.join(VAULT_PATH, "Inbox")
NEEDS_ACTION_PATH = os.path.join(VAULT_PATH, "Needs_Action")
DONE_PATH = os.path.join(VAULT_PATH, "Done")

# Ledger to track processed files
LEDGER_FILE = os.path.join(PROJECT_ROOT, "processed_tasks_ledger.txt")

def get_processed_tasks():
    if not os.path.exists(LEDGER_FILE):
        return set()
    with open(LEDGER_FILE, 'r') as f:
        return set(line.strip() for line in f)

def add_to_processed_tasks(task_file):
    with open(LEDGER_FILE, 'a') as f:
        f.write(os.path.basename(task_file) + '\n')

def read_task_content(task_file_path):
    try:
        with open(task_file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading task file {task_file_path}: {e}")
        return None

def create_plan_file(original_task_content, original_task_filename):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    plan_filename = f"Plan_{timestamp}_{original_task_filename.replace('.md', '')}.md"
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
        return False

def move_to_done(task_file_path):
    try:
        done_file_path = os.path.join(DONE_PATH, os.path.basename(task_file_path))
        os.makedirs(DONE_PATH, exist_ok=True)
        os.rename(task_file_path, done_file_path)
        logger.info(f"Moved task {os.path.basename(task_file_path)} to Done.")
    except Exception as e:
        logger.error(f"Error moving file {task_file_path} to Done: {e}")

def run_planner_once():
    """Scans the Inbox for new tasks and triggers planning for each."""
    logger.info("Starting AI Employee single run...")
    processed_tasks = get_processed_tasks()
    
    inbox_files = glob.glob(os.path.join(INBOX_PATH, "*.md"))
    if not inbox_files:
        logger.info("No tasks found in Inbox.")
        print("No new tasks found in Inbox.")
        return

    for task_file in inbox_files:
        task_filename = os.path.basename(task_file)
        if task_filename not in processed_tasks:
            logger.info(f"New task found: {task_filename}")
            print(f"Processing new task: {task_filename}")
            
            task_content = read_task_content(task_file)
            if task_content:
                if create_plan_file(task_content, task_filename):
                    add_to_processed_tasks(task_filename)
                    # We move the original file to Done to prevent re-processing
                    move_to_done(task_file) 
                else:
                    logger.error(f"Failed to create plan for {task_filename}")
            else:
                logger.error(f"Could not read content for {task_filename}, skipping.")
        
    logger.info("AI Employee single run finished.")
    print("AI Employee run finished.")

if __name__ == "__main__":
    run_planner_once()
