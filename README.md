# max-ai-framework

Max Nerdal's personal AI framework. Shared library of skills, agents, commands, and workflows for Claude Code. Symlinks into `~/.claude/` so it's available globally.

## Structure

```
max-ai-framework/
  .claude/                 — Symlinked to ~/.claude/ (CLAUDE.md, agents, commands, rules, skills, settings)
    skills/                — Atomic capabilities (drive-reader-s, cv-tailorer-p, job-tracker-p, ...)
  workflows/               — Multi-step orchestrations (job-application-p, interview-prep-p, ...)
  prompts/                 — Shared writing principles (tailoring-principles-p.md, ...)
  templates/               — HTML templates (cv-p.html, letter-p.html, job-post-p.html)
  mcp-servers/gdrive-s/    — Custom Google Drive MCP server (Node)
  docs/                    — Setup guides + reference material
  .mcp.json[.example]      — MCP server configs
  config.example.md        — Drive IDs / OAuth paths template (config.md is gitignored)
  setup.sh                 — Creates ~/.claude/ symlinks on a new machine
```

**Suffix convention:** every skill, agent, command, workflow, prompt, and template is tagged by primary beneficiary so the framework can later be split per area without grepping. `-cc` Cura Connect, `-p` Personal, `-mn` Max Nerdal AB, `-s` Shared cross-area. See [CLAUDE.md](CLAUDE.md) for the full rule.

## Design principles

- **Shared library, not container** — skills/agents live here; project code lives in its own repo per app
- **App repos provide project context** — each app's CLAUDE.md `@imports` the relevant Obsidian area docs
- **Obsidian is the second brain** — business knowledge, brand, strategy, project state all in the vault
- **Logic lives in the repo, data doesn't** — personal files stay in Google Drive
- **Config bridges the two** — gitignored `config.md` holds API keys, Drive IDs, OAuth paths

## Getting started

See [docs/setup.md](docs/setup.md) for setup instructions.

For a dedicated always-on server setup, see [docs/server-setup.md](docs/server-setup.md).
