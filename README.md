# max-ai-framework

*[English](README.md) · [Svenska](README.sv.md)*

Max Nerdal's personal AI framework for Claude Code. A shared toolkit of skills, agents, slash commands, workflows, prompts, templates, and MCP servers that turn Claude Code from a generic assistant into a context-aware collaborator across two businesses (Cura Connect AB, Max Nerdal AB) and personal life.

This repo is the source of truth. It symlinks into `~/.claude/` so every project on the machine sees the same toolkit and the same identity, regardless of which directory Claude Code is launched from.

## Why this exists

A stock Claude Code install starts every conversation cold. It has no idea who you are, what you work on, what your standards are, or where to find the documents it needs. You end up re-explaining the same context every session and re-building the same automations in every repo.

This framework fixes that by pushing four things upstream:

1. **Identity, once, globally.** A single top-level `CLAUDE.md` describes who I am, what I run, and how my knowledge is structured, so any Claude Code session in any directory starts with the right assumptions.
2. **Business knowledge in an Obsidian vault.** Business docs, brand voice, project state, and decision logs live in a second-brain vault. The framework tells Claude how to discover and load context from it on demand instead of hard-coding it.
3. **Reusable capabilities as skills, agents, commands, workflows.** Anything I would otherwise re-write as a one-off prompt lives here as a versioned artifact.
4. **External systems as MCP integrations.** Google Drive, Gmail, Calendar, and Google Tasks are wired in so Claude can read/write real state, not just chat about it.

The rest of this README walks through each of those layers: what it does, why, and where to find it.

## The layers

### Layer 1: Global identity (`.claude/CLAUDE.md`)

**What:** The top-level system prompt that loads into every Claude Code session on this machine. Introduces me, the businesses, the vault, general preferences (concise responses, no emojis, no unnecessary comments), Gmail/Calendar account routing, and the area-suffix convention that everything else in the framework follows.

**Why:** Without this, every new project directory would need its own bootstrap and Claude would ask the same setup questions forever. With it, I can `cd` into any repo (even one I created five minutes ago) and Claude already knows the setup.

**Where:** `.claude/CLAUDE.md` in this repo, symlinked to `~/.claude/CLAUDE.md`.

### Layer 2: Obsidian second brain

**What:** An Obsidian vault at `~/Documents/obsidian-vault/` holds everything that changes over time and does not belong in code:

- **Business context per area** in `Areas/{Cura Connect, Max Nerdal AB, Personal}/_context/` (brand voice, ICP, operations). Static, canonical.
- **Every project I run**, one anchor file per project in `Areas/{area}/Projects/<Name>.md`, with `status: active | paused | done` frontmatter, a description, the full plan checklist, and a decisions log. Supporting docs live beside the anchor (`<Name>-architecture.md`, `<Name>-flatten.md`, etc.). Projects that outgrow ~3 files are promoted to a folder with `Index.md` as anchor.
- **Daily logs** in `Daily logs/YYYY-MM-DD.md` capturing today's slice of project work as `[[wikilinks]]`, thoughts, ideas.
- **Ideas** routed to one of three lifecycle homes: today's `## Ideas` section (fresh), a project anchor (tied to active work), or `Areas/{area}/Notes/` (evergreen).
- **Meeting notes**, evergreen SOPs, cross-area reference material.

**Why (the real payoff):** The vault turns "which project are we talking about?" into a cheap lookup, not a long question-and-answer round. When I say "let's continue on the framework refactor" or drop a `[[max-ai-framework-flatten]]` wikilink, Claude reads one small anchor file and immediately knows: what the project is, what's been done, what's next on the checklist, what decisions were made and why, what architecture supporting docs exist. No re-briefing me, no re-explaining, no burning tokens on context reconstruction. The status frontmatter also means "what am I working on right now?" is a single glob for `status: active` across all areas.

