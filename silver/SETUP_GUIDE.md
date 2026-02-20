# AI Employee Setup Guide

This guide will help you set up the necessary credentials for your AI Employee to interact with external services like Gmail and LinkedIn.

---

## 1. Google App Password (for Sending Emails)

If you have 2-Factor Authentication (2FA) enabled on your Gmail account, you cannot use your regular password for applications like this. You need to generate a special "App Password".

**Steps:**

1.  Go to the [Google App Passwords page](https://myaccount.google.com/apppasswords). You might need to sign in to your Google Account.
2.  If you have multiple apps listed, select "Mail" for the app and "Other (Custom name)" for the device. You can name it "AI Employee" or anything descriptive.
3.  Click "Generate".
4.  A 16-character password will be generated. Copy this password.
5.  **Update your `.env` file:** Open the `.env` file in your project root and update the `EMAIL_PASSWORD` variable with this newly generated App Password.
    ```
    EMAIL_ADDRESS=your_gmail_address@gmail.com
    EMAIL_PASSWORD=your_16_character_app_password
    ```

---

## 2. Gmail API Credentials (for Gmail Watcher)

To allow the `GmailWatcher` to read your emails, you need to enable the Gmail API and generate `credentials.json` file. This involves setting up an OAuth 2.0 client ID.

**Steps:**

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a new project (if you don't have one) or select an existing one.
3.  Navigate to "APIs & Services" > "Enabled APIs & Services".
4.  Search for and enable the "Gmail API".
5.  Go to "APIs & Services" > "Credentials".
6.  Click "CREATE CREDENTIALS" and choose "OAuth client ID".
7.  Select "Desktop app" as the application type and give it a name (e.g., "AI Employee Desktop").
8.  Click "CREATE".
9.  A dialog will appear with your client ID and client secret. Click "DOWNLOAD CLIENT CONFIGURATION" and save the file as `credentials.json` in your project's root directory (`C:\Users\DELL\Desktop\Hackathon 0\silver`).

---

## 3. LinkedIn Credentials

The LinkedIn script uses Playwright to automate posting. It will now run in a visible browser window.

**Steps:**

1.  Ensure your `LINKEDIN_EMAIL` and `LINKEDIN_PASSWORD` are correctly set in your `.env` file.
2.  When the LinkedIn action is triggered, a browser window will open. You might need to manually log in or solve a CAPTCHA. Be ready to interact with this window.

---

## 4. Restarting the AI Employee

After updating your `.env` file and placing `credentials.json`, you need to restart all AI Employee processes.

**Steps:**

1.  Close all open command prompt windows that were started by `run_ai_employee.bat`.
2.  Open your terminal in the project root (`C:\Users\DELL\Desktop\Hackathon 0\silver`).
3.  Run the command: `.un_ai_employee.bat`

Once restarted, the system will process the new tasks in `vault/Inbox`, create plans, prompt for approval (if needed), and then attempt to execute the actions with your updated credentials.
