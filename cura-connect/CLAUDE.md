# Cura Connect — Claude Context

## What this folder is
Work automation for Cura Connect AB (`curaconnect.se`). Follows the same three-layer architecture as the parent framework.

## Architecture
- `skills/` — atomic capabilities
- `workflows/` — orchestration with setup instructions
- `.claude/commands/` — slash command entry points
- `config.md` — gitignored: API keys, credential paths
- `config.example.md` — committed template

## Active workflow: hosp-automation

Processes unread HOSP emails from `hosp@socialstyrelsen.se` in `max.nerdal@curaconnect.se`.

**Stack:** Python + Playwright (headless Chromium) + Gmail API + recman API  
**Entry point:** `.claude/commands/hosp.md` → `/hosp`  
**Python venv:** `skills/hosp-automation/.venv/` — always run with `.venv/bin/python3`

**Pipeline per email:**
1. Gmail API → list unread from hosp@socialstyrelsen.se
2. Extract Socialstyrelsen portal URL from email body
3. Playwright → navigate portal, accept GDPR, extract PIN + name
4. `page.pdf()` → real, text-selectable PDF
5. recman API → find candidate by firstName + lastName
6. recman API → upload PDF to candidate file section
7. Gmail API → mark email as read

**Known limitations:**
- Candidate lookup is name-only — duplicate names require manual resolution
- PDFs saved to `skills/hosp-automation/pending/` before upload; retry logic handles failures on next run
- LaunchAgent (daily schedule) not yet set up — waiting for test email to verify end-to-end

## Key config values (in config.md)
- `RECMAN_API_KEY` — recman.io API key
- Gmail OAuth token: `~/.config/cura-connect/.gdrive-server-credentials.json`
