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

## Access
Use Read, Grep, and Glob over the vault path. The Obsidian CLI and QMD MCP are not installed; file reads cover the basics.
