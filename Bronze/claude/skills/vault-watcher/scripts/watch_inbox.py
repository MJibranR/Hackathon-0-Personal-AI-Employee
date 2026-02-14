import argparse
import time
import os
import shutil
import logging
from logging.handlers import RotatingFileHandler
import fcntl # For file locking on Unix-like systems
import msvcrt # For file locking on Windows

# Configure logging
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
log_file_path = os.path.join(LOG_DIR, 'actions.log')
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
AI_NEEDS_APPROVAL_DIR = "AI_Employee_Vault/Needs_Approval/" # New directory for human approval
DEDUPE_LEDGER_FILE = "vault_watcher_ledger" # This is a file, not a directory

# Define Lock file
LOCK_FILE_DIR = "lockfiles"
LOCK_FILE_NAME = "vault_watcher.lock"
LOCK_FILE_PATH = os.path.join(LOCK_FILE_DIR, LOCK_FILE_NAME)

# Ensure the output directories exist
os.makedirs(AI_INBOX_DIR, exist_ok=True)
os.makedirs(AI_NEEDS_ACTION_DIR, exist_ok=True)
os.makedirs(AI_DONE_DIR, exist_ok=True)
os.makedirs(AI_NEEDS_APPROVAL_DIR, exist_ok=True) # Ensure Needs_Approval directory exists
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
        shutil.move(file_path, done_file_path)
        logging.info(f"Moved AI task file {file_path} to {done_file_path}")
    except Exception as e:
        logging.error(f"Error moving AI task file {file_path} to Done directory: {e}")

def load_deduplication_ledger():
    if not os.path.exists(DEDUPE_LEDGER_FILE):
        return set()
    with open(DEDUPE_LEDGER_FILE, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f)

def save_deduplication_ledger(processed_files):
    with open(DEDUPE_LEDGER_FILE, 'w', encoding='utf-8') as f:
        for file_hash in processed_files:
            f.write(f"{file_hash}\n")

def get_file_hash(file_path):
    # A simple hash based on file content and name for deduplication
    # In a real scenario, a more robust hashing algorithm (e.g., SHA256) would be used.
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return str(hash(content + file_path)) # Combine content and path to make hash unique
    except Exception:
        return None

def process_ai_task_file(file_path, processed_files_ledger):
    file_hash = get_file_hash(file_path)
    if file_hash in processed_files_ledger:
        logging.info(f"File {os.path.basename(file_path)} already processed. Skipping.")
        return

    if not _wait_for_file_ready(file_path, timeout=15, stable_time=0.6):
        logging.warning(f"File {file_path} not stable/unlocked after wait; skipping processing.")
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

        # Check for human approval keywords
        if "approve" in full_body.lower() or "review" in full_body.lower() or "human_in_the_loop" in full_body.lower():
            task_status = "Needs Approval"
            target_directory = AI_NEEDS_APPROVAL_DIR
        elif "completed" in full_body.lower() or "finished" in full_body.lower() or "resolved" in full_body.lower():
            task_status = "Done"
            target_directory = AI_DONE_DIR

        original_filename = os.path.basename(file_path)
        new_filename = f"processed_{original_filename}"
        output_file_path = os.path.join(target_directory, new_filename)

        output_content = f"""# AI Task: {title}

## Summary
{summary}

## Original File
{file_path}
## Status
{task_status}
"""
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(output_content)

        logging.info(f"Advanced Watcher Processed '{original_filename}' and saved to '{output_file_path}'")
        move_ai_task_to_done(file_path)
        if file_hash: # Only add to ledger if hash was successfully generated
            processed_files_ledger.add(file_hash) # Add to ledger after successful processing

    except Exception as e:
        logging.error(f"Error processing AI task file {file_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Advanced Vault Watcher")
    parser.add_argument("--reset", action="store_true", help="Reset the deduplication ledger.")
    parser.add_argument("--status", action="store_true", help="Check the status of the watcher.")
    args = parser.parse_args()

    processed_files_ledger = load_deduplication_ledger()

    if args.reset:
        processed_files_ledger.clear()
        save_deduplication_ledger(processed_files_ledger)
        logging.info("Resetting the deduplication ledger...")
        print("Resetting the deduplication ledger...") # Keep print for immediate user feedback
        logging.info("Ledger reset complete.")
        print("Ledger reset complete.") # Keep print for immediate user feedback
        return

    if args.status:
        logging.info(f"Advanced Watcher status: OK. Processed {len(processed_files_ledger)} unique files.")
        print(f"Advanced Watcher status: OK. Processed {len(processed_files_ledger)} unique files.") # Keep print for immediate user feedback
        return

    # Attempt to acquire lock
    if not acquire_lock():
        print("Another instance of Advanced Vault Watcher is already running. Exiting.")
        logging.warning("Another instance of Advanced Vault Watcher is already running. Exiting.")
        sys.exit(1)

    try:
        logging.info("Starting the advanced vault watcher...")
        print("Starting the advanced vault watcher...") # Keep print for immediate user feedback
        while True:
            for filename in os.listdir(AI_INBOX_DIR):
                if filename.endswith(".md"):
                    file_path = os.path.join(AI_INBOX_DIR, filename)
                    process_ai_task_file(file_path, processed_files_ledger)
            save_deduplication_ledger(processed_files_ledger) # Save ledger periodically
            logging.info("Advanced watcher is running and checking for new tasks...")
            print("Advanced watcher is running and checking for new tasks...") # Keep print for immediate user feedback
            time.sleep(15)
    except KeyboardInterrupt:
        logging.info("Advanced watcher stopped.")
        print("\nAdvanced watcher stopped.")
    except Exception as e:
        logging.error(f"An error occurred in the advanced watcher: {e}")
        print(f"An error occurred in the advanced watcher: {e}")
    finally:
        release_lock() # Ensure lock is released on exit

if __name__ == "__main__":
    main()