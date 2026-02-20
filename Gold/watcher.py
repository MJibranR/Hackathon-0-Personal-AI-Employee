import os
import time
import logging
from logging.handlers import RotatingFileHandler
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
log_file_path = os.path.join(LOG_DIR, 'actions.log')
log_handler = RotatingFileHandler(log_file_path, maxBytes=1*1024*1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

# Define the directory to watch
INBOX_DIR = "vault/Inbox/"
os.makedirs(INBOX_DIR, exist_ok=True)

class NewFileHandler(FileSystemEventHandler):
    """A simple handler that just logs when a new file is created."""
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".md"):
            # Log that a new file has been detected.
            # The planner.py script will be responsible for processing it.
            logger.info(f"[FILE DETECTED] New file in Inbox: {os.path.basename(event.src_path)}")
            print(f"[FILE DETECTED] New file in Inbox: {os.path.basename(event.src_path)}")


if __name__ == "__main__":
    print("AI Employee File Watcher")
    print(f"Watching for new files in: {os.path.abspath(INBOX_DIR)}")
    print("Press Ctrl+C to stop.")

    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, INBOX_DIR, recursive=False)

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    logger.info("File watcher stopped.")
    print("\nFile watcher stopped.")

