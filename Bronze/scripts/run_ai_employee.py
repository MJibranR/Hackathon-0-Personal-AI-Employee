import sys
import os
import fcntl # For file locking on Unix-like systems
import msvcrt # For file locking on Windows

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import argparse
import time
import shutil
import logging
import re
from logging.handlers import RotatingFileHandler

# Import skill modules
from skills.gmail_send import send_gmail
from skills.linkedin_post import post_to_linkedin
from skills.vault_file_manager import create_note, update_note, move_note

# Configure logging
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
log_file_path = os.path.join(LOG_DIR, 'ai_employee.log')
# Set up RotatingFileHandler
log_handler = RotatingFileHandler(log_file_path, maxBytes=1*1024*1024, backupCount=5) # 1MB per file, keep 5 backups
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

# Define the directories for AI Employee Vault
AI_INBOX_DIR = "AI_Employee_Vault/Inbox/"
AI_NEEDS_ACTION_DIR = "AI_Employee_Vault/Needs_Action/"
AI_DONE_DIR = "AI_Employee_Vault/Done/"
AI_NEEDS_APPROVAL_DIR = "AI_Employee_Vault/Needs_Approval/"

# Define Lock file
LOCK_FILE_DIR = "lockfiles"
LOCK_FILE_NAME = "ai_employee.lock"
LOCK_FILE_PATH = os.path.join(LOCK_FILE_DIR, LOCK_FILE_NAME)

# Ensure the output directories exist
os.makedirs(AI_INBOX_DIR, exist_ok=True)
os.makedirs(AI_NEEDS_ACTION_DIR, exist_ok=True)
os.makedirs(AI_DONE_DIR, exist_ok=True)
os.makedirs(AI_NEEDS_APPROVAL_DIR, exist_ok=True)
os.makedirs(LOCK_FILE_DIR, exist_ok=True) # Ensure lockfiles directory exists

