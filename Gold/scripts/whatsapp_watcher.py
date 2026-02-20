# scripts/whatsapp_watcher.py
import time
import logging
from playwright.sync_api import sync_playwright
from .base_watcher import BaseWatcher

class WhatsAppWatcher(BaseWatcher):
    def __init__(self, check_interval=60):
        super().__init__(check_interval)
        self.playwright = None
        self.browser = None
        self.page = None
        self.processed_messages = set()

    def start_browser(self):
        self.playwright = sync_playwright().start()
        # Launch browser with user profile for session persistence
        self.browser = self.playwright.chromium.launch_persistent_context(
            user_data_dir="whatsapp_session",
            headless=False  # Headless false for initial QR scan
        )
        self.page = self.browser.new_page()
        self.page.goto("https://web.whatsapp.com")
        self.logger.info("Please scan the QR code if needed.")
        time.sleep(30) # Wait for initial load

    def check_for_updates(self):
        if not self.page:
            self.start_browser()
        
        # Look for unread indicators (green badge)
        unread_chats = self.page.query_selector_all('div[aria-label^="Unread"]')
        updates = []
        for chat in unread_chats:
            chat_name = chat.query_selector('span[title]').text_content()
            unread_count = chat.query_selector('span[aria-label*="unread message"]').text_content()
            updates.append({"chat": chat_name, "count": unread_count, "timestamp": time.time()})
        
        return updates

    def process_update(self, update):
        chat_name = update['chat']
        count = update['count']
        
        title = f"WhatsApp: {chat_name} ({count} unread)"
        content = f"""**Chat:** {chat_name}
**Unread Messages:** {count}
**Time:** {time.ctime(update['timestamp'])}

---
**Actions Required:**
- [ ] Check messages
- [ ] Reply
"""
        return self.create_task_file(title, content, priority="High", tags=["whatsapp", "communication"])

    def close(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

if __name__ == "__main__":
    watcher = WhatsAppWatcher(check_interval=60)
    try:
        watcher.run()
    except KeyboardInterrupt:
        watcher.close()
