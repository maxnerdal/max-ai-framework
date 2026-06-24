# How Claude Code Loads Context

This doc explains *what* Claude knows about when you start a session, and *why*. Use it to keep global config lean and per-app sessions rich.

---

## The four loading rules

1. **`CLAUDE.md` walks up, not down.** Claude reads `CLAUDE.md` from the CWD, then walks upward to parents and home. It does **not** descend into subfolders.
2. **`~/.claude/` is global.** Anything there (`CLAUDE.md`, `rules/*.md`, `agents/`, `commands/`, `skills/`) loads in every session, regardless of CWD.
3. **Project `.claude/` overlays the global one.** Claude looks for a single project `.claude/` walking up from CWD. Intermediate `.claude/` directories along the path are **not** merged — only the closest one + `~/.claude/`.
4. **`@imports` in CLAUDE.md pull other files into context eagerly.** Use them to load adjacent docs (e.g. Obsidian vault context) without waiting for Claude to search.

`~/.claude/rules/*.md` is auto-loaded globally — convention-based, no `@import` needed. Use it for cross-context rules (e.g. how to use the Obsidian vault).

---

## The layout

```
~/
├── .claude/
│   ├── CLAUDE.md  ──────────► symlink → max-ai-framework/.claude/CLAUDE.md
│   ├── agents/    ──────────► symlink → max-ai-framework/.claude/agents/
│   ├── commands/  ──────────► symlink → max-ai-framework/.claude/commands/
│   └── rules/     ──────────► symlink → max-ai-framework/.claude/rules/
│       └── obsidian.md         (auto-loaded global rule)
│
└── Documents/
    ├── max-ai-framework/         (shared toolkit — no app code)
    │   ├── CLAUDE.md             (framework map)
    │   ├── .claude/              (global config, symlinked above)
    │   │   └── skills/           (cv-tailorer, drive-reader, job-tracker, ...)
    │   ├── workflows/            (job-application, interview-prep, ...)
    │   ├── prompts/, templates/, mcp-servers/
    │   └── docs/
    │
    ├── hosp-automation/          (app repo — Cura HOSP cert automation)
    │   ├── CLAUDE.md             (Cura @imports for this pipeline)
    │   └── scripts/, SKILL.md, WORKFLOW.md, ...
    │
    ├── tradingbots/              (app repo — own CLAUDE.md)
    │
    └── obsidian-vault/           (second brain)
        └── Areas/
            ├── Cura Connect/_context/      (imported by hosp-automation CLAUDE.md)
            ├── Max Nerdal AB/_context/     (imported by future MNAB app repos)
            └── Personal/_context/          (imported by personal-side workflows)
```

---

## What loads when

### Start in `~/Documents/max-ai-framework/` (the toolkit itself)
```
~/.claude/CLAUDE.md                      ← global "who I am"
~/.claude/rules/obsidian.md              ← vault location + search rules
max-ai-framework/CLAUDE.md               ← framework map
```
**Claude knows:** Max's identity, the framework structure, the vault exists, all global skills/agents/commands.

### Start in `~/Documents/hosp-automation/` (the Cura HOSP automation app)
```
~/.claude/CLAUDE.md                      ← global "who I am"
~/.claude/rules/obsidian.md              ← vault location + search rules
hosp-automation/CLAUDE.md                ← app context
  └── @ vault/Areas/Cura Connect/_context/Operations.md
  └── @ vault/Areas/Cura Connect/_context/Recman.md
  └── @ vault/Areas/Cura Connect/Projects/.../curaconnect-ai-framework-IVO-HOSP.md
+ hosp-automation/.claude/commands/hosp.md  (the /hosp slash command)
```
**Claude knows:** all of the above, plus the HOSP pipeline's specific context and the `/hosp` command, plus all global skills/agents/commands from `~/.claude/`.

### Start in any new app repo
Same pattern: write a `CLAUDE.md` in the app repo root with `@imports` pulling the relevant Obsidian area context. Global tools come for free.

---

## Practical rules of thumb

- **Lean global, rich apps.** Global `~/.claude/CLAUDE.md` + `rules/` is small — it loads every session. Per-app CLAUDE.md carries the heavy `@imports` for that app's domain.
- **`@import` only the canonical and stable.** `_context/` files = yes. `Projects/` and `Notes/` = no — they change too often and are large; let Claude read them on demand via the vault rules.
- **Start Claude in the app's repo, not in the framework.** Working on hosp-automation? `cd ~/Documents/hosp-automation && claude`. Working on the toolkit itself? `cd ~/Documents/max-ai-framework && claude`.
- **Need cross-area context once?** Just ask ("read Cura Connect's ICP"). It costs a turn but doesn't pollute every session.
- **Daily notes and Project.md files are read on-demand**, never `@imported`. The obsidian rules teach Claude where they live and *when* to look (e.g. when you mention "today" or reference a project). Generic prompts unrelated to projects/areas/time don't trigger a vault dive.
- **Backlog files (`Areas/*/Notes/Backlog.md`) are read on-demand by `/morning`** and when the user asks about scheduling. Not auto-loaded.

## Why no area folders inside the framework?
Earlier versions had `personal/`, `cura-connect/`, `max-nerdal-ab/` subfolders each with their own CLAUDE.md and skills. That was reverted on 2026-06-11 — Claude Code doesn't merge intermediate `.claude/` directories along the walk-up path, so per-area tools at `<area>/.claude/skills/` wouldn't have been discovered from a deeper CWD anyway. The canonical pattern is `~/.claude/` + per-app `CLAUDE.md`. See vault `[[max-ai-framework-flatten]]` for the full reasoning.

## Wiring status

Tracked in the vault: `Areas/Max Nerdal AB/Projects/max-ai-framework/max-ai-framework-obsidian.md`.
