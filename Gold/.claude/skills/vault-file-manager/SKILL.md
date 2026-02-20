# Skill: vault-file-manager

## Description
Manages the workflow of task files by moving them between different stages within the `AI_Employee_Vault`. This is essential for tracking task progress.

## Usage
Provide the source file path and the target directory.

### Command
```
python .claude/skills/vault-file-manager/scripts/move_task.py <source_file_path> <target_directory>
```
Valid target directories are `Inbox`, `Needs_Action`, and `Done`.

## Requirements
- The script requires Python 3.10+.
- The source file must exist.
- The target directory must be one of the valid options.

## Output
- On success, it prints: "Successfully moved [source_file] to [target_directory]."
- On failure, it prints an error message.