Code repositories are a bad place to hold this. They get stale, they mix code with plans, they scatter one project's context across multiple repos, and they don't cross-link. The vault sits above the repos and is the single source of truth for *what is currently true about the work*.

**How Claude finds it:** `.claude/rules/obsidian.md` teaches Claude when to trigger vault reads (project questions, "what am I working on today", named projects, `[[wikilinks]]`) and when not to (generic coding questions, tool usage, system setup). Read-passively vs. read-conditionally is spelled out per section so the vault is not scanned for every prompt. A coupling rule ensures that editing a project anchor also checks its supporting docs for mirror updates.

**Where:** Vault is outside this repo (personal data). Loading rules: `.claude/rules/obsidian.md`.

### Layer 3: MCP integrations

**What:** Model Context Protocol servers that give Claude Code real read/write access to external systems.

- **`workspace-mcp`** (registered user-scope via `claude mcp add -s user`): Google Drive, Gmail, Calendar, Google Tasks, Docs, Sheets, Slides, Forms, Contacts. Multi-account by design: every tool call takes a `user_google_email` argument, so the same server routes to `maxnerdal@gmail.com` or `max.nerdal@curaconnect.se` per call. One server, both inboxes, both Drives, both Task lists.

**Why:** Claude only being able to "read files" is a hard limit. With MCP, morning briefings can pull unread mail and today's calendar. Backlog items land in Google Tasks. State lives where I already look at it (Gmail, Calendar, Drive, Tasks app), not in a Claude-only sandbox.

**Where:** `.mcp.json.example` shows the project-scope registration pattern for any repo that wants to bundle its own MCP servers. Setup: `docs/google-workspace-mcp-setup.md`, `docs/server-setup.md`.

### Layer 4: Skills (`.claude/skills/*/SKILL.md`)

**What:** Atomic, portable capabilities. Each skill is a folder with a `SKILL.md` frontmatter file that Claude auto-discovers and invokes when the description matches the task.

Current skills:

- **Shared (`-s`):**
  - `drive-reader-s/` reads Drive files by name or ID (CVs, letters, references, past applications).
  - `drive-writer-s/` writes finalized documents to Drive with the `application-YYYYMMDD-company-role` folder convention.
- **Personal (`-p`):**
  - `job-post-parser-p/` parses a URL or pasted ad into a structured job object, archives the post.
  - `job-tracker-p/` reads/writes the job application tracker Google Sheet.
  - `job-searcher-p/` searches the web for jobs matching my profile, filters duplicates.
  - `cv-tailorer-p/` suggests targeted CV edits per job.
  - `personal-letter-writer-p/` drafts tailored cover letters in my voice.
  - `screening-answerer-p/` handles application form screening questions.
  - `interview-prepper-p/` generates likely interview questions and company research.

**Why:** Skills stay small and single-purpose so they compose. They are portable (no Claude-Code-specific assumptions) so they can be reused in other harnesses later.

**Where:** `.claude/skills/`, symlinked to `~/.claude/skills/` for global discovery.

### Layer 5: Agents (`.claude/agents/*.md`)

**What:** Claude-Code-specific sub-agents that run their own tool loop with a scoped tool allowlist. Used for the parts of a workflow that benefit from isolation or a narrower toolset.

- `application-drafter-p.md` runs the full drafting pipeline for a job application (parse post, load CV + letter, propose changes) and stops before writing anything, so the user can review.
- `application-finalizer-p.md` executes the approved changes: copies source docs into a new folder, applies edits, updates the tracker.
- `interview-preparer-p.md` runs the interview-prep flow end-to-end.

**Why:** Some jobs are messy enough that they deserve their own conversation. Agents keep the main chat clean and let me scope tools tightly (an agent doing web research does not also need edit access to my vault).

**Where:** `.claude/agents/`, symlinked to `~/.claude/agents/`.

### Layer 6: Slash commands (`.claude/commands/*.md`)

