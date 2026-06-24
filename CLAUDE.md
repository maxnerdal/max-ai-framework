# max-ai-framework

## What this repo is
Max Nerdal's personal AI framework. Source of truth for Claude Code's shared library: skills, agents, commands, workflows, prompts, templates, and MCP servers. Symlinks into `~/.claude/` so the toolkit is available globally.

## Structure (flat shared library)
- `.claude/` — symlinked to `~/.claude/`. Holds the global identity (`CLAUDE.md`), `agents/`, `commands/`, `rules/`, `skills/`, `settings.json`. Agents follow the same area-suffix convention: `application-drafter-p.md`, `application-finalizer-p.md`, `interview-preparer-p.md`. Commands: `morning-s.md`, `sweep-s.md`, `job-application-p.md`, `interview-prep-p.md`, `update-application-p.md`.
- `.claude/skills/` — atomic capabilities, each as `<name>/SKILL.md` with frontmatter. Shared: `drive-reader-s/`, `drive-writer-s/`. Personal: `cv-tailorer-p/`, `interview-prepper-p/`, `job-post-parser-p/`, `job-searcher-p/`, `job-tracker-p/`, `personal-letter-writer-p/`, `screening-answerer-p/`. Auto-discoverable across projects via the `~/.claude/skills/` symlink.
- `workflows/` — multi-step orchestrations. `job-application-p/`, `interview-prep-p/`, `update-application-p/`.
- `prompts/` — shared writing principles. `drive-output-conventions-p.md`, `source-material-loader-p.md`, `tailoring-principles-p.md`.
- `templates/` — HTML templates. `cv-p.html`, `letter-p.html`, `job-post-p.html`.
- `mcp-servers/gdrive-s/` — custom Google Drive MCP server (Node).
- `docs/` — setup guides and reference material.
- `.mcp.json`, `.mcp.json.example` — project-scoped MCP configs.
- `config.md` (gitignored), `config.example.md` — Drive IDs, OAuth paths.

## Pattern: build apps in their own repos
Project code does not live here. Each app — `tradingbots`, `hosp-automation`, future portfolio site, future Cura ai-framework — is its own repo with its own `CLAUDE.md` that `@imports` the relevant Obsidian area docs. This framework provides the shared toolkit; app repos provide the project context.

The Obsidian vault at `~/Documents/obsidian-vault/` is the source of truth for business knowledge per area (Cura Connect / Max Nerdal AB / Personal). App repos load that context via `@~/Documents/obsidian-vault/Areas/{area}/_context/...` imports.

## Setup
`setup.sh` symlinks `.claude/{CLAUDE.md,agents,commands,rules}` into `~/.claude/`. Run once on a new machine.

## Key conventions
- Skills are portable (no Claude-Code-specific assumptions); agents are Claude-Code-specific.
- Sensitive data (Drive IDs, API keys, OAuth tokens) lives in gitignored `config.md` files or `~/.config/...` — never committed.
- No em dashes in code or AI-generated content.

## Naming convention — area suffixes
Every skill, agent, command, workflow, and prompt is tagged by its primary beneficiary so the framework can later be split per area without grepping. Suffix goes on the filename (and on the containing folder for skills):

| Area | Suffix | Examples |
|---|---|---|
| Cura Connect | `-cc` | `recman-uploader-cc/`, `hosp-cert-checker-cc.md` |
| Personal | `-p` | `cv-tailorer-p/`, `job-application-p.md` |
| Max Nerdal AB | `-mn` | `consulting-proposal-writer-mn/` |
| Shared (cross-area) | `-s` | `morning-s.md`, `sweep-s.md`, `drive-reader-s/` |

The suffix carries through to invocation: a slash command file at `.claude/commands/job-application-p.md` is invoked as `/job-application-p`; an agent file at `.claude/agents/application-drafter-p.md` is invoked as `@application-drafter-p`. Cross-references inside skills/workflows/agents must use the suffixed names.

When in doubt about classification, default to `-s` (shared). Promote to a specific area when a tool grows hard dependencies on that area's data sources, credentials, or conventions.
