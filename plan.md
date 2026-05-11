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

**Symlinks managed by `setup.sh`.** Symlinks `~/.claude/CLAUDE.md`, `~/.claude/agents/`, and `~/.claude/commands/` to the repo's copies so Claude Code picks them up globally. Claude Code's runtime files (`projects/`, `sessions/`, `mcp.json`, `settings.json`, …) stay in `~/.claude/` as real files — never enter the repo. Cowork scheduled tasks (`claude-cowork/Scheduled/`) are managed manually for now — copy in whatever you want version-controlled.

---

## setup.sh

Creates the per-subfolder `.claude/` symlinks on a new machine. Backs up any existing path before symlinking. Idempotent — safe to run multiple times.

See `setup.sh` at the repo root.

---

## Skills, agents, and workflows

Three layers, one mental model:

- **Skills** (`<context>/skills/`) — atomic capabilities. Referenced by both workflows and agents.
- **Agents** (`.claude/agents/`) — execution specs with isolated context windows and tool allowlists. Heavy work that reads a lot and returns a little. Invoked via `@name` or the Agent tool.
- **Workflows** (`<context>/workflows/`) — thin, user-facing orchestrations triggered by slash commands. Describe the user experience: steps, pauses, decision points.

A workflow can delegate to multiple agents (e.g. `/job-application` → `@application-drafter` → user review → `@application-finalizer`). Pipeline detail belongs in the agent file; user dialogue and decision points belong in the workflow file. The two should not duplicate each other.

## No sync needed

Skills and workflows are markdown files Claude reads as instructions — not a Claude Code system feature. They can be pointed to from `~/.claude/CLAUDE.md` and Claude will find them in any project without syncing:

> "Dev team skills and workflows live at `~/max-ai-framework/max-nerdal-ab/`. Read them when relevant."

**Agents are different.** Claude Code's `@agent-name` invocation is hardcoded to look in `~/.claude/agents/` and the project's `.claude/agents/`. A CLAUDE.md pointer cannot change this. Agents must be in one of those two places to be formally invoked as subagents.

**Practical split:**
- Skills and workflows → develop in context folders (`max-nerdal-ab/` etc.), reference via `~/.claude/CLAUDE.md`
- Agents → live flat in `.claude/agents/` for now. Per-context agent folders (with symlinks back into `.claude/agents/`) become worthwhile only when the framework grows past ~10 agents or a context needs to ship standalone — see TODOs.

---

## Open TODOs

- [ ] Test `setup.sh` — run on a clean machine or by temporarily removing symlink targets and re-running.
- [ ] Revisit per-context agent folders (`<context>/agents/` with symlinks into `.claude/agents/`) when the framework crosses ~10 agents, when a context needs to ship standalone, or when name collisions become real. Symlink plumbing already sketched.
