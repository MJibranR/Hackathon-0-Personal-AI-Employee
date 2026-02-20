import os
import sys
import shutil

def move_task(source_path, dest_folder):
    """
    Moves a task file to a specified directory within the vault.
    """
    base_vault_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'AI_Employee_Vault'))
    valid_folders = ["Inbox", "Needs_Action", "Done"]

    if dest_folder not in valid_folders:
        print(f"Error: Invalid destination folder '{dest_folder}'. Must be one of {valid_folders}.")
        sys.exit(1)

    if not os.path.isfile(source_path):
        print(f"Error: Source file not found at '{source_path}'.")
        sys.exit(1)

    dest_path = os.path.join(base_vault_path, dest_folder, os.path.basename(source_path))
    
    try:
        os.makedirs(os.path.join(base_vault_path, dest_folder), exist_ok=True)
        shutil.move(source_path, dest_path)
        print(f"Successfully moved {os.path.basename(source_path)} to {dest_folder}.")
    except Exception as e:
        print(f"Error: Failed to move file. {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python move_task.py <source_file_path> <target_directory>")
        sys.exit(1)

    source_file = sys.argv[1]
    target_dir = sys.argv[2]
    move_task(source_file, target_dir)