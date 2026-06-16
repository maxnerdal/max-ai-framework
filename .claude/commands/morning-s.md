Generate today's morning briefing in the user's Obsidian daily note.

## Account map

Per-area Google routing. Update when accounts or list IDs change.

| Area | Google account | Tasks list(s) for backlog |
|---|---|---|
| Personal | maxnerdal@gmail.com | Personal — Backlog (`QVRXVU1FdUNySGdiVm5nNA`) |
| Cura Connect | max.nerdal@curaconnect.se | Cura Connect — Backlog (`eGItTmM3S0NiTC0tcm15Qg`), Cura Connect — Recurring (`X0d1X0RLQTE4Yk9FN1RZag`) |
| Max Nerdal AB | *(not configured)* | *(none)* |

Reading calendar + Gmail for an area requires its Google account to be connected via the `workspace-mcp` server. If an account isn't reachable, note it in the briefing rather than failing.

## Steps

1. **Compute today's date** in `YYYY-MM-DD` format.

2. **Check today's daily note** at `~/Documents/obsidian-vault/Daily logs/{YYYY-MM-DD}.md`.
   - If it exists, read it. Do not overwrite content outside `## Morning briefing`.
   - If it doesn't exist, ask the user to open Obsidian and click "Today's note" so Templater fires the template. As a fallback, write the template inline (sections: Morning briefing / Cura Connect / Personal / Max Nerdal AB / Ideas).

3. **Read recent context:**
   - Last 3 daily notes (yesterday, day-before, day-before-that) for unfinished todos and momentum.
   - All `~/Documents/obsidian-vault/Areas/*/Projects/*.md` with `status: active` (anchors only — files without `status:` are supporting docs). For folder-style projects, the anchor is the file matching the folder name (e.g. `max-ai-framework/max-ai-framework.md`).
   - For each area, query its Tasks list(s) from the Account map via `mcp__workspace-mcp__list_tasks` (pass `user_google_email`, `task_list_id`, `due_max` set to `{today+7d}T23:59:59Z`, leave `show_completed=False`). Merge results from all of the area's lists. Each returned task has `title`, `due` (RFC 3339), `notes`, and `id` — keep all four for later steps. Detect `DEADLINE` by case-insensitive substring match in the task `title`. Tasks **without** a `due` value are the new "undated" set — ignore unless the user asks. The legacy `Areas/*/Notes/Backlog.md` files are now stubs and must NOT be parsed.
   - Resolve any `[[Project-name]]` wikilinks found in daily notes to their Project.md to get the current open checklist.
   - For each configured Google account: read calendar for next 7 days via `mcp__workspace-mcp__get_events` (pass `user_google_email`, `time_min`, `time_max`), and recent unread inbox via `mcp__workspace-mcp__search_gmail_messages` with query `is:unread in:inbox` and `page_size: 3`. Resolve subjects/dates with `mcp__workspace-mcp__get_gmail_messages_content_batch` (format: `metadata`). **Never** use the hosted `mcp__claude_ai_Gmail__*` / `mcp__claude_ai_Google_Calendar__*` connectors — they route to the wrong inbox.

4. **Write a `## Morning briefing` section** into today's daily note with this layout:

   ```markdown
   ## Morning briefing
   ----------------------------------------------------------------------
   ----------------------------------------------------------------------
   #### 📅 Today's combined calendar
   - HH:MM — [Area] Event title
   #### Calendar notes for the week
   - **One line per date** with notable load (heavy days, conflicts), area-tagged. Do not list attendees — just event title and time. Multiple events on the same date go on the same line, chained with `→`.
   #### 🚨 Deadlines within 7 days
   - YYYY-MM-DD (N days) — [Area] [[Project-or-item]]
   ----------------------------------------------------------------------
   #### Cura Connect
   ###### Projects
   - [[Project-name]] — next open checklist item
   ###### Todos
   - [ ] YYYY-MM-DD — title <!-- gt:TASK_ID --> (only overdue + today's; DEADLINE prefixed 🚨)
   ###### Email (account)
   - N unread
     - "Subject" — HH:MM (last 3)
   ----------------------------------------------------------------------
   #### Personal
   - (same structure)
   ----------------------------------------------------------------------
   #### Max Nerdal AB
   - (same structure; if email account not configured, note "*(no account configured)*")
   #### 💡 Open ideas
   - Items from the last 3 daily notes' ## Ideas sections not promoted to a Project.md or area's Notes/

   ----------------------------------------------------------------------
   ----------------------------------------------------------------------
   ```

   **Spacing:** keep the example tight — no blank lines between a subheader and its bullets, single blank line between top-level (`####`) blocks only where it aids scanning.

   **Dividers:** the briefing is framed by a **double rule** (two `---` lines stacked, top and bottom). Each area block (Cura, Personal, Max Nerdal AB) is preceded by a **single `---` rule** — including Cura, which is separated from the Deadlines block above it. The Calendar / Week / Deadlines / Open ideas blocks themselves are not flanked by rules.

   **Setext gotcha:** when a `---` rule directly follows a paragraph or italic line (e.g. `*(no previous...)*`), CommonMark parses it as a setext H2 underline and the line above becomes a giant heading. Always insert a blank line between paragraph/italic content and the rule below it. Rules that follow a list item or ATX heading are safe without a blank line.

   **One row, 100-char cap:** every list item in the briefing (Calendar, Week, Deadlines, Projects, Email, Open ideas) is one line, max 100 characters. No wrapped sentences, no multi-line bullets. Summarize aggressively — strip attendees, drop "the/a", abbreviate ("HiInt" not "Hi-Intensity"), use `→` to chain. **Exception: Todos.** Todo lines must reproduce the task title verbatim (`- [ ] YYYY-MM-DD — title <!-- gt:TASK_ID -->`) — never truncate them, even if they exceed 100. The trailing HTML comment carries the Google Tasks ID so `/sweep-s` (when rewritten) can mark the task completed via API.

5. **Todo pull rule:** Only tasks whose `due` date is **today or earlier (overdue)** are written as unchecked checkboxes under that area's `###### Todos` subheader, in chronological order. Future-dated tasks stay in their Tasks list — they're not surfaced in the area block. DEADLINE-titled tasks (case-insensitive substring) with `due` within 7 days still appear in the top-level `🚨 Deadlines within 7 days` summary as a heads-up, but only get pulled into the area's Todos block on their due date (or after, if missed). Each checkbox line takes the form `- [ ] YYYY-MM-DD — <title> <!-- gt:TASK_ID -->`. If the title already starts with `🚨 DEADLINE —` keep it as-is. Undated tasks (no `due` value) are ignored unless the user asks.

6. **Don't** auto-check off items, modify content outside `## Morning briefing`, or pull items into the area's top-level `## {area}` writing section. The briefing is fully self-contained — the user's writing surface below it is untouched.

## Companion command

`/sweep-s` is the end-of-day closer for this workflow. Backlogs migrated from `Backlog.md` to Google Tasks on 2026-06-16 (see [[max-ai-framework-tasks-backed-backlog]]); `/sweep-s` still runs but its backlog-cleanup step is currently a no-op against the Backlog.md stubs. The Tasks-aware rewrite — which will parse the `<!-- gt:TASK_ID -->` comments emitted here and call `manage_task` action=update status=completed — is tracked in that Project.md. The daily note keeps its checked-off history regardless.

## Out of scope for this command

- **Two-way calendar** (creating events from todos) — read-only.
- **Email auto-triage** (which need reply) — listing unread is in scope, classification is not.
- **Cowork monitor state** — separate future iteration.
- **Scheduled routine** — manual `/morning-s` only for now.
