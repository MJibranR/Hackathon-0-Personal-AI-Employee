# Skill: gmail-send

## Description
This skill sends an email using SMTP with credentials stored in environment variables. It is designed for sending real emails from a specified Gmail account.

## Usage
To send an email, provide the recipient's email address, the subject, and the body of the email.

### Command
```
python .claude/skills/gmail-send/scripts/send_email.py <to_address> <subject> "<body>"
```

## Requirements
- The environment variables `EMAIL_ADDRESS` and `EMAIL_PASSWORD` must be set.
- The script requires Python 3.10+
- The script is executed via a subprocess.

## Output
- On success, it prints a confirmation message: "Email sent successfully to [to_address]."
- On failure, it prints an error message.