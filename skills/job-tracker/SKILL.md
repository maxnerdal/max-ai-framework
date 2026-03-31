---
name: job-tracker
description: >
  Read and write the job application tracker Google Sheet. Use this skill whenever you need to
  look up job application status, add a new job to the tracker, update a job's status, check for
  duplicate entries, or list jobs by status/deadline. Triggers on: tracking jobs, updating
  application status, checking if a job is already tracked, listing applications, finding jobs
  with upcoming deadlines, marking jobs as applied/interview/rejected.
---

# job-tracker

Read and write the Job Tracker Google Sheet. The tracker is the central record of all job
applications — every other skill that needs to know about application state depends on this one.

## How it works

The tracker is a Google Sheet stored at `DRIVE_JOB_TRACKER_ID` in config.md.

The gdrive MCP reads Sheets as CSV but cannot write to individual cells — it only writes
plain text. To write proper rows and columns, always use the `sheets.py` script via Bash.

### Reading

```
1. Read config.md → get DRIVE_JOB_TRACKER_ID
2. Run: python skills/job-tracker/scripts/sheets.py read <DRIVE_JOB_TRACKER_ID>
3. Output is a JSON array of arrays — parse into rows
```

Alternatively, `mcp__gdrive__read_file` also works for reading (returns CSV), but
`sheets.py read` returns structured JSON which is easier to work with.

### Writing

Always read the current state first, modify rows in memory, re-sort, then write back.

```
1. Read current sheet (see above)
2. Make changes (add row, update status, re-sort)
3. Write back:
   python skills/job-tracker/scripts/sheets.py write <DRIVE_JOB_TRACKER_ID> '<rows_json>'
   where rows_json is a JSON array of arrays including the header row
```

### Appending a single new row

```
python skills/job-tracker/scripts/sheets.py append <DRIVE_JOB_TRACKER_ID> '<row_json>'
where row_json is a JSON array of 9 values in column order
```

### Dependencies

The script requires `google-auth` and `google-api-python-client`. Check if installed:
```
python -c "from google.oauth2 import service_account; print('OK')"
```
If not: `pip install google-auth google-api-python-client`

## Schema

### Columns (in order)

| Column | Description | Values |
|---|---|---|
| Company | Company name | Free text |
| Role | Job title | Free text |
| URL | Link to job posting | URL |
| Status | Current application state | See status values below |
| Priority | How important this application is | `High`, `Medium`, `Low` |
| Deadline | Application deadline | `YYYY-MM-DD` or empty |
| Applied Date | When the application was submitted | `YYYY-MM-DD` or empty |
| Follow-up Date | When to follow up (set by user) | `YYYY-MM-DD` or empty |
| Notes | Any additional context | Free text |

### Status values

- `Found` — discovered but not yet applied
- `Applied` — application submitted
- `Interview` — invited to interview
- `Offer` — received an offer
- `Rejected` — rejected by company
- `Declined` — user declined the opportunity
- `Filled` — position was filled

### Sort order

When writing back, always sort rows in this order:

1. **Active statuses first** (`Found`, `Interview`, `Offer`) — sorted by Deadline ascending (empty deadlines last)
2. **Terminal statuses at the bottom** (`Applied`, `Rejected`, `Declined`, `Filled`) — sorted by Applied Date descending (most recent first)

This keeps actionable items at the top and history at the bottom.

## Operations

### Add a new job

```
1. Read current sheet
2. Check for duplicates — match on Company + Role (case-insensitive)
3. If duplicate found, report it and do not add
4. Append new row with Status = "Found", other fields as provided
5. Re-sort and write back
```

Default values for new rows: Status = `Found`, Priority = `Medium`, dates empty.

### Update a job's status

```
1. Read current sheet
2. Find the row by Company name (case-insensitive partial match is fine)
3. Update the Status field
4. If status is "Applied", set Applied Date to today's date
5. Re-sort and write back
```

### Check for duplicates

Before adding a job, search existing rows for matching Company + Role. Return the existing
row if found so the caller can decide whether to skip or update.

### List jobs by filter

Read the sheet and filter by any column value. Common queries:
- All jobs with status `Found` (not yet applied)
- Jobs with deadlines in the next 7 days
- All jobs with status `Interview` (for interview prep)
- Jobs matching a company name

## Important notes

- Always read the sheet fresh before writing — never work from stale data
- Always re-sort after any modification
- The header row must always be preserved as the first row
- Keep all rows permanently — never delete rows, even terminal statuses
- Dates must be in `YYYY-MM-DD` format for correct sorting
- When the sheet is empty (only headers), simply append the new row
- If the caller provides a status update to `Interview`, suggest running `/interview-prep`
