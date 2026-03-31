# Workflow: Update Application

Manually update the status of a job in the tracker. Quick command for recording
what happens after applications are submitted — interview invites, rejections, offers.

## Invocation

`/update-application <company> <status>`

Examples:
- `/update-application spotify interview`
- `/update-application klarna rejected`
- `/update-application netflix offer`
- `/update-application bolt declined`

---

## Valid status values

| Status | When to use |
|---|---|
| `found` | Discovered but not yet applied |
| `applied` | Application submitted |
| `interview` | Invited to interview |
| `offer` | Received an offer |
| `rejected` | Rejected by the company |
| `declined` | User chose not to proceed |
| `filled` | Position was filled |

Status matching is case-insensitive. Partial company name match is fine
(e.g., "spotify" matches "Spotify AB").

---

## Step 1: Find the tracker row

Invoke the `job-tracker` skill:
1. Read config.md → get `DRIVE_JOB_TRACKER_ID`
2. Read the tracker sheet
3. Find the row matching the company name (case-insensitive partial match)

If multiple rows match, list them and ask the user to clarify.
If no row matches, ask the user to confirm the company name.

---

## Step 2: Update the status

Update the matching row:
- Status → new value (capitalized: `Interview`, `Rejected`, etc.)
- If status is `Applied`: set Applied Date to today (YYYY-MM-DD)
- All other date fields remain unchanged

Re-sort the sheet (active statuses at top by deadline, terminal statuses at bottom).
Write the full sheet back using `mcp__gdrive__update_file`.

---

## Step 3: Confirm and prompt next action

Report the update:
```
Updated: [Company] — [Role] → [Status]
```

Then prompt based on the new status:

**If `Interview`:**
"Great news! Run `/interview-prep` to generate a prep document for this interview."

**If `Offer`:**
"Congratulations! Take your time to evaluate. Update to `Declined` or `Applied`
(accepted) when you've decided."

**If `Rejected` or `Filled`:**
"Sorry to hear it. The row is kept in the tracker for history."

**If `Declined`:**
"Noted. The row is kept in the tracker for history."

---

## Error handling

- If the tracker read fails: report the error with the tracker ID from config
- If the tracker write fails after a successful read: report it and show what the
  update would have been so the user can retry
