import os
import sys
import time
import datetime

def request_approval(action_description):
    """
    Creates an approval request file and waits for a human to approve or reject it.
    """
    approval_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'AI_Employee_Vault', 'Needs_Approval'))
    os.makedirs(approval_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    approval_filename = f"approval_request_{timestamp}.md"
    approval_filepath = os.path.join(approval_dir, approval_filename)

    content = f"""# Human Approval Request

## Action
{action_description}

## Status
PENDING

---
**To approve, replace 'PENDING' with 'APPROVED'.**
**To reject, replace 'PENDING' with 'REJECTED'.**
"""

    try:
        with open(approval_filepath, 'w') as f:
            f.write(content)
        print(f"Approval request created at: {approval_filepath}")
    except Exception as e:
        print(f"Error: Could not create approval file. {e}")
        sys.exit(1)

    # Wait for approval
    timeout = 3600  # 1 hour
    start_time = time.time()
    while time.time() - start_time < timeout:
        with open(approval_filepath, 'r') as f:
            file_content = f.read()
        
        if "APPROVED" in file_content:
            print("Action approved.")
            sys.exit(0)
        elif "REJECTED" in file_content:
            print("Action rejected.")
            sys.exit(1)
            
        time.sleep(5)

    print("Approval timed out.")
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python request_approval.py \"<action_description>\"")
        sys.exit(1)

    description = sys.argv[1]
    request_approval(description)