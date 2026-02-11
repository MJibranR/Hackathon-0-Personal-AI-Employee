import os
import datetime

# --- Configuration Section ---
# Define the log files to monitor
SYSTEM_LOG_FILE = os.path.join("Logs", "System_Log.md")
WATCHER_ERROR_LOG = os.path.join("Logs", "watcher_errors.log")

# Define the maximum size for a log file before rotation (in bytes)
# 1 MB = 1 * 1024 * 1024 bytes
MAX_LOG_SIZE_BYTES = 1 * 1024 * 1024 

# --- Log Rotation Function ---

def check_and_rotate_log(log_filepath):
    """
    Checks if a log file exceeds a predefined size. If it does, the function
    renames the current log file with a timestamp and creates a new, empty
    log file with the original name. This prevents log files from growing
    indefinitely.
    """
    # Ensure the Logs directory exists, though file_watcher.py should handle this
    log_dir = os.path.dirname(log_filepath)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        print(f"Created missing log directory: {log_dir}")
        # If the directory didn't exist, the log file certainly doesn't, so no rotation needed yet.
        return

    # Check if the log file exists
    if os.path.exists(log_filepath):
        # Get the current size of the log file
        file_size = os.path.getsize(log_filepath)

        # If the file size exceeds the maximum allowed size
        if file_size > MAX_LOG_SIZE_BYTES:
            print(f"Log file '{log_filepath}' ({file_size} bytes) exceeds {MAX_LOG_SIZE_BYTES} bytes. Rotating...")

            # Generate a timestamp for the new name
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            
            # Split the original filename into name and extension
            name, ext = os.path.splitext(os.path.basename(log_filepath))
            
            # Construct the new (rotated) filename
            rotated_filename = f"{name}_{timestamp}{ext}"
            rotated_filepath = os.path.join(log_dir, rotated_filename)

            try:
                # Rename the old log file to the rotated filename
                os.rename(log_filepath, rotated_filepath)
                print(f"Rotated '{log_filepath}' to '{rotated_filepath}'")

                # Create a new, empty log file with the original name
                # This ensures the logging system can continue writing to the expected path
                with open(log_filepath, "w", encoding="utf-8") as f:
                    # You might want to write an initial header here if the log type requires it
                    # For System_Log.md, you might write "# System Log"
                    # For watcher_errors.log, you might write "# Watcher Error Log"
                    # For simplicity, we'll leave it empty unless specified otherwise by the user.
                    pass 
                print(f"Created new empty log file: '{log_filepath}'")

            except OSError as e:
                # Handle potential errors during file operations (e.g., permissions)
                print(f"Error rotating log file '{log_filepath}': {e}")
        else:
            print(f"Log file '{log_filepath}' is within size limits ({file_size} bytes).")
    else:
        print(f"Log file '{log_filepath}' does not exist. No rotation needed.")

# --- Main Execution ---

if __name__ == "__main__":
    print("Starting log manager script...")
    
    # Check and rotate the System Log file
    check_and_rotate_log(SYSTEM_LOG_FILE)
    
    # Check and rotate the Watcher Error Log file
    check_and_rotate_log(WATCHER_ERROR_LOG)
    
    print("Log manager script finished.")
