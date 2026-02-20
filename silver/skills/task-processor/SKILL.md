# Task Processor Skill

This skill is responsible for processing a generated plan and creating the necessary approval requests for actions that require human-in-the-loop verification.

## Functionality
- Reads a `Plan_...md` file from the `/vault/Plans` directory.
- Parses the plan to identify the required action (e.g., 'send_email', 'post_linkedin').
- Creates a detailed approval request file in the `/vault/Pending_Approval` directory.
- Moves the processed plan file to the `/vault/Done` directory.

## How to Use
This skill is typically activated automatically by the orchestrator after a plan has been generated.

## Example
When a plan for sending an invoice email is created, the Task Processor creates an approval file with the email's recipient, subject, and body, and places it in the pending approval queue for human review.
