# max-ai-framework

## What this repo is
Max Nerdal's personal AI framework. Source of truth for Claude Code configs, skills, agents, workflows, and prompts across all contexts.

## Structure
- `.claude/` — Claude Code global config (symlinked to `~/.claude`)
- `personal/` — personal context: job applications, CV, Drive integration
- `cura-connect/` — work automation for Cura Connect AB
- `max-nerdal-ab/` — work context for Max Nerdal AB
- `claude-cowork/` — Cowork scheduled task definitions

## Using this repo
Each subfolder has its own CLAUDE.md. Open the relevant subfolder in Claude Code when working in that context.

The `.claude/` folder is symlinked to `~/.claude` so Claude Code picks it up globally. Run `setup.sh` on a new machine to create all symlinks.

## Key conventions
- Personal data lives in Google Drive — never in this repo
- Each context has a `config.md` (gitignored) with Drive IDs and credential paths
- `config.example.md` is the committed template for each context
