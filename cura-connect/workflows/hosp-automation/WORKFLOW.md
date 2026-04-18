# Workflow: HOSP Automation

## Overview
Processes unread HOSP emails from Socialstyrelsen automatically.
Run manually with `/hosp` or schedule via cron.

---

## First-time setup (do once)

### 1. Install Python dependencies
```bash
cd cura-connect/skills/hosp-automation
pip install -r requirements.txt
playwright install chromium
```

### 2. Create Google Cloud project
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. New Project → name it `cura-connect-automation`
3. APIs & Services → Enable APIs → search **Gmail API** → Enable
4. Credentials → Create Credentials → OAuth client ID
   - Configure consent screen if prompted: External, app name `HOSP Automation`
   - Application type: **Desktop app**, name: `hosp-automation`
5. Download the JSON → save to `~/.config/cura-connect/gcp-oauth.keys.json`

### 3. Run one-time Gmail OAuth flow
```bash
python3 cura-connect/skills/hosp-automation/scripts/oauth_flow.py
```
A browser window opens. Sign in as `max.nerdal@curaconnect.se` and grant access.
Token is saved to `~/.config/cura-connect/gmail-token.json`.

---

## Manual run
```bash
python3 cura-connect/skills/hosp-automation/scripts/hosp_processor.py
```
Or from Claude Code terminal: `/hosp`

---

## Schedule (run every morning at 08:00)

### macOS LaunchAgent
Create `~/Library/LaunchAgents/se.curaconnect.hosp.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>se.curaconnect.hosp</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>/Users/maxnerdal/Documents/max-ai-framework/cura-connect/skills/hosp-automation/scripts/hosp_processor.py</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>8</integer>
    <key>Minute</key>
    <integer>0</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>/Users/maxnerdal/Documents/max-ai-framework/cura-connect/skills/hosp-automation/hosp.log</string>
  <key>StandardErrorPath</key>
  <string>/Users/maxnerdal/Documents/max-ai-framework/cura-connect/skills/hosp-automation/hosp.log</string>
</dict>
</plist>
```

Load it:
```bash
launchctl load ~/Library/LaunchAgents/se.curaconnect.hosp.plist
```

---

## Monitoring
Logs are written to `cura-connect/skills/hosp-automation/hosp.log`.

Each entry shows: timestamp, email ID, extracted PIN + name, recman candidateId, fileId, read status.

Errors are logged without crashing — the script continues to the next email.

---

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| No portal URL in email | Logged as warning, email skipped (stays unread) |
| Portal blocks headless browser | Error logged, email skipped |
| Name not found in recman | Error logged, email skipped (stays unread for manual review) |
| Multiple recman candidates with same name | Warning logged, email skipped (resolve manually) |
| File upload fails | Error logged, email NOT marked as read (will retry next run) |
| Gmail token expired | Runtime error with instructions to re-run oauth_flow.py |