**What:** User-triggered entry points invoked as `/name`.

- `/morning-s` builds today's morning briefing in the Obsidian daily note (calendar, unread mail digest, due tasks per area).
- `/sweep-s` end-of-day closer that syncs briefing check-marks with Google Tasks bidirectionally.
- `/job-application-p` runs the job application workflow.
- `/interview-prep-p` runs interview prep for a job in the tracker.
- `/update-application-p` updates a submitted application (fixes, follow-ups).

**Why:** Slash commands are the shortest path from "I want X" to Claude doing X. Two-letter suffixes prevent accidental cross-area triggers (a Cura-specific command should not fire during personal work and vice versa).

**Where:** `.claude/commands/`, symlinked to `~/.claude/commands/`.

### Layer 7: Workflows (`workflows/<name>/WORKFLOW.md`)

**What:** Multi-step orchestrations that combine skills and agents into a full pipeline. Currently: `job-application-p/`, `interview-prep-p/`, `update-application-p/`.

**Why:** Skills answer "what can I do?", workflows answer "how do these pieces fit together for this end-to-end job?". Splitting them keeps the atomic skills reusable while the workflow captures the specific sequencing for one use case.

**Where:** `workflows/` at repo root.

### Layer 8: Prompts and templates

**What:**
- `prompts/` shared writing conventions applied across skills: `tailoring-principles-p.md`, `source-material-loader-p.md`, `drive-output-conventions-p.md`.
- `templates/` HTML scaffolds for finalized artifacts: `cv-p.html`, `letter-p.html`, `job-post-p.html`.

**Why:** Two skills that both write to Drive should not disagree on formatting. Two skills that both tailor content should not have their own conflicting notion of "how honest" tailoring is allowed to be. Centralizing these in `prompts/` and `templates/` means changing tone or format once propagates everywhere.

**Where:** `prompts/`, `templates/`.

## How global access works

Every layer above needs to be reachable from any directory on the machine, not just from inside this repo. There are three separate mechanisms in play:

**1. Symlinks into `~/.claude/`.** `setup.sh` links the repo-controlled parts of the framework into the user-scope Claude Code config directory that every session reads on startup:

```
~/.claude/CLAUDE.md   ->  ~/Documents/max-ai-framework/.claude/CLAUDE.md
~/.claude/agents      ->  ~/Documents/max-ai-framework/.claude/agents
~/.claude/commands    ->  ~/Documents/max-ai-framework/.claude/commands
~/.claude/rules       ->  ~/Documents/max-ai-framework/.claude/rules
~/.claude/skills      ->  ~/Documents/max-ai-framework/.claude/skills
```

This is why `/morning-s`, `@application-drafter-p`, and every skill are available whether Claude Code is started in `~/Documents/hosp-automation/`, in a scratch folder, or anywhere else. The whole `~/.claude/` directory is not symlinked (Claude Code writes runtime state there that does not belong in the repo). Only the five paths above are linked in.

**2. Indirect reference for workflows.** Workflow folders live at `workflows/*/WORKFLOW.md` in this repo and are *not* symlinked. Instead, each slash command that owns a workflow contains a one-liner like *"Read and execute the workflow at `workflows/job-application-p/WORKFLOW.md`"*. Because the global `CLAUDE.md` tells Claude that the framework lives at `~/Documents/max-ai-framework/`, that relative path is resolved against the repo root and the file is read directly. Workflows are not "installed globally"; they are *referenced* from commands that are.

**3. MCP servers.** These are registered separately, not via symlinks. `workspace-mcp` is registered user-scope (`claude mcp add -s user ...`) so every project sees it. Repos can also register their own MCP servers project-scope via a `.mcp.json` at the repo root, which Claude Code picks up when launched inside that repo. See `.mcp.json.example` for the template.

## The area-suffix convention

Every skill, agent, command, workflow, and prompt is tagged by primary beneficiary via a filename suffix, so the framework can be split per area later without grepping content.

