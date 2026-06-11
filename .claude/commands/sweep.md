End-of-day backlog cleanup and daily-log finalization. Read checked todos out of today's morning briefing, remove the matching lines from each area's `Backlog.md`, then append a `## What got done` section to today's daily note recording git activity and any deferred todos. Pair to `/morning`.

## Why this exists

The morning briefing captures the **plan**. By itself it never becomes a record of what actually happened — checked items pile up in the briefing, but the daily note still reads the same as it did at 9am. `/sweep` closes the loop:

1. Backlog cleanup — `/morning` pulls dated backlog items into the briefing as `- [ ]` checkboxes; throughout the day they get ticked off. Without a sweep, those same items would re-appear in tomorrow's briefing. The daily note IS the history (rule from `~/.claude/rules/obsidian.md`), so checked items stay there untouched; only the backlog is mutated.
2. Daily-log finalization — at end of day, the daily note should be an accurate record of what got done. Git activity (commits across all known repos today) is captured automatically, and any unchecked planned todos are surfaced as deferred. Combined with the hand-written area sections, the file becomes a real ledger.
3. Area-capture routing — the top-level `## <Area>` h2 sections collect free-form thoughts during the day. Without a sweep, those notes only ever live in the daily note and never reach a persistent home (Project anchor, area Notes, Backlog). Sweep walks each capture and asks where it belongs, per the idea-routing rule in `~/.claude/rules/obsidian.md`.

## Steps

1. **Compute today's date** in `YYYY-MM-DD` format.

2. **Read today's daily note** at `~/Documents/obsidian-vault/Daily logs/{YYYY-MM-DD}.md`. If it doesn't exist, exit with "no daily note for today, nothing to sweep."

3. **Locate the `## Morning briefing` section.** Within it, iterate the area subsections (`### Cura Connect`, `### Personal`, `### Max Nerdal AB` — match by header text exactly, since these map 1:1 to vault folder names).

4. **For each area, find its `###### Todos` block.** Collect every line matching the pattern `- [x] <content>`. Strip any leading 🚨 emoji from the content. The `<content>` is the matching key.

5. **For each checked item, mutate that area's backlog:**
   - Path: `~/Documents/obsidian-vault/Areas/{Area}/Notes/Backlog.md`.
   - Find the line that reads `- [ ] <content>` (exact match against the captured content, after stripping 🚨 from the briefing line).
   - Delete that line.
   - If no match is found, log a warning naming the item and which backlog was searched — do **not** delete arbitrary lines. A missed match usually means the user edited the backlog text after `/morning` ran; surfacing it lets them clean it up by hand.

6. **Collect today's git activity.** Glob `~/Documents/*/.git` (depth 1) to discover repos. For each repo, run `git -C <repo> log --since="00:00" --until="now" --all --pretty=format:'%h %s'` to capture every commit authored today on any branch. No author filter (single-user machine). Skip repos with zero commits silently. Capture the current default branch name per repo via `git -C <repo> symbolic-ref --short HEAD` for the display label (best-effort; fall back to "various" if detached or unclear).

7. **Collect deferred todos.** Re-walk the briefing's area `###### Todos` blocks (same logic as step 3–4) and capture every line still matching `- [ ] <content>`. These are items that were pulled into today's briefing but not checked off. Tag each with its area name. Do **not** rewrite the briefing line; the briefing is a snapshot of the morning and stays as-is.

8. **Write the `## What got done` section.** Append (or replace, if it already exists) a `## What got done` section at the end of `Daily logs/{YYYY-MM-DD}.md`. Idempotent: rerunning `/sweep` must replace the existing section, not duplicate it.

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

