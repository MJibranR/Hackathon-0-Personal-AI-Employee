# Skill: linkedin-post

## Description
This skill uses Playwright to automate logging into LinkedIn and creating a new text post. It requires LinkedIn credentials to be set as environment variables.

## Usage
To create a LinkedIn post, provide the content of the post as an argument.

### Command
```
python .claude/skills/linkedin-post/scripts/post_linkedin.py "<post_content>"
```

## Requirements
- The environment variables `LINKEDIN_EMAIL` and `LINKEDIN_PASSWORD` must be set.
- Playwright must be installed (`pip install playwright` and `playwright install`).
- The script requires Python 3.10+.

## Output
- On success, it prints: "LinkedIn post created successfully."
- On failure, it prints an error message.