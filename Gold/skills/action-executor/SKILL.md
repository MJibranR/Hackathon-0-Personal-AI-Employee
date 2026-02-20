# Action Executor Skill

This skill executes actions that have been approved by a human.

## Functionality
- Watches the `/vault/Approved` directory for approval files.
- Parses the approval file to understand the action and its parameters.
- Calls the appropriate script to execute the action (e.g., `send_email.py`, `post_linkedin.py`).
- Moves the approval file to the `/vault/Done` directory after execution.

## How to Use
This skill is automatically activated by the orchestrator when a file is moved to the `/vault/Approved` directory.

## Example
When a human approves an email by moving the approval file, the Action Executor reads the file, calls the `send_email.py` script with the correct parameters, and sends the email.
