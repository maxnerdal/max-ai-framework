# ai-framework — Claude Context

## What this repo is
A personal AI framework for Max Nerdal. Contains skills, agents, workflows, and prompts that let Claude work autonomously on personal and professional tasks — primarily job applications for now.

## Read this first
Before doing anything, read the full plan:
👉 `plan.md`

It contains the architecture, build order, design decisions, and v2 roadmap.

## Current status
All skills written. Next step: build agents (`.claude/agents/`), then workflows and commands.

## Architecture (three-layer pattern)
- `skills/` — atomic capabilities (portable across Claude, Gemini, OpenAI)
- `.claude/agents/` — autonomous pipelines as Claude Code subagents (own context window)
- `workflows/` — multi-step orchestration with human checkpoints (portable, LLM-agnostic)
- `.claude/commands/` — thin slash command wrappers that invoke workflows (Claude Code specific)
- `prompts/` — shared writing principles referenced by skills (portable)

## Key conventions
- All personal data lives in Google Drive — never in this repo
- `config.md` holds all Drive IDs and local credential paths (gitignored)
- `config.example.md` is the committed template
- Skills are built using `/skill-creator` plugin
- Slash commands live in `.claude/commands/` and point to `workflows/*/WORKFLOW.md`
- Agents live in `.claude/agents/` — Claude Code subagents with their own context window

## Local setup
- Google Drive MCP configured in: `~/.claude/mcp.json`
- OAuth client keys: `~/.config/claude/gcp-oauth.keys.json`
- OAuth tokens: `~/.config/claude/.gdrive-server-credentials.json`
- Config with personal Drive IDs: `config.md` (gitignored)
- Sheets API script (no dependencies): `skills/job-tracker/scripts/sheets.py`

## User
Max Nerdal — Swedish developer, building this framework for personal use. Working directory: `/Users/maxnerdal/Documents/ai-framework/`