9. **Route area captures.** For each top-level area section (`## Cura Connect`, `## Personal`, `## Max Nerdal AB` — match by h2 header text exactly), read the content between that header and the next `##` header.

   - **Skip silently** if the section has no body content (only whitespace, or no bullets/paragraphs).
   - **Parse into capture units:** a bold header line (`**<title>**`) followed by its bullets/paragraph forms one unit; loose top-level bullets in a contiguous stretch form one unit; standalone paragraphs are their own unit. Use judgement — if the user wrote one cohesive thought, treat it as one unit even if formatting is mixed.
   - **For each capture unit, prompt with `AskUserQuestion`.** Show the unit verbatim in the question text and ask where it should be routed. Options:
     - **Area Note** — append to `Areas/{Area}/Notes/<file>.md`. If an existing note in that area clearly matches the topic, propose appending to it; otherwise propose a new filename inferred from the unit's title/content. Confirm the filename before writing.
     - **Project** — drill: new or existing. *New* → scaffold `Areas/{Area}/Projects/<ProjectName>.md` with `status: active` frontmatter, a description distilled from the capture, and a plan checklist seeded from any bullets. *Existing* → list active projects in that area (anchors with `status: active`) and ask which one to append the capture into (under a heading like `## Notes` or `## Decisions` as appropriate).
     - **Backlog todo** — drill: dated or undated. If dated, ask for the date (offer today as default). Append `- [ ] YYYY-MM-DD — <content>` or `- [ ] <content>` to the right section of `Areas/{Area}/Notes/Backlog.md`. If the capture is a multi-bullet group, ask whether to file as one todo or split into several.
     - **Project todo** — list active Project anchors in the area and append `- [ ] <content>` to the chosen project's plan checklist. Use this when the capture is actionable and clearly belongs to an ongoing project's scope.
     - **Leave as-is** — no action; the daily note remains the only home for this capture.
   - **Do not delete or modify the daily note's area section.** The daily note IS the history (`~/.claude/rules/obsidian.md` — "the daily note IS the history; never move done items between files"). Routing creates a persistent home elsewhere; the original capture stays in the daily note as the timestamped record of when it was thought.
   - Track each routing decision for the summary (counts per destination type).

10. **Print a summary:** per-area count of items removed from backlog, list of any warnings (unmatched items), total commits across N repos, count of deferred todos, and routing counts. Format:

    ```
    Sweep complete.
      Backlog: <total> removed (Personal: <n>, Cura Connect: <n>, Max Nerdal AB: <n>), <warnings> warnings.
      What got done: <commits> commits across <repos> repos, <deferred> deferred todos.
      Routed: <n> captures (Notes: <n>, Projects: <n>, Backlog: <n>, Project todos: <n>, Left: <n>).
    ```

## What this does NOT do

- Does not modify the morning briefing. Checked and unchecked items both stay as they were — the briefing is the morning snapshot. Deferred todos appear in the new `## What got done` section, not by rewriting the briefing.
- Does not modify calendar events. If a planned event didn't happen, the user marks it manually.
- Does not auto-modify project checklists *without confirmation*. The routing step can append `- [ ]` items to a Project's plan, but only after the user picks "Project todo" and chooses the target project — never silently.
- Does not act on `- [x]` items found anywhere outside an area's `###### Todos` subsection — ad-hoc todos the user added elsewhere are off-limits.
- Does not act on items under `## No date` in the backlog. Sweep only removes lines that were dated.
- Does not query GitHub. Pure local `git log` — pushed-but-uncommitted work isn't a thing, and local commits not yet pushed still count as "shipped" today.
- Does not delete or rewrite captures in the daily note's `## <Area>` sections. Routing copies the capture to a persistent home; the daily note retains the original as history.
- Does not auto-route. Every routing decision goes through `AskUserQuestion` — no silent filing.

## Scheduling (optional)

To run nightly at 23:59, set up a macOS LaunchAgent. Ask Claude:

> Set up a macOS LaunchAgent called `com.max.sweep` that runs `claude --print "/sweep"` daily at 23:59. Make sure the PATH includes the directory where `claude` is installed (check with `which claude`). Log output to `/tmp/sweep.log`. Load it with `launchctl` after creating it.

Until then, run `/sweep` manually before bed.
