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

## Skills and workflows across projects (no sync needed)

Skills and workflows are markdown files Claude reads as instructions — not a Claude Code system feature. This means they can be pointed to from `~/.claude/CLAUDE.md` and Claude will find them in any project without syncing:

> "Dev team skills and workflows live at `~/max-ai-framework/max-nerdal-ab/`. Read them when relevant."

**Agents are different.** Claude Code's `@agent-name` invocation is hardcoded to look in `~/.claude/agents/` and the project's `.claude/agents/`. A CLAUDE.md pointer cannot change this. Agents must be in one of those two places to be formally invoked as subagents.

**Practical split:**
- Skills and workflows → develop in context folders (`max-nerdal-ab/` etc.), reference via `~/.claude/CLAUDE.md`
- Agents → live directly in `.claude/agents/`, already global, no sync needed

---

## Open TODOs

- [ ] Test `setup.sh` — run on a clean machine or by temporarily removing symlink targets and re-running.
- [ ] Fix paths in `.claude/agents/` — agents still reference old paths (e.g. `ai-framework/config.md`). Update to `max-ai-framework/personal/config.md` and any other stale references.
- [ ] Resolve `.mcp.json` location — currently at repo root. Decide whether it moves to `.claude/mcp.json` to make Drive MCP global, and update setup instructions accordingly.
- [ ] Discuss and clarify the definition of "agents" — there is a conceptual mismatch between Max's use of the word (autonomous pipelines / dev team roles built from skills) and Claude Code's use of the word (subagents in `.claude/agents/` with their own context window). Need to align on terminology before building out the dev team.
