import os
import sys
import time
from playwright.sync_api import sync_playwright

# Define a directory for screenshots
SCREENSHOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "logs", "screenshots"))
os.makedirs(SCREENSHOT_DIR, exist_ok=True) # Ensure screenshot directory exists

def post_to_linkedin(content):
    email = os.environ.get("LINKEDIN_EMAIL")
    password = os.environ.get("LINKEDIN_PASSWORD")

    if not email or not password:
        print("Error: LINKEDIN_EMAIL or LINKEDIN_PASSWORD environment variables not set.")
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        try:
            page.goto("https://www.linkedin.com/login")
            page.fill("input#username", email)
            page.fill("input#password", password)
            page.click("button[type='submit']")
            page.wait_for_load_state('networkidle')

            # Check for successful login by looking for the feed
            if not page.is_visible("div.feed-identity-module"):
                 screenshot_filename = f"linkedin_login_failed_{int(time.time())}.png"
                 screenshot_path = os.path.join(SCREENSHOT_DIR, screenshot_filename)
                 page.screenshot(path=screenshot_path)
                 print(f"Error: LinkedIn login failed. Please check credentials or for CAPTCHA. Screenshot saved to {screenshot_path}")
                 browser.close()
                 sys.exit(1)
            
            # Screenshot after successful login
            screenshot_filename = f"linkedin_logged_in_{int(time.time())}.png"
            screenshot_path = os.path.join(SCREENSHOT_DIR, screenshot_filename)
            page.screenshot(path=screenshot_path)
            print(f"Info: Logged into LinkedIn. Screenshot saved to {screenshot_path}")

            page.click("button.share-box__open-modal-button")
            page.wait_for_selector("div.ql-editor", state="visible")
            
            # Screenshot before filling post content
            screenshot_filename = f"linkedin_post_modal_open_{int(time.time())}.png"
            screenshot_path = os.path.join(SCREENSHOT_DIR, screenshot_filename)
            page.screenshot(path=screenshot_path)
            print(f"Info: Post modal open. Screenshot saved to {screenshot_path}")

            page.fill("div.ql-editor", content)
            page.click("button.share-actions__primary-action")
            
            page.wait_for_timeout(10000) # Increased timeout for post submission

            # Screenshot after clicking post button
            screenshot_filename = f"linkedin_post_button_clicked_{int(time.time())}.png"
            screenshot_path = os.path.join(SCREENSHOT_DIR, screenshot_filename)
            page.screenshot(path=screenshot_path)
            print(f"Info: Post button clicked. Screenshot saved to {screenshot_path}")
            
            print("LinkedIn post created successfully.")
            
        except Exception as e:
            print(f"Error: An error occurred while posting to LinkedIn. {e}")
            sys.exit(1)
        finally:
            browser.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python post_linkedin.py \"<post_content>\"")
        sys.exit(1)
    
    post_content = sys.argv[1]
    post_to_linkedin(post_content)