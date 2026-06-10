Generate today's morning briefing in the user's Obsidian daily note.

## Account map

Per-area Google account routing. Update when accounts change.

| Area | Google account |
|---|---|
| Personal | maxnerdal@gmail.com |
| Cura Connect | max.nerdal@curaconnect.se |
| Max Nerdal AB | *(not configured)* |

Reading calendar + Gmail for an area requires its Google account to be connected in **Claude.ai → Settings → Integrations**. If an account isn't reachable, note it in the briefing rather than failing.

## Steps

1. **Compute today's date** in `YYYY-MM-DD` format.

2. **Check today's daily note** at `~/Documents/obsidian-vault/Daily logs/{YYYY-MM-DD}.md`.
   - If it exists, read it. Do not overwrite content outside `## Morning briefing`.
   - If it doesn't exist, ask the user to open Obsidian and click "Today's note" so Templater fires the template. As a fallback, write the template inline (sections: Morning briefing / Cura Connect / Personal / Max Nerdal AB / Ideas).

3. **Read recent context:**
   - Last 3 daily notes (yesterday, day-before, day-before-that) for unfinished todos and momentum.
   - All `~/Documents/obsidian-vault/Areas/*/Projects/*.md` with `status: active` (anchors only — files without `status:` are supporting docs). For folder-style projects, the anchor is the file matching the folder name (e.g. `max-ai-framework/max-ai-framework.md`).
   - Each `~/Documents/obsidian-vault/Areas/*/Notes/Backlog.md` (if exists). Parse items under `## Dated`: detect `DEADLINE` keyword, parse leading `YYYY-MM-DD`, compute days-until. Items under `## No date` are ignored unless the user asks.
   - Resolve any `[[Project-name]]` wikilinks found in daily notes to their Project.md to get the current open checklist.
   - For each configured Google account: read calendar for next 7 days via `mcp__claude_ai_Google_Calendar__list_events`, and recent unread inbox via `mcp__claude_ai_Gmail__search_threads` with query `is:unread newer_than:7d`.

4. **Write a `## Morning briefing` section** into today's daily note with this layout:

   ```markdown
   ## Morning briefing

   ### 📅 Today's combined calendar
   - HH:MM — [Area] Event title
   (events from all configured accounts, sorted by time)

   ### Calendar notes for the week
   - One line per upcoming day with notable load (heavy days, conflicts), area-tagged

   ### 🚨 Deadlines within 7 days
   - YYYY-MM-DD (N days) — [Area] [[Project-or-item]]
   (sourced from: DEADLINE items in backlogs + project Plan checklists containing DEADLINE)

   ### Cura Connect
   - 📋 Soft targets:
     - YYYY-MM-DD — item (from backlog, dated within next 7 days, no DEADLINE keyword)
   - 🟢 Active: [[Project-name]] — current next open checklist item (one bullet per status: active Project.md in this area)
   - 📧 Email (account): N unread
     - "Subject" — HH:MM (last 3 unread)

   ### Personal
   - (same structure)

   ### Max Nerdal AB
   - (same structure; if email account not configured, note "*(no account configured)*")

   ### 💡 Open ideas
   - Items from the last 3 daily notes' ## Ideas sections that haven't been promoted to a Project.md or area's Notes/
   ```

5. **Auto-pull rule:** Only DEADLINE-marked items whose date == today get pulled into today's daily note's matching `## {area}` section as an unchecked checkbox. Soft-dated items and overdue soft items stay in the briefing only — they are not pulled.

6. **Don't** auto-check off items, move tasks between sections, or modify content outside `## Morning briefing` (except the explicit auto-pull rule in step 5). The daily note is the user's writing surface; the briefing is the section this command owns.

## Out of scope for this command

- **Two-way calendar** (creating events from todos) — read-only.
- **Email auto-triage** (which need reply) — listing unread is in scope, classification is not.
- **Cowork monitor state** — separate future iteration.
- **Scheduled routine** — manual `/morning` only for now.
