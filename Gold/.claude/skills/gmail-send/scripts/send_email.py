import os
import smtplib
import sys
from email.mime.text import MIMEText

def send_email(to, subject, body):
    """
    Sends an email using credentials from environment variables.
    """
    sender_email = os.environ.get("EMAIL_ADDRESS")
    password = os.environ.get("EMAIL_PASSWORD")

    if not sender_email or not password:
        print("Error: EMAIL_ADDRESS or EMAIL_PASSWORD environment variables not set.")
        sys.exit(1)

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, password)
            server.send_message(msg)
            print(f"Email sent successfully to {to}.")
    except Exception as e:
        print(f"Error: Failed to send email. {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python send_email.py <to_address> <subject> \"<body>\"")
        sys.exit(1)
    
    to_address = sys.argv[1]
    subject = sys.argv[2]
    body = sys.argv[3]
    
    send_email(to_address, subject, body)