import os
import time
import glob
import datetime
import re
import shutil
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
log_file_path = os.path.join(LOG_DIR, 'ai_employee.log')
log_handler = RotatingFileHandler(log_file_path, maxBytes=1*1024*1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VAULT_PATH = os.path.join(PROJECT_ROOT, "vault")
NEEDS_ACTION_PATH = os.path.join(VAULT_PATH, "Needs_Action")
PENDING_APPROVAL_PATH = os.path.join(VAULT_PATH, "Pending_Approval")
DONE_PATH = os.path.join(VAULT_PATH, "Done")

def get_processed_plans():
    # For simplicity, we process all plans in the directory.
    # A more robust system would have a ledger for processed plans.
    return set()

def parse_plan(plan_content):
    """Parses a plan file to extract action details."""
    actions = []
    
    try:
        # Extract the content between the '---' markers
        original_task = plan_content.split('---')[1].strip()
    except IndexError:
        logger.error("Could not find '---' separators in plan file.")
        return None

    # Check for email action
    if "send an email" in original_task.lower():
        try:
            to_address = re.search(r'send an email to ([\w\.-]+@[\w\.-]+)', original_task, re.IGNORECASE).group(1)
            subject = re.search(r'Subject: (.*)', original_task, re.IGNORECASE).group(1)
            body = original_task.split('Body:')[1].strip()
            actions.append({
                "action": "send_email",
                "to": to_address,
                "subject": subject,
                "body": body
            })
        except (AttributeError, IndexError) as e:
            logger.error(f"Could not parse email details from plan: {e}")

    # Check for LinkedIn action
    if "post the following on linkedin" in original_task.lower():
        try:
            content = original_task.split('on behalf of "Muhammad Jibran Rehan":')[1].strip()
            actions.append({
                "action": "post_linkedin",
                "content": content
            })
        except (AttributeError, IndexError) as e:
            logger.error(f"Could not parse LinkedIn post content from plan: {e}")
            
    return actions if actions else None

def create_approval_request(plan_file, action_details):
    """Creates a file in the Pending_Approval directory for a single action."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f") # Add microseconds for more uniqueness
    action_type = action_details['action']
    approval_filename = f"APPROVAL_{action_type}_{timestamp}.md"
    approval_file_path = os.path.join(PENDING_APPROVAL_PATH, approval_filename)

    # Dynamically build approval content based on action_details
    approval_content_header = f"""---
action: {action_type}
plan_file: {os.path.basename(plan_file)}
"""
    approval_content_body = ""

    if action_type == 'send_email':
        approval_content_header += f"to: {action_details.get('to', 'N/A')}\n"
        approval_content_header += f"subject: {action_details.get('subject', 'N/A')}\n"
        # Ensure body content is correctly indented for YAML multiline string
        body_content = action_details.get('body', 'N/A').replace('\n', '\n  ')
        approval_content_header += f"body: |\n  {body_content}\n" 
        
        approval_content_body = f"""## Email Details
- To: {action_details.get('to', 'N/A')}
- Subject: {action_details.get('subject', 'N/A')}
- Body:
{action_details.get('body', 'N/A')}
"""
    elif action_type == 'post_linkedin':
        # Ensure content is correctly indented for YAML multiline string
        linkedin_content = action_details.get('content', 'N/A').replace('\n', '\n  ')
        approval_content_header += f"content: |\n  {linkedin_content}\n"
        
        approval_content_body = f"""## LinkedIn Post Content
{action_details.get('content', 'N/A')}
"""
    
    final_approval_content = f"""{approval_content_header}---

{approval_content_body}

## To Approve
Move this file to the /vault/Approved folder.

## To Reject
Move this file to the /vault/Rejected folder.
"""

    try:
        os.makedirs(PENDING_APPROVAL_PATH, exist_ok=True)
        with open(approval_file_path, 'w', encoding='utf-8') as f:
            f.write(final_approval_content)
        logger.info(f"Created approval request: {approval_file_path}")
        return True
    except Exception as e:
        logger.error(f"Error creating approval file {approval_file_path}: {e}")
        return False

def move_plan_to_done(plan_file):
    """Moves a plan file to the Done directory."""
    done_file_path = os.path.join(DONE_PATH, os.path.basename(plan_file))
    shutil.move(plan_file, done_file_path)
    logger.info(f"Moved plan {os.path.basename(plan_file)} to Done.")

def scan_plans_and_process():
    """Scans the Needs_Action directory and processes new plans."""
    processed_plans = get_processed_plans()
    logger.info(f"Scanning for plans: {NEEDS_ACTION_PATH}")

    for plan_file in glob.glob(os.path.join(NEEDS_ACTION_PATH, "*.md")):
        logger.info(f"New plan found: {plan_file}")
        with open(plan_file, 'r', encoding='utf-8') as f: # Specify encoding
            plan_content = f.read()
        
        actions_to_take = parse_plan(plan_content)
        
        if actions_to_take:
            for action_details in actions_to_take:
                create_approval_request(plan_file, action_details)
            move_plan_to_done(plan_file)
        else:
            logger.info(f"No specific actions found in plan: {plan_file}. Moving to Done.")
            move_plan_to_done(plan_file)

def main():
    """Main loop for the AI Employee processor."""
    os.makedirs(NEEDS_ACTION_PATH, exist_ok=True)
    os.makedirs(PENDING_APPROVAL_PATH, exist_ok=True)
    os.makedirs(DONE_PATH, exist_ok=True)
    
    while True:
        scan_plans_and_process()
        logger.info(f"Waiting for 15 seconds before next scan...")
        time.sleep(15)

if __name__ == "__main__":
    main()