def acquire_lock():
    """Attempts to acquire a file lock. Returns True on success, False otherwise."""
    try:
        if os.name == 'nt': # Windows
            lock_fd = os.open(LOCK_FILE_PATH, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            msvcrt.locking(lock_fd, msvcrt.LK_NBLCK, 1)
            return True
        else: # Unix-like
            lock_fd = os.open(LOCK_FILE_PATH, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
    except (OSError, IOError):
        logger.warning(f"Failed to acquire lock: {LOCK_FILE_PATH}. Another instance might be running.")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred while acquiring lock: {e}")
        return False

def release_lock():
    """Releases the file lock."""
    try:
        if os.path.exists(LOCK_FILE_PATH):
            os.remove(LOCK_FILE_PATH)
            logger.info(f"Released lock: {LOCK_FILE_PATH}")
    except Exception as e:
        logger.error(f"Error releasing lock: {LOCK_FILE_PATH}: {e}")

def _wait_for_file_ready(file_path, timeout=10, stable_time=0.5):
    start = time.time()
    last_size = -1
    stable_since = None
    while time.time() - start < timeout:
        try:
            size = os.path.getsize(file_path)
        except OSError:
            size = -1
        if size == last_size:
            if stable_since is None:
                stable_since = time.time()
            elif time.time() - stable_since >= stable_time:
                try:
                    with open(file_path, "rb"):
                        return True
                except (OSError, PermissionError):
                    pass
        else:
            stable_since = None
            last_size = size
        time.sleep(0.2)
    return False

def move_ai_task_to_done(file_path):
    """Moves a processed AI task file to the AI DONE directory."""
    if not os.path.exists(file_path):
        return
    try:
        done_file_path = os.path.join(AI_DONE_DIR, os.path.basename(file_path))
        move_note(file_path, done_file_path) # Use vault_file_manager skill
    except Exception as e:
        logger.error(f"Error moving AI task file {file_path} to Done directory: {e}")

def process_ai_task_file(file_path):
    if not _wait_for_file_ready(file_path, timeout=15, stable_time=0.6):
        logger.warning(f"File {file_path} not stable/unlocked after wait; skipping processing.")
        return

    try:
        content = []
        retries = 10
        delay = 0.5
        for i in range(retries):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.readlines()
                break
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='utf-16') as f:
                        content = f.readlines()
                    break
                except UnicodeDecodeError:
                    try:
                        with open(file_path, 'r', encoding='latin-1') as f:
                            content = f.readlines()
                        break
                    except (OSError, PermissionError) as e:
                        pass
            except (IOError, OSError, PermissionError) as e:
                pass
            time.sleep(delay)
            delay *= 2

        title = "No Title"
        summary = "No summary available."
        full_body = ""

        if content:
            title = content[0].strip().lstrip('# ').strip() if content else "No Title"
            full_body = " ".join([line.strip() for line in content[1:] if line.strip()])
            
            if full_body:
                summary = full_body[:150]
                if len(full_body) > 150:
                    summary = summary.rsplit(' ', 1)[0] + "..."
            else:
                summary = "No detailed content found."

        task_status = "Needs Action"
        target_directory = AI_NEEDS_ACTION_DIR
        skill_dispatched = False

        # --- Skill Dispatch Logic ---
        full_body_lower = full_body.lower()
        if "send email" in full_body_lower or "email" in full_body_lower:
            recipient_match = re.search(r"to:\s*([\w\.-]+@[\w\.-]+)", full_body_lower)
            subject_match = re.search(r"subject:\s*(.+)", full_body_lower)
            body_match = re.search(r"body:\s*(.+)", full_body_lower)
            
            recipient = recipient_match.group(1).strip() if recipient_match else "default@example.com"
            subject = subject_match.group(1).strip() if subject_match else title
            email_body = body_match.group(1).strip() if body_match else summary

            if send_gmail(recipient, subject, email_body):
                task_status = "Dispatched - Email Sent"
                skill_dispatched = True
            else:
                task_status = "Dispatch Failed - Email"

        elif "post linkedin" in full_body_lower or "linkedin" in full_body_lower:
            linkedin_content_match = re.search(r"content:\s*(.+)", full_body_lower)
            linkedin_content = linkedin_content_match.group(1).strip() if linkedin_content_match else full_body
            
            if post_to_linkedin(linkedin_content):
                task_status = "Dispatched - LinkedIn Posted"
                skill_dispatched = True
            else:
                task_status = "Dispatch Failed - LinkedIn"

        # --- Human Approval Workflow ---
        if not skill_dispatched: # Only apply human approval if no skill was dispatched
            if "approve" in full_body_lower or "review" in full_body_lower or "human_in_the_loop" in full_body_lower:
                task_status = "Needs Approval"
                target_directory = AI_NEEDS_APPROVAL_DIR
            elif "completed" in full_body_lower or "finished" in full_body_lower or "resolved" in full_body_lower():
                task_status = "Done"
                target_directory = AI_DONE_DIR
        else: # If a skill was dispatched, move to done directly
            target_directory = AI_DONE_DIR
            
        original_filename = os.path.basename(file_path)
        new_filename = f"processed_{original_filename}" # For AI Employee, we'll keep it 'processed_'
        output_file_path = os.path.join(target_directory, new_filename)

        output_content = f"""# AI Task: {title}

## Summary
{summary}

## Original File
{file_path}
## Status
{task_status}
"""
        create_note(output_file_path, output_content) # Use vault_file_manager skill

        logging.info(f"AI Employee Processed '{original_filename}' and saved to '{output_file_path}' (Status: {task_status})")
        move_ai_task_to_done(file_path) # Always move to done after processing, even if skill dispatched or needs approval

    except Exception as e:
        logging.error(f"Error processing AI task file {file_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="AI Employee Task Processor")
    parser.add_argument("--once", action="store_true", help="Run the scheduler once and exit.")
    parser.add_argument("--status", action="store_true", help="Check the status of the AI Employee.")
    args = parser.parse_args()

    if args.status:
        logging.info("AI Employee status: OK")
        print("AI Employee status: OK") # Keep print for immediate user feedback
        return

    # Attempt to acquire lock for daemon mode only
    if not args.once:
        if not acquire_lock():
            print("Another instance of AI Employee daemon is already running. Exiting.")
            logging.warning("Another instance of AI Employee daemon is already running. Exiting.")
            sys.exit(1)

    try:
        if args.once:
            logging.info("Running the AI Employee scheduler once...")
            print("Running the AI Employee scheduler once...") # Keep print for immediate user feedback
            for filename in os.listdir(AI_INBOX_DIR):
                if filename.endswith(".md"):
                    file_path = os.path.join(AI_INBOX_DIR, filename)
                    process_ai_task_file(file_path)
            logging.info("Scheduler run complete.")
            print("Scheduler run complete.") # Keep print for immediate user feedback
        else:
            logging.info("Starting the AI Employee daemon...")
            print("Starting the AI Employee daemon...") # Keep print for immediate user feedback
            while True:
                for filename in os.listdir(AI_INBOX_DIR):
                    if filename.endswith(".md"):
                        file_path = os.path.join(AI_INBOX_DIR, filename)
                        process_ai_task_file(file_path)
                logging.info("AI Employee is running and checking for new tasks...")
                print("AI Employee is running and checking for new tasks...") # Keep print for immediate user feedback
                time.sleep(15)
    except KeyboardInterrupt:
        logging.info("AI Employee daemon stopped by user.")
        print("\nAI Employee daemon stopped by user.")
    except Exception as e:
        logging.error(f"An error occurred in the AI Employee daemon: {e}")
        print(f"An error occurred in the AI Employee daemon: {e}")
    finally:
        if not args.once: # Release lock only if running in daemon mode
            release_lock()

if __name__ == "__main__":
    main()