from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import sys
import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Configure logging
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
log_file_path = os.path.join(LOG_DIR, 'ai_employee.log') # Using ai_employee.log for consistency
log_handler = RotatingFileHandler(log_file_path, maxBytes=1*1024*1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)


load_dotenv() # Load environment variables from .env

# Ensure the project root is in sys.path when running this script directly
# This allows absolute imports like 'skills.base_watcher' to resolve.
script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_dir, os.pardir)) # 'os.pardir' means '..'
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from skills.base_watcher import BaseWatcher
from datetime import datetime


class GmailWatcher(BaseWatcher):
    def __init__(self, vault_path: str, credentials_path: str = 'credentials.json', token_path: str = 'token.json'):
        super().__init__(vault_path, check_interval=120)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.inbox = self.vault_path / 'Inbox' # Add this line
        self.inbox.mkdir(parents=True, exist_ok=True) # Ensure Inbox exists
        # OAuth2 scopes - use modify so we can mark messages as read if desired
        SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

        # Paths for client secrets and saved user token
        self.credentials_path = credentials_path
        self.token_path = token_path

        try:
            self.creds = None

            # Try to load saved user credentials (token.json)
            if os.path.exists(self.token_path):
                self.creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

            # If no valid credentials loaded, try performing the OAuth flow using client secrets
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                elif os.path.exists(self.credentials_path):
                    flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
                    self.creds = flow.run_local_server(port=0)
                else:
                    raise FileNotFoundError(f"{self.credentials_path} not found.")

            # Save/refresh token file
            if self.creds:
                with open(self.token_path, 'w') as token_file:
                    token_file.write(self.creds.to_json())

            # Build the Gmail service
            if self.creds and self.creds.valid:
                self.service = build('gmail', 'v1', credentials=self.creds)
            else:
                self.service = None

        except Exception as e:
            self.logger.warning(f"Could not load Gmail credentials or build service: {e}. GmailWatcher will run in mock mode.")
            self.service = None # Run in mock mode if service cannot be built

        self.processed_ids = set()
        
    def check_for_updates(self) -> list:
        if not self.service:
            self.logger.info("GmailWatcher in mock mode: no actual updates checked.")
            # Simulate a new email every few checks for demonstration
            if len(self.processed_ids) == 0: # Only create one mock email for now
                mock_message = {'id': 'mock_email_12345', 'snippet': 'This is a mock important email needing action.'}
                return [mock_message]
            return []

        try:
            results = self.service.users().messages().list(
                userId='me', q='is:unread is:important'
            ).execute()
            messages = results.get('messages', [])
            return [m for m in messages if m['id'] not in self.processed_ids]
        except Exception as e:
            self.logger.error(f"Error checking Gmail updates: {e}")
            return []
    
    def create_action_file(self, message) -> Path:
        if not self.service:
            # Mock behavior for file creation
            content = f'''---
type: email
from: Mock Sender <mock@example.com>
subject: Mock Important Email
received: {datetime.now().isoformat()}
priority: high
status: pending
---

## Email Content
{message['snippet']}

## Suggested Actions
- [ ] Review mock email
'''
            filepath = self.inbox / f'EMAIL_{message["id"]}.md' # Changed to self.inbox
        else:
            msg = self.service.users().messages().get(
                userId='me', id=message['id']
            ).execute()
            
            # Extract headers
            headers = {h['name']: h['value'] for h in msg['payload']['headers']}
            
            content = f'''---
type: email
from: {headers.get('From', 'Unknown')}
subject: {headers.get('Subject', 'No Subject')}
received: {datetime.now().isoformat()}
priority: high
status: pending
---


## Email Content
{msg.get('snippet', '')}


## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
'''
            filepath = self.needs_action / f'EMAIL_{message["id"]}.md'
        
        filepath.write_text(content)
        self.processed_ids.add(message['id'])
        self.logger.info(f"Created action file: {filepath}")
        return filepath

if __name__ == '__main__':
    # For hackathon context, assuming the script is run from the project root (silver)
    # VAULT_PATH should point to the 'vault' directory within the project root.
    VAULT_PATH = Path(__file__).parent.parent / 'vault' # Corrected VAULT_PATH calculation
    watcher = GmailWatcher(str(VAULT_PATH))
    # To run the watcher, you'd typically call watcher.run() in a separate process
    # For this simulation, we'll just demonstrate its capabilities
    print("GmailWatcher initialized (mock mode if credentials not found).")
    mock_updates = watcher.check_for_updates()
    if mock_updates:
        watcher.create_action_file(mock_updates[0])
        print(f"Mock email action file created in {VAULT_PATH / 'Inbox'}") # Changed to Inbox
    watcher.run() # Start the continuous run loop