# max-ai-framework

## What this repo is
Max Nerdal's personal AI framework. Source of truth for Claude Code's shared library: skills, agents, commands, workflows, prompts, templates, and MCP servers. Symlinks into `~/.claude/` so the toolkit is available globally.

## Structure (flat shared library)
- `.claude/` — symlinked to `~/.claude/`. Holds the global identity (`CLAUDE.md`), `agents/`, `commands/`, `rules/`, `settings.json`.
- `skills/` — atomic capabilities (cv-tailorer, drive-reader, job-tracker, ...)
- `workflows/` — multi-step orchestrations with human checkpoints (job-application, interview-prep, update-application)
- `prompts/` — shared writing principles referenced by skills
- `templates/` — HTML templates for output documents (CV, letters, job posts)
- `mcp-servers/gdrive/` — custom Google Drive MCP server (Node)
- `docs/` — setup guides and reference material
- `.mcp.json`, `.mcp.json.example` — project-scoped MCP configs
- `config.md` (gitignored), `config.example.md` — Drive IDs, OAuth paths

## Pattern: build apps in their own repos
Project code does not live here. Each app — `tradingbots`, `hosp-automation`, future portfolio site, future Cura ai-framework — is its own repo with its own `CLAUDE.md` that `@imports` the relevant Obsidian area docs. This framework provides the shared toolkit; app repos provide the project context.

The Obsidian vault at `~/Documents/obsidian-vault/` is the source of truth for business knowledge per area (Cura Connect / Max Nerdal AB / Personal). App repos load that context via `@~/Documents/obsidian-vault/Areas/{area}/_context/...` imports.

## Setup
`setup.sh` symlinks `.claude/{CLAUDE.md,agents,commands,rules}` into `~/.claude/`. Run once on a new machine.

## Key conventions
- Skills are portable (no Claude-Code-specific assumptions); agents are Claude-Code-specific.
- Sensitive data (Drive IDs, API keys, OAuth tokens) lives in gitignored `config.md` files or `~/.config/...` — never committed.
- No em dashes in code or AI-generated content.
