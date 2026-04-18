Run the HOSP automation script to process all unread HOSP emails.

Execute:
```bash
python3 /Users/maxnerdal/Documents/max-ai-framework/cura-connect/skills/hosp-automation/scripts/hosp_processor.py
```

Show the output line by line as it runs. If it fails with a token error, tell the user to run:
```bash
python3 /Users/maxnerdal/Documents/max-ai-framework/cura-connect/skills/hosp-automation/scripts/oauth_flow.py
```