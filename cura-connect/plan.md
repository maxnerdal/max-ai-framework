# Cura Connect Automation — Plan

## What this folder is
Work automation for Cura Connect (`curaconnect.se`).
Separate from `../` (Max's personal framework) but follows the same three-layer architecture.

## Architecture
```
cura-connect/
  skills/             — atomic capabilities
  workflows/          — orchestration with setup instructions
  .claude/commands/   — slash command entry points
  config.md           — gitignored: API keys, credential paths
  config.example.md   — committed template
```

## Current workflows

### hosp-automation (v1 — active)
Processes unread HOSP emails from `hosp@socialstyrelsen.se` in `max.nerdal@curaconnect.se`.

**Stack:** Python + Playwright (headless Chromium) + Gmail API + recman API

**Steps per email:**
1. Gmail API → list unread from hosp@socialstyrelsen.se
2. Extract Socialstyrelsen portal URL from email body
3. Playwright → navigate portal, accept GDPR, extract PIN + name from #contentContainer
4. `page.pdf()` → real, text-selectable PDF (Chrome's print-to-PDF engine)
5. recman API → find candidate by firstName + lastName
6. recman API → upload PDF to candidate's file section (scope=candidate, operation=insert)
7. Gmail API → mark email as read

**Known limitations (v1):**
- Candidate lookup is by name only (recman API has no personnummer filter)
  → Multiple candidates with identical names require manual resolution
- No "Kurs/certifiering" entry created — file goes to general candidate files
  (recman API scope for courses not found; may require recman support contact)

**Schedule:** macOS LaunchAgent at 08:00 daily (see WORKFLOW.md)

## Setup status
- [ ] GCP project created + Gmail API enabled
- [ ] OAuth credentials JSON downloaded to ~/.config/cura-connect/gcp-oauth.keys.json
- [ ] oauth_flow.py run (Gmail token saved)
- [ ] Dependencies installed (pip install -r requirements.txt + playwright install chromium)
- [ ] Tested end-to-end on one email
- [ ] LaunchAgent loaded for daily schedule
