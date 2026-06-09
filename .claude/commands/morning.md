Generate today's morning briefing in the user's Obsidian daily note.

## Steps

1. **Compute today's date** in `YYYY-MM-DD` format.

2. **Check today's daily note** at `~/Documents/obsidian-vault/Daily logs/{YYYY-MM-DD}.md`.
   - If it exists, read it to know what's already there. Do not overwrite existing content outside `## Morning briefing`.
   - If it doesn't exist, ask the user to open Obsidian and click "Today's note" so Templater fires the template. As a fallback, write the template inline (sections: Morning briefing / Cura Connect / Personal / Max Nerdal AB / Ideas).

3. **Read recent context:**
   - Last 3 daily notes (yesterday, day-before, day-before-that) for unfinished todos and momentum.
   - All `~/Documents/obsidian-vault/Areas/*/Projects/*.md` with `status: active` (anchors only — files without `status:` are supporting docs).
   - Resolve any `[[Project-name]]` wikilinks found in the daily notes to their `Project.md` to get the current open checklist.

4. **Write a `## Morning briefing` section** into today's daily note containing:
   - **Carry-over** — unchecked todos from yesterday's daily note, grouped by area, with `[[Project-name]]` wikilinks preserved.
   - **Active projects per area** — one line per `status: active` `Project.md` with its current next open checklist item.
   - **Suggested priorities** — 2–3 items the user should consider today. Frame as suggestions, not decisions.
   - **Open ideas** — fresh ideas from the last 3 days' `## Ideas` sections that haven't been promoted to a `Project.md` or area's `Notes/`.

5. **Do not** auto-check off items, move tasks between sections, or modify content outside `## Morning briefing`. The daily note is the user's writing surface; the briefing is the only section this command owns.

## Out of scope for this command (MVP)

- Calendar events (Google Calendar MCP)
- Email triage (Gmail MCP)
- Cowork monitor state

These integrations will be added in a future iteration of this command.