| Suffix | Area | Examples |
|--------|------|----------|
| `-cc` | Cura Connect | `hosp-cert-checker-cc.md` |
| `-p` | Personal | `cv-tailorer-p/`, `/job-application-p` |
| `-mn` | Max Nerdal AB | `consulting-proposal-writer-mn/` |
| `-s` | Shared | `/morning-s`, `drive-reader-s/` |

The suffix carries through to invocation: file `application-drafter-p.md` becomes agent `@application-drafter-p`; file `morning-s.md` becomes command `/morning-s`. When in doubt: default to `-s` and promote to a specific area only when the tool grows hard dependencies on that area's data or credentials.

## Runtime tuning

Small config changes made to keep Claude Code smooth day to day. Documented so I know why they are there and can reproduce them on a fresh machine.

- **Broad `WebFetch` permission in `~/.claude/settings.json`.** Research sessions used to interrupt every few minutes to approve a new domain. Now `WebFetch` is allowed globally. Tradeoff accepted: any URL Claude decides to fetch goes through without a prompt. Safe for a solo developer machine, would not be safe in a shared environment.
- **`skipDangerousModePermissionPrompt: true`.** Avoids the modal on every session start.
- **Model default: `opus`.** Set globally rather than picking per session.
- **Voice mode enabled (hold-to-talk).** Faster than typing for long dictations.

Project-scoped MCP allowlists (`.claude/settings.local.json`, gitignored) accumulate over time as I approve individual servers/domains. That file is not portable; the durable settings are in `~/.claude/settings.json` and `.claude/settings.json`.

## Design principles

- **Shared library, not container.** Skills/agents live here; project code lives in its own repo per app (Cura Connect apps in `~/Documents/hosp-automation/`, `curaconnect-ai-framework`; Max Nerdal AB apps like tradingbots each in their own repo).
- **App repos provide project context.** Each app's `CLAUDE.md` `@imports` the relevant Obsidian area docs.
- **Obsidian is the second brain.** Business knowledge, brand, strategy, project state all in the vault. Code repos hold code and behavior.
- **Logic lives in the repo, data does not.** Personal files stay in Google Drive; secrets stay in gitignored `config.md` or `~/.config/`.
- **Skills portable, agents Claude-specific.** So the atomic capabilities can be reused if I move off Claude Code later.
- **No em dashes in generated content.** House style.

## Repo layout

```
max-ai-framework/
  .claude/                    Symlinked into ~/.claude/
    CLAUDE.md                 Global identity + preferences (Layer 1)
    agents/                   Claude Code sub-agents (Layer 5)
    commands/                 Slash commands (Layer 6)
    rules/obsidian.md         When and how to read the vault
    skills/                   Atomic capabilities (Layer 4)
    settings.json             Global permissions/theme/model
    settings.local.json       (gitignored) Machine-specific approvals
  workflows/                  Multi-step orchestrations (Layer 7)
  prompts/                    Shared writing principles (Layer 8)
  templates/                  HTML templates for finalized docs
  docs/                       Setup guides + reference material
  shell/aliases.sh            Sourced by ~/.zshrc via setup.sh
  .mcp.json.example           Project-scope MCP registration template
  config.example.md           Drive IDs + OAuth paths template
  config.md                   (gitignored) Actual IDs/paths
  setup.sh                    Creates the ~/.claude/ symlinks
  CLAUDE.md                   Repo-level context for Claude
```

## Getting started

See [docs/setup.md](docs/setup.md) for setup on a fresh machine.

For always-on server setup: [docs/server-setup.md](docs/server-setup.md).

For the Google Workspace MCP configuration: [docs/google-workspace-mcp-setup.md](docs/google-workspace-mcp-setup.md).

For how Claude Code discovers context (CLAUDE.md loading order, imports, precedence): [docs/claude-context-loading.md](docs/claude-context-loading.md).
