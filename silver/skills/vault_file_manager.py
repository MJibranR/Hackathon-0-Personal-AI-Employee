import os
import shutil
import logging

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True) # Ensure logs directory exists
logging.basicConfig(filename=os.path.join(LOG_DIR, 'ai_employee.log'), level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def create_note(path, content):
    """Creates a new markdown note at the specified path with content."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        logging.info(f"VaultFileManager Skill: Created note at {path}")
        return True
    except Exception as e:
        logging.error(f"VaultFileManager Skill: Error creating note at {path}: {e}")
        return False

def update_note(path, content):
    """Updates an existing markdown note at the specified path with new content."""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        logging.info(f"VaultFileManager Skill: Updated note at {path}")
        return True
    except Exception as e:
        logging.error(f"VaultFileManager Skill: Error updating note at {path}: {e}")
        return False

def move_note(source_path, destination_path):
    """Moves a markdown note from source_path to destination_path."""
    try:
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        shutil.move(source_path, destination_path)
        logging.info(f"VaultFileManager Skill: Moved note from {source_path} to {destination_path}")
        return True
    except Exception as e:
        logging.error(f"VaultFileManager Skill: Error moving note from {source_path} to {destination_path}: {e}")
        return False

if __name__ == "__main__":
    # Example usage
    test_dir = "test_vault_manager"
    os.makedirs(test_dir, exist_ok=True)

    create_note(os.path.join(test_dir, "new_note.md"), "# New Note
This is a test note.")
    update_note(os.path.join(test_dir, "new_note.md"), "# Updated Note
This note has been updated.")
    move_note(os.path.join(test_dir, "new_note.md"), os.path.join(test_dir, "sub_dir", "moved_note.md"))

    shutil.rmtree(test_dir) # Clean up
