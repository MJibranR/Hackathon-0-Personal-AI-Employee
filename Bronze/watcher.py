import os
import time
import shutil
import logging
from logging.handlers import RotatingFileHandler
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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

# Define the directories
INBOX_DIR = "vault/Inbox/"
NEEDS_ACTION_DIR = "vault/Needs_Action/"
DONE_DIR = "vault/Done/"

# Ensure the output directories exist
os.makedirs(NEEDS_ACTION_DIR, exist_ok=True)
os.makedirs(DONE_DIR, exist_ok=True)

def move_to_done(file_path):
    """Moves a file to the DONE directory."""
    if not os.path.exists(file_path):
        return
    try:
        done_file_path = os.path.join(DONE_DIR, os.path.basename(file_path))
        shutil.move(file_path, done_file_path)
        logging.info(f"Moved file {file_path} to {done_file_path}")
    except Exception as e:
        logging.error(f"Error moving file {file_path} to Done directory: {e}")

class MarkdownEventHandler(FileSystemEventHandler):
    def _wait_for_file_ready(self, file_path, timeout=10, stable_time=0.5):
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

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".md"):
            logging.info(f"[DETECTED] New file: {os.path.basename(event.src_path)}")
            self.process_markdown_file(event.src_path)

    def process_markdown_file(self, file_path):
        if not self._wait_for_file_ready(file_path, timeout=15, stable_time=0.6):
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

            if not content:
                title = "No Title"
                summary = "No summary available."
                full_body = ""
            else:
                title = content[0].strip().lstrip('# ').strip() if content else "No Title"
                full_body = " ".join([line.strip() for line in content[1:] if line.strip()])
                
                if full_body:
                    summary = full_body[:150]
                    if len(full_body) > 150:
                        summary = summary.rsplit(' ', 1)[0] + "..."
                else:
                    summary = "No detailed content found."

            task_status = "Needs Action"
            target_directory = NEEDS_ACTION_DIR

            if "completed" in full_body.lower() or "finished" in full_body.lower() or "resolved" in full_body.lower():
                task_status = "Done"
                target_directory = DONE_DIR

            original_filename = os.path.basename(file_path)
            new_filename = f"response_{original_filename}"
            output_file_path = os.path.join(target_directory, new_filename)

            output_content = f"""# Task: {title}

## Summary
{summary}

## Original File
{file_path}
## Status
{task_status}
"""
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(output_content)

            logging.info(f"[PROCESSED] {original_filename} -> {os.path.join(os.path.basename(target_directory), new_filename)}")
            move_to_done(file_path)

        except Exception as e:
            logging.error(f"Error processing file {file_path}: {e}")

if __name__ == "__main__":
    print("BRONZE Agent Factory File Watcher")
    print(f"Watching:\n{os.path.abspath(INBOX_DIR)}")
    print(f"Output : {os.path.abspath(NEEDS_ACTION_DIR)}")
    print("Drop a .md file into vault/Inbox/ to begin.")
    print("Press Ctrl+C to stop.")

    event_handler = MarkdownEventHandler()
    observer = Observer()
    observer.schedule(event_handler, INBOX_DIR, recursive=False)

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    logging.info("File watcher stopped.")
    print("\nFile watcher stopped.")
