End-of-day closer for the daily workflow. Syncs check-marks between today's morning briefing and Google Tasks in both directions, then appends a `## What got done` ledger to today's daily note. Pair to `/morning-s`.

## Why this exists

The morning briefing captures the **plan**. By itself it never becomes a record of what actually happened — checked items pile up in the briefing, but the daily note still reads the same as it did at 9am, and the Tasks list still shows them open. `/sweep-s` closes the loop:

1. **Bidirectional task sync** — `/morning-s` writes briefing rows like `- [ ] YYYY-MM-DD — title <!-- gt:TASK_ID -->`. During the day:
   - Items checked off in the briefing get marked `completed` in Google Tasks via the embedded ID.
   - Items completed directly in the Google Tasks UI (mobile, desktop, calendar sidebar) get flipped from `[ ]` to `[x]` in the briefing.
   The briefing and Tasks list end the day consistent. Daily note IS the history (rule from `~/.claude/rules/obsidian.md`), so checked items stay in the briefing untouched after sync.
2. **Daily-log finalization** — at end of day the daily note should be an accurate record of what got done. Git activity (commits across all known repos today) is captured automatically, and any unchecked planned todos are surfaced as deferred. Combined with the hand-written area sections, the file becomes a real ledger.
3. **Area-capture routing** — the top-level `## <Area>` h2 sections collect free-form thoughts during the day. Without a sweep, those notes only ever live in the daily note and never reach a persistent home (Project anchor, area Notes, Tasks). Sweep walks each capture and asks where it belongs, per the idea-routing rule in `~/.claude/rules/obsidian.md`.

## Account map

Same routing as `/morning-s` — kept in sync. Update when accounts or list IDs change.

| Area | Google account | Tasks list(s) for backlog |
|---|---|---|
| Personal | maxnerdal@gmail.com | Personal — Backlog (`QVRXVU1FdUNySGdiVm5nNA`) |
| Cura Connect | max.nerdal@curaconnect.se | Cura Connect — Backlog (`eGItTmM3S0NiTC0tcm15Qg`), Cura Connect — Recurring (`X0d1X0RLQTE4Yk9FN1RZag`) |
| Max Nerdal AB | *(not configured)* | *(none)* |

## Steps

1. **Compute today's date** in `YYYY-MM-DD` format. Capture `today_start` as `{YYYY-MM-DD}T00:00:00Z` and `now` as the current RFC 3339 timestamp.

2. **Read today's daily note** at `~/Documents/obsidian-vault/Daily logs/{YYYY-MM-DD}.md`. If it doesn't exist, exit with "no daily note for today, nothing to sweep."

3. **Locate the `## Morning briefing` section.** Within it, iterate the area subsections (`#### Cura Connect`, `#### Personal`, `#### Max Nerdal AB` — match by header text exactly, since these map 1:1 to vault folder names and to the Account map above).

4. **For each area, find its `###### Todos` block and parse every line.** A line is in scope if it matches the pattern `- [ ] <content> <!-- gt:<TASK_ID> -->` or `- [x] <content> <!-- gt:<TASK_ID> -->`. Capture: `state` (`[ ]` or `[x]`), `content` (without the trailing comment), `task_id`. Lines without a `<!-- gt:... -->` comment are legacy or hand-added — leave them untouched and log a warning naming the line.

5. **For each area, fetch tasks completed today from Google Tasks.** Call `mcp__workspace-mcp__list_tasks` per list in the Account map with `show_completed=True`, `show_hidden=True`, `completed_min={today_start}`, `completed_max={now}`. Merge results across the area's lists. Collect the set of completed `task_id`s — call this `completed_in_tasks`.

