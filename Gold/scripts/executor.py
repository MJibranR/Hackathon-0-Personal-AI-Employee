import os
import time
import glob
import shutil
import subprocess
import sys
import logging
import re
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
import yaml # Import PyYAML

load_dotenv()

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
APPROVED_PATH = os.path.join(VAULT_PATH, "Approved")
DONE_PATH = os.path.join(VAULT_PATH, "Done")

from .error_manager import ErrorManager

from .utils.audit_logger import audit_logger

# Paths to the action scripts
SEND_EMAIL_SCRIPT = os.path.join(PROJECT_ROOT, ".claude", "skills", "gmail-send", "scripts", "send_email.py")
POST_LINKEDIN_SCRIPT = os.path.join(PROJECT_ROOT, ".claude", "skills", "linkedin-post", "scripts", "post_linkedin.py")
ODOO_SCRIPT = os.path.join(PROJECT_ROOT, ".claude", "skills", "odoo-accounting", "scripts", "odoo_accounting.py")
META_SCRIPT = os.path.join(PROJECT_ROOT, ".claude", "skills", "meta-social", "scripts", "meta_social.py")
X_SCRIPT = os.path.join(PROJECT_ROOT, ".claude", "skills", "x-twitter", "scripts", "x_twitter.py")

@ErrorManager.with_backoff(max_retries=3, base_delay=2.0)
def execute_action(action_details):
    """Executes the action specified in the approval file."""
    action = action_details.get('action')
    logger.info(f"Executing action: {action}")
    
    # Pre-execution logging (audit trail)
    audit_logger.log(
        action_type=action,
        target=action_details.get('to', action_details.get('client_id', 'n/a')),
        parameters=action_details,
        approval_status="approved",
        approved_by="human"
    )

    try:
        if action == 'send_email':
            to = action_details.get('to')
            subject = action_details.get('subject')
            body = action_details.get('body')
            if to and subject and body:
                # Ensure body is a single string for subprocess call
                body_str = body.replace('\n  ', '\n').strip()
                subprocess.run([sys.executable, SEND_EMAIL_SCRIPT, to, subject, body_str])
            else:
                logger.error(f"Missing details for sending email: {action_details}")

        elif action == 'post_linkedin':
            content = action_details.get('content')
            if content:
                # Ensure content is a single string for subprocess call
                content_str = content.replace('\n  ', '\n').strip()
                subprocess.run([sys.executable, POST_LINKEDIN_SCRIPT, content_str])
            else:
                logger.error(f"Missing content for LinkedIn post: {action_details}")

        elif action == 'create_odoo_invoice':
            client_id = action_details.get('client_id')
            amount = action_details.get('amount')
            if client_id and amount:
                subprocess.run([sys.executable, ODOO_SCRIPT, str(client_id), str(amount)])
            else:
                logger.error(f"Missing details for Odoo invoice: {action_details}")

        elif action in ['post_facebook', 'post_instagram']:
            platform = action.replace('post_', '')
            content = action_details.get('content')
            if content:
                content_str = content.replace('\n  ', '\n').strip()
                subprocess.run([sys.executable, META_SCRIPT, platform, content_str])
            else:
                logger.error(f"Missing content for Meta post: {action_details}")

        elif action == 'post_x':
            content = action_details.get('content')
            if content:
                content_str = content.replace('\n  ', '\n').strip()
                subprocess.run([sys.executable, X_SCRIPT, content_str])
            else:
                logger.error(f"Missing content for X post: {action_details}")
        
        else:
            logger.error(f"Unknown action: {action_details}")
            
    except Exception as e:
        # Audit failure
        audit_logger.log(
            action_type=action,
            target="n/a",
            parameters=action_details,
            result="failure",
            approval_status="approved"
        )
        raise e

def move_to_done(file_path):
    """Moves a file to the Done directory."""
    done_file_path = os.path.join(DONE_PATH, os.path.basename(file_path))
    shutil.move(file_path, done_file_path)
    logger.info(f"Moved approval file {os.path.basename(file_path)} to Done.")

def scan_approved_and_execute():
    """Scans the Approved directory and executes tasks."""
    logger.info(f"Scanning for approved tasks: {APPROVED_PATH}")
    for file_path in glob.glob(os.path.join(APPROVED_PATH, "*.md")):
        logger.info(f"Approved task found: {file_path}")
        
        action_details = parse_approval_file(file_path)
        if action_details:
            execute_action(action_details)
            move_to_done(file_path)
        else:
            logger.error(f"Could not parse approval file: {file_path}")

def main():
    os.makedirs(APPROVED_PATH, exist_ok=True)
    os.makedirs(DONE_PATH, exist_ok=True)

    while True:
        scan_approved_and_execute()
        logger.info(f"Waiting for {10} seconds before next scan...")
        time.sleep(10)

if __name__ == "__main__":
    main()