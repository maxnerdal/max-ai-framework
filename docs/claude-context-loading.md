# How Claude Code Loads Context

This doc explains *what* Claude knows about when you start a session, and *why*. It's the map for keeping global config lean and area sessions rich.

---

## The three loading rules

1. **Walks up, not down.** Claude loads `CLAUDE.md` from the current working directory, then walks upward to parents and home. It does **not** descend into subfolders.
2. **`~/.claude/` is global.** Anything there loads in every session, regardless of CWD.
3. **`@imports` pull other files into context eagerly.** Use them in a `CLAUDE.md` to load adjacent docs (e.g. vault context) without waiting for Claude to search.

There's a fourth, less-documented behavior worth knowing:

4. **`~/.claude/rules/*.md` is auto-loaded globally.** Files in this folder act like extensions of the global `CLAUDE.md` — convention-based, no `@import` needed. Use it for cross-context rules (e.g. how to use the Obsidian vault).

---

## The layout

```
~/
├── .claude/
│   ├── CLAUDE.md  ──────────► symlink → max-ai-framework/.claude/CLAUDE.md
│   └── rules/    ──────────► symlink → max-ai-framework/.claude/rules/
│       └── obsidian.md         (auto-loaded global rule)
│
└── Documents/
    ├── max-ai-framework/
    │   ├── CLAUDE.md              (project root — framework map)
    │   ├── .claude/
    │   │   ├── CLAUDE.md          (global "who I am")
    │   │   └── rules/
    │   │       └── obsidian.md
    │   ├── cura-connect/
    │   │   └── CLAUDE.md          (area + @imports to vault)
    │   ├── personal/
    │   │   └── CLAUDE.md          (area — imports pending)
    │   └── max-nerdal-ab/
    │       └── CLAUDE.md          (area — imports pending)
    │
    └── obsidian-vault/
        └── Areas/
            ├── Cura Connect/
            │   ├── _context/      ──► imported by cura-connect/CLAUDE.md
            │   ├── Projects/         (read on demand)
            │   └── Notes/            (read on demand)
            ├── Personal/
            │   └── _context/         (not yet populated)
            └── Max Nerdal AB/
                └── _context/         (not yet populated)
```

---

## What loads when

### Start in `~/Documents/max-ai-framework/` (root)
```
~/.claude/CLAUDE.md                      ← global "who I am"
~/.claude/rules/obsidian.md              ← vault location + search rules
max-ai-framework/CLAUDE.md               ← framework map
```
**Claude knows:** Max's identity, the framework structure, the vault exists.
**Claude does *not* know:** Cura Connect's brand voice, ICP, services. Has to search the vault to find them.

### Start in `~/Documents/max-ai-framework/cura-connect/`
```
~/.claude/CLAUDE.md                      ← global "who I am"
~/.claude/rules/obsidian.md              ← vault location + search rules
max-ai-framework/CLAUDE.md               ← framework map (walked up)
cura-connect/CLAUDE.md                   ← area context
  └── @ vault/Areas/Cura Connect/_context/About.md
  └── @ vault/Areas/Cura Connect/_context/BrandGuidelines.md
  └── @ vault/Areas/Cura Connect/_context/Glossary.md
  └── @ vault/Areas/Cura Connect/_context/ICP.md
  └── @ vault/Areas/Cura Connect/_context/Operations.md
  └── @ vault/Areas/Cura Connect/_context/Recman.md
  └── @ vault/Areas/Cura Connect/_context/Services.md
  └── @ vault/Areas/Cura Connect/_context/Values.md
```
**Claude knows:** all of the above, plus full Cura Connect business context.

---

## Practical rules of thumb

- **Lean global, rich areas.** Global (`~/.claude/CLAUDE.md` + `rules/`) should be small — it loads every session. Area folders carry the heavy `@imports`.
- **`@import` only the canonical and stable.** `_context/` files = yes. `Projects/` and `Notes/` = no (they change too often and are large; let Claude read them on demand via the vault rules).
- **Start Claude in the right folder.** Personal job apps → `personal/`. Cura work → `cura-connect/`. Framework changes → root.
- **Need cross-area context once?** Just ask ("read Cura Connect's ICP"). It costs a turn but doesn't pollute every session.

## Wiring status

| Area | `_context/` populated? | `@imports` wired? |
|---|---|---|
| Cura Connect | Yes (8 docs) | Yes |
| Personal | No | Pending |
| Max Nerdal AB | No | Pending |

Update this table as the other areas come online.
