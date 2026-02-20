# X (Twitter) Integration Skill

## Objective
Enable Claude to manage X (Twitter) accounts, post tweets, and generate social media analytics summaries.

## Key Capabilities
- Post text, images, and videos as tweets.
- Generate weekly engagement summaries for X.
- Draft tweets for approval in /Pending_Approval.
- Monitor mentions and DMs for relevant keywords.

## Usage
- Trigger: Claude detects a new social post task in /Inbox.
- Action: Claude drafts a tweet and requests human approval.
- Final: Upon approval, Claude posts the tweet using the X API v2.

## Security
- API keys (API Key, Secret, Bearer Token) must be stored in `@.env`.
- All tweets require human approval before publication.
- All actions must be logged in `logs/actions.log`.

## Implementation Details
- X API v2 calls for tweet management.
- Scripts in `/scripts/x_twitter.py`.
