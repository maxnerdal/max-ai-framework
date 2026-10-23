Generate today's morning briefing in the user's Obsidian daily note: a short overview plus a scratch board for agreeing on what is relevant today.

## Account map

Per-area Google routing. Update when accounts or list IDs change. The tag is used on every briefing line that belongs to an area.

| Area | Tag | Google account | Tasks list(s) for backlog |
|---|---|---|---|
| Personal | `[P]` | maxnerdal@gmail.com | Personal — Backlog (`QVRXVU1FdUNySGdiVm5nNA`) |
| Cura Connect | `[CC]` | max.nerdal@curaconnect.se | Cura Connect — Backlog (`eGItTmM3S0NiTC0tcm15Qg`), Cura Connect — Recurring (`X0d1X0RLQTE4Yk9FN1RZag`) |
| Max Nerdal AB | `[MN]` | *(not configured)* | *(none)* |

Reading calendar + Gmail for an area requires its Google account to be connected via the `workspace-mcp` server. If an account needs re-auth, call `mcp__workspace-mcp__start_google_auth` so the consent page opens, tell the user, and note the gap in the briefing rather than failing.

## Routine events

Daily blocks that are left out of the briefing entirely: `Vakna`, `Gym`, `Lunch`, `Middag`, `Läggdax`. Match by exact event title. Extend this list when the user names more.

## Steps

1. **Compute today's date** in `YYYY-MM-DD` format.

2. **Check today's daily note** at `~/Documents/obsidian-vault/Daily logs/{YYYY-MM-DD}.md`.
   - If it exists, read it. Do not overwrite content outside `## Morning briefing`. When replacing an existing briefing, the section ends at the next line that starts with `## ` (an H2 at line start). Do not match on a substring: `#### Cura Connect` contains `## Cura Connect`.
   - If it doesn't exist, write the template inline (frontmatter `date`/`weekday`, H1, then sections: Morning briefing / Cura Connect / Personal / Max Nerdal AB / Ideas).

3. **Read recent context:**
   - Last 3 daily notes for unfinished todos and momentum.
   - All `~/Documents/obsidian-vault/Areas/*/Projects/*.md` with `status: active` (anchors only — files without `status:` are supporting docs). For folder-style projects, the anchor is the file matching the folder name (e.g. `max-ai-framework/max-ai-framework.md`).
   - For each area, query its Tasks list(s) from the Account map via `mcp__workspace-mcp__list_tasks` (pass `user_google_email`, `task_list_id`, `due_max` set to `{today+7d}T23:59:59Z`, `show_completed=False`). Keep `title`, `due`, `notes`, `id` and the area. Detect `DEADLINE` by case-insensitive substring match in the `title`. Tasks without `due` are ignored unless the user asks. The legacy `Areas/*/Notes/Backlog.md` files are stubs and must NOT be parsed.
   - Resolve any `[[Project-name]]` wikilinks found in daily notes to their Project.md to get the current open checklist.
   - For each configured Google account: calendar for next 7 days via `mcp__workspace-mcp__get_events`, and unread mail via `mcp__workspace-mcp__search_gmail_messages` with `include_headers: true`:
     - `is:unread in:inbox` with `page_size: 10` for the count (write `10+` if a next page exists).
     - `is:unread in:inbox newer_than:7d -category:promotions -category:updates -category:social` for the mail worth a look.
   - **Never** use the hosted `mcp__claude_ai_Gmail__*` / `mcp__claude_ai_Google_Calendar__*` connectors — they route to the wrong inbox.

4. **Write a `## Morning briefing` section** into today's daily note with this layout:

   ```markdown
   ## Morning briefing
   ----------------------------------------------------------------------
   ----------------------------------------------------------------------
   #### Today
   - HH:MM — [Tag] Event title
   #### Week
   - **Ddd DD** — [Tag] Event HH:MM → [Tag] Event HH:MM
   #### 🚨 Deadlines within 7 days
   - YYYY-MM-DD (N days) — [Tag] [[Project-or-item]]
   ----------------------------------------------------------------------
   #### Todos
   - [ ] YYYY-MM-DD — [Tag] title <!-- gt:TASK_ID -->
   #### Email
   - [Tag] account — N unread; "Subject" (Sender), "Subject" (Sender)
   ----------------------------------------------------------------------
   #### Today — scratch
   - [Tag] suggestion — why (source)

   ----------------------------------------------------------------------
   ----------------------------------------------------------------------
   ```

   **Today / Week:** only non-routine events (see Routine events). Week lists only days that have something, one line per day, chained with `→`. Flag clashes with `⚠`. If a calendar is empty for the whole range, omit it silently; if it was unreachable, add one line saying so.

   **Todos:** one merged list across all areas, no per-area blocks. Pull rule: only tasks with `due` today or earlier (overdue). Sort by `due`, then by title. DEADLINE tasks within 7 days appear in the Deadlines block as a heads-up, and in Todos only from their due date. Line format `- [ ] YYYY-MM-DD — [Tag] <title> <!-- gt:TASK_ID -->`, title verbatim and never truncated.

   **Email:** one line per configured account. Count, then at most 3 subjects from the "worth a look" query. Leave out subjects if there are none. Security notices (credential rotation, unknown logins) always go in.

   **Today — scratch:** 3–5 suggestions for what is relevant today that are not already in Todos: project next steps, tasks due in the next 1–2 days worth starting, emails that need action, open ideas from the last 3 daily notes. Each line tagged and one-row. These are suggestions only. After writing the briefing, ask the user what goes on today's list, then rewrite this block with the agreed items as `- [ ]` lines (no `gt:` comment unless it is an existing task).

   **No per-area project lists.** Project state feeds the scratch suggestions instead.

   **Spacing:** no blank lines between a subheader and its bullets.

   **Dividers:** a double rule frames the briefing top and bottom. A single rule separates the overview (Today/Week/Deadlines), the lists (Todos/Email), and the scratch board.

   **Setext gotcha:** when a `---` rule directly follows a paragraph or italic line, CommonMark parses it as a setext H2 underline. Always insert a blank line between paragraph/italic content and the rule below it. Rules that follow a list item or ATX heading are safe without a blank line.

   **One row, 100-char cap:** every list item except Todos is one line, max 100 characters. Summarize aggressively — strip attendees, drop "the/a", abbreviate ("HiInt" not "Hi-Intensity").

5. **Don't** auto-check off items, modify content outside `## Morning briefing`, or pull items into the daily note's `## {area}` writing sections.

## Companion command

`/sweep-s` is the end-of-day closer. It parses the `#### Todos` block, derives each line's area from its tag via the Account map, and syncs check-marks with Google Tasks through the `<!-- gt:TASK_ID -->` comments.

## Out of scope for this command

- **Two-way calendar** (creating events from todos) — read-only.
- **Email auto-triage** beyond the "worth a look" filter.
- **Scheduled routine** — manual `/morning-s` only for now.
