# Obsidian Rules

## Vault location
The vault lives at `/Users/maxnerdal/Documents/obsidian-vault/`.

## Layout
- `Areas/{Cura Connect, Max Nerdal AB, Personal}/_context/` — canonical business docs per area (brand voice, ICP, operations). Single source of truth, never duplicated.
- `Areas/{name}/Projects/` — one `.md` per project with `status: active | paused | done`.
- `Areas/{name}/Notes/` — research, references, ideas tied to that area.
- `Daily logs/` — daily notes capturing thoughts and tasks.
- `Meeting Notes/` — meeting transcripts.
- `Notes/` — evergreen reference (SOPs, cross-area knowledge).

The Areas map 1:1 to framework contexts: `Areas/Cura Connect/` ↔ `cura-connect/`, etc. Code and automation live in the framework repo; business knowledge lives in the vault.

## Context Loading
1. Before starting any project work, check the vault for relevant context. Don't ask me for information that's already documented — go find it.
2. Check if the project's CLAUDE.md already has `@path` imports from the vault — if so, that context is already loaded.
3. If not, use Grep and Glob over the vault to find relevant notes.
4. For questions about active work, current strategy, or recent decisions — check `Areas/{name}/Projects/` **before** `_context/`. `_context/` is canonical and static (what the business is); `Projects/` holds current thinking (what we're doing now). Skipping `Projects/` produces outdated or generic answers.
5. Read key context files (brand guidelines, ICP, operations) before making decisions.
6. Never assume you know the current state of a project — the vault has the latest.
7. When I reference a meeting, decision, note, or any business context — search the vault first rather than asking me to explain it.

## Daily notes

**Important framing:** the rules below are META rules. They tell me *when* to look at daily notes, not *what* to load passively. A generic prompt unrelated to projects/areas/time (e.g. "how do I write a bash for loop?") must NOT trigger a vault dive.

**Definition (loaded passively):**
- Location: `Daily logs/YYYY-MM-DD.md`, one combined note per day.
- Sections: `## Morning briefing` / `## Cura Connect` / `## Personal` / `## Max Nerdal AB` / `## Ideas`.
- The daily note IS the history — never move done items between files; the filename is the date stamp.

**Triggers (conditional reads):**
- When the user asks "what am I working on" / "today" / mentions today's date → read today's daily note.
- When the user asks "this week" / "what did I do" / similar retrospective → read the last 7 daily notes.
- When the user captures a fresh thought or todo during work → append to today's daily note under the appropriate area section, don't create a separate file.

**Don't trigger when:** the prompt is unrelated to projects/areas/time (generic coding questions, tool usage, system setup) — leave the vault alone.

**Idea routing (three lifecycle homes):**
- Fresh, captured during the day → today's `## Ideas` section.
- Tied to an active project → drop into that `Areas/{area}/Projects/{name}.md` (the anchor file).
- Evergreen / cross-project → `Areas/{area}/Notes/`.

## Projects and todos

**Definition (loaded passively):**
- Every multi-step initiative gets a `Areas/{area}/Projects/{ProjectName}.md` anchor with `status: active|paused|done` frontmatter, a description, the full plan checklist, and a decisions log.

**Area-ownership rule** — pick by *primary beneficiary / portfolio owner*, not by what tools the work touches:
- **Cura Connect** — Cura business/ops + Cura-specific automations (HOSP automation, curaconnect-ai-framework).
- **Max Nerdal AB** — the AI framework itself, consulting portfolio, technical builds for the CV (max-ai-framework-daily-workflow, framework refactors).
- **Personal** — life logistics: job search, training, apartment, events.

The pivot: HOSP automation stays in Cura because Cura is the beneficiary, even though Max built it. max-ai-framework-daily-workflow goes to MNAB because the framework is Max's professional portfolio.

**Naming convention:**
- Anchor: `<ProjectName>.md` with `status:` frontmatter — *this is the project* in the Bases kanban.
- Supporting docs: `<ProjectName>-<aspect>.md` with **no status frontmatter** (they're documentation, not separately status-tracked).
- Independent deliverable / peer artifact (e.g. a published whitepaper): may carry its own `status:`.
- When a project grows past ~3 substantial files → promote to a folder `<ProjectName>/` with `Index.md` as anchor.

**Plan-file rule:** `~/.claude/plans/*.md` is ephemeral — plan-mode scratchpad. Persistent project state lives in `Areas/{area}/Projects/`. When a plan is approved, distill its persistent parts (description, checklist, decisions) into a Project.md; the plan file can then be discarded.

**Triggers (conditional reads):**
- When the user asks "what's active" / "what am I working on" → read `Areas/*/Projects/*.md` for `status: active` (anchors only — files without `status:` are supporting docs).
- When the user references a project by name (or via `[[wikilink]]`) → resolve and read that Project.md.
- When the user describes a new multi-step initiative → propose creating a Project.md in the right area; don't silently file under the wrong area.
- **Coupling rule:** when editing a project anchor, check files matching `<ProjectName>-*.md` (the supporting docs) for mirror updates. Example: editing `curaconnect-ai-framework.md` → also check `curaconnect-ai-framework-architecture.md`.

**Don't trigger when:** the prompt is unrelated to project/area work. Just because daily notes and Project.md files exist doesn't mean every prompt warrants reading them.

**Daily slice rule:** daily notes hold the day's *slice* of project work as wikilinks `[[Project-name]]`, not the full project checklist. The full checklist lives in the Project.md.

## Access
Use Read, Grep, and Glob over the vault path. The Obsidian CLI and QMD MCP are not installed; file reads cover the basics.
