# Skill: human-approval

## Description
This skill creates a formal request for human approval for sensitive actions. It generates a file in the `Needs_Approval` directory and waits for a human to approve or reject the action by editing the file.

## Usage
Provide a description of the action requiring approval.

### Command
```
python .claude/skills/human-approval/scripts/request_approval.py "<action_description>"
```

## Requirements
- The script requires Python 3.10+.
- A human operator must monitor the `AI_Employee_Vault/Needs_Approval/` directory.

## Output
- Creates an approval file and prints its path.
- Waits for approval and then prints "Action approved." or "Action rejected.".
- If timeout, it prints "Approval timed out."