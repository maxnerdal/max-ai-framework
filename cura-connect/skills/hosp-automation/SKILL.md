# Skill: hosp-automation

## What it does
Processes unread HOSP emails from `hosp@socialstyrelsen.se` in `max.nerdal@curaconnect.se`.

For each unread email:
1. Extracts the Socialstyrelsen portal URL from the email body
2. Opens the portal with headless Playwright, accepts the GDPR notice
3. Extracts personnummer and full name from `#contentContainer`
4. Captures the portal page as a real PDF using `page.pdf()` (Chrome's print-to-PDF)
5. Searches recman.io for the candidate by first + last name
6. Uploads the PDF to the candidate's file section
7. Marks the email as read

## Scripts

| File | Purpose |
|------|---------|
| `hosp_processor.py` | Main entry point — run this |
| `portal_scraper.py` | Playwright: navigate portal, extract data, capture PDF |
| `gmail_client.py` | Gmail API: list unread HOSP emails, mark as read |
| `recman_client.py` | recman API: find candidate, upload file |
| `oauth_flow.py` | One-time setup: Gmail OAuth2 consent + token save |

## Config keys (in `cura-connect/config.md`)
- `RECMAN_API_KEY` — recman API key
- `GMAIL_CREDENTIALS_PATH` — path to GCP OAuth JSON (~/.config/cura-connect/gcp-oauth.keys.json)
- `GMAIL_TOKEN_PATH` — path to saved Gmail token (~/.config/cura-connect/gmail-token.json)

## First-time setup
See `cura-connect/workflows/hosp-automation/WORKFLOW.md`.

## Dependencies
```
pip install -r requirements.txt
playwright install chromium
```
