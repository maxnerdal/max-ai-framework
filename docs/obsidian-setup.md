# Obsidian Setup

The Obsidian vault is the AI's second brain — single source of truth for business context, projects, meeting notes, and daily thinking. This doc tracks what's done and what's next.

Based on the guide: [Obsidian Is My AI's Second Brain](references/obsidian-guide.pdf) by AI with Remy.

---

## Vault location
`/Users/maxnerdal/Documents/obsidian-vault/` — git-versioned separately from this framework.

## Layout
- `Areas/{Cura Connect, Max Nerdal AB, Personal}/` — per-area folders
  - `_context/` — canonical business docs (brand, ICP, operations)
  - `Projects/` — one `.md` per project, `status: active | paused | done`
  - `Notes/` — research and references
- `Daily logs/` — one note per day
- `Meeting Notes/` — meeting transcripts
- `Notes/` — evergreen reference (SOPs, cross-area knowledge)
- `_System/Templates/` — Templater templates

### Reference structure (from AI with Remy)

The canonical structure from the source guide:

```
Vault/
├── Areas/                       Business areas & clients
│   ├── AI with Remy/
│   │   ├── _context/            Brand voice, ICP, positioning, etc.
│   │   ├── Content/             All content, organised by type
│   │   │   ├── newsletters/
│   │   │   ├── youtube/
│   │   │   ├── articles/
│   │   │   └── reels/
│   │   ├── Notes/               Junk drawer (research, references, anything)
│   │   └── Projects/            Per-area project tracker
│   └── Client Name/             One folder per client
│       ├── _context/            Client business docs
│       ├── Notes/
│       └── Projects/
│
├── Daily logs/                  Daily notes + Backlog (pinned at top)
├── Meeting Notes/               Auto-synced from Granola
├── Notes/                       Evergreen reference notes
│
└── _System/
    ├── Templates/               Auto-applied templates
    └── attachments/
```

**Our adaptation:**
- Per-area folders are our actual contexts: `Cura Connect`, `Max Nerdal AB`, `Personal` (no `Client Name/` split — we have areas, not clients).
- No `Content/` subtree (we don't publish content yet).
- `Daily logs/` Backlog convention not yet adopted — see Next list.
- `Meeting Notes/` Granola sync not yet wired — see Next list.

### Our current structure

```
obsidian-vault/
├── Areas/                       Business & life contexts (1:1 with max-ai-framework subfolders)
│   ├── Cura Connect/            Active — populated
│   │   ├── _context/            About · BrandGuidelines · Glossary · ICP · Operations · Recman · Services · Values
│   │   ├── Projects/            AI-ramverk · AI-ramverk-arkitektur · AI-strategi
│   │   └── Notes/               Avtal/ (RS 2022-03983) · Ekonomi/ (Årsredovisning 2024-25)
│   ├── Max Nerdal AB/           Skeleton only — _context, Projects, Notes pending content
│   │   ├── _context/
│   │   ├── Projects/
│   │   └── Notes/
│   └── Personal/                Skeleton only — _context, Projects, Notes pending content
│       ├── _context/
│       ├── Projects/
│       └── Notes/
│
├── Daily logs/                  Empty — daily-note workflow pending (see Next)
├── Meeting Notes/               Empty — Granola sync pending (see Next)
├── Notes/                       Empty — evergreen cross-area reference
│
└── _System/
    ├── Templates/               Empty — Daily.md template pending
    └── attachments/             CuraConnect_logo.pdf
```

---

## Done

- [x] Vault structure created (Areas, Daily logs, Meeting Notes, Notes, _System)
- [x] Cura Connect `_context/` populated (About, BrandGuidelines, Glossary, ICP, Operations, Recman, Services, Values)
- [x] Global CLAUDE.md "Obsidian — Second Brain" section added
- [x] `.claude/rules/obsidian.md` created with vault location, layout, and 6-rule context loading policy
- [x] `setup.sh` symlinks `~/.claude/rules` → repo

---

## Next

### Populate the other Areas
- [ ] `Areas/Max Nerdal AB/_context/` — consulting brand, services, positioning
- [ ] `Areas/Personal/_context/` — CV summary, job-application context (mirror what's in `personal/`)

### Wire up `@imports` per area
Each context CLAUDE.md should pull in its `_context/` docs. See [claude-context-loading.md](claude-context-loading.md) for the full loading model.
- [x] `cura-connect/CLAUDE.md` — 8 `_context/` imports wired
- [ ] `max-nerdal-ab/CLAUDE.md` — placeholder added; pending `_context/` population
- [ ] `personal/CLAUDE.md` — placeholder added; pending `_context/` population

### Daily logs
- [ ] Templater plugin installed and configured
- [ ] Daily note template at `_System/Templates/Daily.md`
- [ ] Decide: morning-briefing automation (Claude reads calendar/email/recent notes, writes today's daily note before I open Obsidian)

### Meeting Notes
- [ ] Granola Sync Plus plugin installed
- [ ] Connect Granola → `Meeting Notes/`

### Obsidian CLI (Layer 2 — active search)
Currently Claude reads the vault via filesystem (Read/Grep/Glob). The Obsidian CLI adds vault-aware commands (daily notes, tags, backlinks, properties).
- [ ] Install: see https://help.obsidian.md/cli
- [ ] Update `.claude/rules/obsidian.md` — remove the "CLI not installed" line, add CLI usage rules

### QMD MCP (Layer 3 — semantic search, optional)
Vector search for fuzzy queries where keyword search misses. Only worth installing once the vault grows past ~hundreds of notes.
- [ ] Install: `npm install -g @tobilu/qmd`
- [ ] `qmd collection add ~/Documents/obsidian-vault --name obsidian && qmd embed`
- [ ] Add MCP server config to `~/.claude.json`
- [ ] LaunchAgent: `qmd update && qmd embed` twice daily
- [ ] Add CLI-vs-QMD routing rules to `.claude/rules/obsidian.md`

### Additional rule files
The `~/.claude/rules/` pattern scales. Future candidates:
- [ ] `telegram.md` — if a Telegram bot is set up
- [ ] `google-workspace.md` — Gmail / Calendar / Drive routing
- [ ] `cowork.md` — Cowork-specific behavior

---

## Notes
- Vault is its own git repo, separate from this framework. Sensitive business content stays in the vault repo; infrastructure stays here.
- The 1:1 mapping (`Areas/Cura Connect/` ↔ `cura-connect/`) is intentional — Claude can navigate between them.
