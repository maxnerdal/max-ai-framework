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
   - [ ] YYYY-MM-DD — item (only overdue + today's; DEADLINE prefixed 🚨)
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

   **One row, 100-char cap:** every list item in the briefing (Calendar, Week, Deadlines, Projects, Email, Open ideas) is one line, max 100 characters. No wrapped sentences, no multi-line bullets. Summarize aggressively — strip attendees, drop "the/a", abbreviate ("HiInt" not "Hi-Intensity"), use `→` to chain. **Exception: Todos.** Todo lines must reproduce the backlog text verbatim (`- [ ] YYYY-MM-DD — description`) so `/sweep` can match — never truncate them, even if they exceed 100.

5. **Todo pull rule:** Only dated backlog items whose date is **today or earlier (overdue)** are written as unchecked checkboxes under that area's `###### Todos` subheader. Future-dated items stay in the backlog — they're not surfaced in the area block. DEADLINE items within 7 days still appear in the top-level `🚨 Deadlines within 7 days` summary as a heads-up, but only get pulled into Todos on their due date (or after, if missed). The checkbox line must match the backlog line text exactly (`- [ ] YYYY-MM-DD — description`) so `/sweep` can match it back at end of day. Undated backlog items are ignored unless the user asks.

6. **Don't** auto-check off items, modify content outside `## Morning briefing`, or pull items into the area's top-level `## {area}` writing section. The briefing is fully self-contained — the user's writing surface below it is untouched.

## Companion command

`/sweep-s` is the end-of-day closer for this workflow. It reads checked todos out of today's briefing and removes the matching lines from each area's `Backlog.md`. The daily note keeps its checked-off history; the backlog gets the open items only.

## Out of scope for this command

- **Two-way calendar** (creating events from todos) — read-only.
- **Email auto-triage** (which need reply) — listing unread is in scope, classification is not.
- **Cowork monitor state** — separate future iteration.
- **Scheduled routine** — manual `/morning-s` only for now.