6. **Reconcile each parsed briefing line** (per area):

   | Briefing state | task_id in `completed_in_tasks`? | Action |
   |---|---|---|
   | `[ ]` | yes | Edit briefing line: flip `[ ]` → `[x]`. Tag for the summary as "synced from Tasks". |
   | `[x]` | yes | Already consistent — no-op. |
   | `[x]` | no | Call `mcp__workspace-mcp__manage_task` (action=update, status=completed, `task_id`, `task_list_id` — re-derive the list from the area's Account-map entry; if the area has multiple lists, try each until one succeeds or all return 404). Tag for the summary as "synced to Tasks". |
   | `[ ]` | no | Deferred — no action this step. Tracked separately in step 8. |

   Mutate the daily note only when flipping `[ ]` → `[x]`. Preserve the entire suffix including the `<!-- gt:... -->` comment.

7. **Collect today's git activity.** Glob `~/Documents/*/.git` (depth 1) to discover repos. For each repo, run `git -C <repo> log --since="00:00" --until="now" --all --pretty=format:'%h %s'` to capture every commit authored today on any branch. No author filter (single-user machine). Skip repos with zero commits silently. Capture the current default branch name per repo via `git -C <repo> symbolic-ref --short HEAD` for the display label (best-effort; fall back to "various" if detached or unclear).

8. **Collect deferred todos.** Re-walk the briefing's area `###### Todos` blocks (state is now post-reconciliation) and capture every line still matching `- [ ] <content>`. Tag each with its area name. Do **not** rewrite these briefing lines — they stay `[ ]` as the day's open-at-EOD record.

9. **Write the `## What got done` section.** Append (or replace, if it already exists) a `## What got done` section at the end of `Daily logs/{YYYY-MM-DD}.md`. Idempotent: rerunning `/sweep-s` must replace the existing section, not duplicate it.

   Format:

   ```markdown
   ## What got done

   #### Shipped
   - **<repo-basename>** (<N> commits on `<branch>`)
     - <shortsha> — <subject>
     - …
   - …

   #### Deferred from morning
   - [<Area>] <content>
   - …
   ```

   Omission rules:
   - If no commits today across any repo → omit the `#### Shipped` subsection entirely.
   - If no deferred todos in any area → omit `#### Deferred from morning` entirely.
   - If both are empty → do not write the `## What got done` section at all.

   Sorting: repos by commit count desc, then alphabetically. Within a repo, commits in chronological order (oldest first).

10. **Route area captures.** For each top-level area section (`## Cura Connect`, `## Personal`, `## Max Nerdal AB` — match by h2 header text exactly), read the content between that header and the next `##` header.

    - **Skip silently** if the section has no body content (only whitespace, or no bullets/paragraphs).
    - **Parse into capture units:** a bold header line (`**<title>**`) followed by its bullets/paragraph forms one unit; loose top-level bullets in a contiguous stretch form one unit; standalone paragraphs are their own unit. Use judgement — if the user wrote one cohesive thought, treat it as one unit even if formatting is mixed.
    - **For each capture unit, prompt with `AskUserQuestion`.** Show the unit verbatim in the question text and ask where it should be routed. Options:
      - **Area Note** — append to `Areas/{Area}/Notes/<file>.md`. If an existing note in that area clearly matches the topic, propose appending to it; otherwise propose a new filename inferred from the unit's title/content. Confirm the filename before writing.
      - **Project** — drill: new or existing. *New* → scaffold `Areas/{Area}/Projects/<ProjectName>.md` with `status: active` frontmatter, a description distilled from the capture, and a plan checklist seeded from any bullets. *Existing* → list active projects in that area (anchors with `status: active`) and ask which one to append the capture into (under a heading like `## Notes` or `## Decisions` as appropriate).
      - **Backlog todo** — create a task via `mcp__workspace-mcp__manage_task` (action=create) on the area's Backlog Tasks list from the Account map. Drill: dated or undated. If dated, ask for the date (offer today as default) and pass it as `due` in RFC 3339 at 09:00 Europe/Stockholm. If a hard deadline, prefix the title with `🚨 DEADLINE —`. If the capture is a multi-bullet group, ask whether to file as one task or split into several. **Never** edit `Areas/{Area}/Notes/Backlog.md` — those files are stubs since 2026-06-16.
      - **Project todo** — list active Project anchors in the area and append `- [ ] <content>` to the chosen project's plan checklist. Use this when the capture is actionable and clearly belongs to an ongoing project's scope.
      - **Leave as-is** — no action; the daily note remains the only home for this capture.
    - **Do not delete or modify the daily note's area section.** The daily note IS the history (`~/.claude/rules/obsidian.md` — "the daily note IS the history; never move done items between files"). Routing creates a persistent home elsewhere; the original capture stays in the daily note as the timestamped record of when it was thought.
    - Track each routing decision for the summary (counts per destination type).

11. **Print a summary:**

    ```
    Sweep complete.
      Sync: <synced-to-tasks> briefing→Tasks, <synced-from-tasks> Tasks→briefing, <warnings> warnings.
      What got done: <commits> commits across <repos> repos, <deferred> deferred todos.
      Routed: <n> captures (Notes: <n>, Projects: <n>, Backlog tasks: <n>, Project todos: <n>, Left: <n>).
    ```

## What this does NOT do

- Does not modify the morning briefing **except** to flip `[ ]` → `[x]` on lines whose Google Task was completed during the day (step 6). All other content stays as the morning snapshot. Deferred todos appear in the new `## What got done` section, not by rewriting the briefing.
- Does not act on briefing lines without a `<!-- gt:TASK_ID -->` comment — they're legacy/hand-added and out of scope. A warning is logged.
- Does not modify calendar events. If a planned event didn't happen, the user marks it manually.
- Does not auto-modify project checklists *without confirmation*. The routing step can append `- [ ]` items to a Project's plan, but only after the user picks "Project todo" and chooses the target project — never silently.
- Does not act on `- [x]` items found anywhere outside an area's `###### Todos` subsection — ad-hoc todos the user added elsewhere are off-limits.
- Does not handle undated Google Tasks. Sweep operates only on tasks present in today's briefing (which `/morning-s` filtered to `due ≤ today`).
- Does not query GitHub. Pure local `git log` — pushed-but-uncommitted work isn't a thing, and local commits not yet pushed still count as "shipped" today.
- Does not delete or rewrite captures in the daily note's `## <Area>` sections. Routing copies the capture to a persistent home; the daily note retains the original as history.
- Does not auto-route. Every routing decision goes through `AskUserQuestion` — no silent filing.
- Does not touch `Areas/*/Notes/Backlog.md` files. Those are migration stubs since 2026-06-16; backlog state lives in Google Tasks.

## Scheduling (optional)

To run nightly at 23:59, set up a macOS LaunchAgent. Ask Claude:

> Set up a macOS LaunchAgent called `com.max.sweep` that runs `claude --print "/sweep-s"` daily at 23:59. Make sure the PATH includes the directory where `claude` is installed (check with `which claude`). Log output to `/tmp/sweep.log`. Load it with `launchctl` after creating it.

Until then, run `/sweep-s` manually before bed.
