# Personal — Claude Context

## What this folder is
Max's personal Claude Code context. Primarily used for job applications: searching, applying, tracking, and preparing for interviews.

## Architecture
- `skills/` — atomic capabilities (cv-tailorer, job-tracker, drive-reader, etc.)
- `workflows/` — multi-step orchestration with human checkpoints
- `prompts/` — shared writing principles referenced by skills
- `templates/` — CV and letter HTML templates

Agents live in `../.claude/agents/` and commands in `../.claude/commands/` — they reference skills and workflows in this folder.

## Key conventions
- All personal data (CV, letters, applications) lives in Google Drive — never in this repo
- `config.md` holds Drive IDs and credential paths (gitignored)
- `config.example.md` is the committed template
- Skills are built using `/skill-creator`

## Local setup
- Google Drive MCP configured in: `~/.claude/mcp.json`
- OAuth client keys: `~/.config/claude/gcp-oauth.keys.json`
- OAuth tokens: `~/.config/claude/.gdrive-server-credentials.json`
- Config with personal Drive IDs: `config.md` (gitignored)
- Sheets API script: `skills/job-tracker/scripts/sheets.py`
