# Meta Social Integration Skill (Facebook/Instagram)

## Objective
Enable Claude to manage social media accounts on Facebook and Instagram, post updates, and generate performance summaries.

## Key Capabilities
- Post text, image, and video updates to Facebook and Instagram.
- Generate weekly engagement summaries.
- Schedule drafts for approval.
- Monitor comments for keywords (e.g., "Pricing," "Help").

## Usage
- Trigger: Claude detects a new project milestone in /Done.
- Action: Claude creates a draft social post in /Pending_Approval.
- Final: Upon approval, Claude posts to Facebook/Instagram.

## Security
- API access tokens must be stored in `@.env`.
- All posts require human approval before publication.
- All actions must be logged in `logs/actions.log`.

## Implementation Details
- Meta Graph API calls to Facebook/Instagram accounts.
- Scripts in `/scripts/meta_social.py`.
