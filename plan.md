# max-ai-framework — Framework Plan

## Purpose
A personal AI framework for Max Nerdal. Version-controlled source of truth for Claude Code configs, skills, agents, and workflows across personal and work contexts. Designed to be set up on any new machine quickly, and shareable with colleagues in the future.

---

## Structure decisions

**One repo, multiple contexts.** Each "hat" Max wears gets its own folder with its own CLAUDE.md, skills, and workflows:
- `personal/` — personal tasks (job applications, CV, Drive)
- `cura-connect/` — work automation for Cura Connect AB
- `max-nerdal-ab/` — consulting work
- `claude-cowork/Scheduled/` — Cowork scheduled task definitions

**Project code lives elsewhere.** Projects like `tradingbots` have their own repos. This framework only contains Claude configuration — not project code.

**CLAUDE.md hierarchy:**
- `.claude/CLAUDE.md` — global identity and preferences, loaded in every Claude Code session
- `<context>/CLAUDE.md` — loaded only when Claude Code is opened inside that folder
- Project `CLAUDE.md` — lives in the project's own repo, loaded when working there

**Symlink for Cowork scheduled tasks only.** `setup.sh` symlinks `~/Documents/Claude/Scheduled` → `repo/claude-cowork/Scheduled` so tasks created in the Cowork desktop app are automatically tracked in git. The `.claude/` folder is NOT symlinked — it is version-controlled here as a reference and manually synced to `~/.claude` when needed.

---

## setup.sh

Creates the Cowork scheduled tasks symlink on a new machine. Backs up any existing path before symlinking. Idempotent — safe to run multiple times.

See `setup.sh` at the repo root.

---

## Open TODOs

- [ ] Test `setup.sh` — run on a clean machine or by temporarily removing symlink targets and re-running.
- [ ] Fix paths in `.claude/agents/` — agents still reference old paths (e.g. `ai-framework/config.md`). Update to `max-ai-framework/personal/config.md` and any other stale references.
- [ ] Resolve `.mcp.json` location — currently at repo root. Decide whether it moves to `.claude/mcp.json` to make Drive MCP global, and update setup instructions accordingly.
