# scripts/gmail_watcher.py
import imaplib
import email
from email.header import decode_header
import os
import time
import logging
from pathlib import Path
from datetime import datetime
from .base_watcher import BaseWatcher
from dotenv import load_dotenv

load_dotenv()

class GmailWatcher(BaseWatcher):
    def __init__(self, check_interval=60):
        super().__init__(check_interval)
        self.email_user = os.getenv("EMAIL_ADDRESS")
        self.email_pass = os.getenv("EMAIL_PASSWORD")
        self.server = "imap.gmail.com"
        self.processed_ids = set()

    def check_for_updates(self):
        updates = []
        try:
            # Connect to Gmail
            mail = imaplib.IMAP4_SSL(self.server)
            mail.login(self.email_user, self.email_pass)
            mail.select("inbox")

            # Search for unread messages
            status, messages = mail.search(None, 'UNSEEN')
            if status != "OK":
                return []

            for msg_id in messages[0].split():
                if msg_id in self.processed_ids:
                    continue
                
                # Fetch message
                res, msg_data = mail.fetch(msg_id, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding or "utf-8")
                        
                        sender = msg.get("From")
                        updates.append({
                            "id": msg_id,
                            "subject": subject,
                            "sender": sender,
                            "body": self._get_body(msg)
                        })
                        self.processed_ids.add(msg_id)

            mail.logout()
        except Exception as e:
            self.logger.error(f"Gmail IMAP Error: {e}")
        
        return updates

    def _get_body(self, msg):
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode()
        else:
            return msg.get_payload(decode=True).decode()
        return ""

    def process_update(self, update):
        title = f"Email: {update['subject']}"
        content = f"""**From:** {update['sender']}
**Subject:** {update['subject']}

{update['body'][:500]}...

---
**Actions Required:**
- [ ] Reply
- [ ] Create Task
"""
        return self.create_task_file(title, content, priority="High", tags=["email"])

if __name__ == "__main__":
    watcher = GmailWatcher(check_interval=60)
    watcher.run()
