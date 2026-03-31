---
name: drive-reader
description: >
  Read documents from Google Drive by name or file ID. Use this skill whenever you need to
  load source material from Drive — CVs, personal letters, work references, project summaries,
  job profiles, education results, or past application documents. Also use it to search the
  applications folder for previous CVs and cover letters to use as style references.
  Triggers on: reading Drive files, loading source material, fetching CV/letter/references,
  searching past applications, anything that requires config.md Drive IDs.
---

# drive-reader

Read documents from Google Drive using the gdrive MCP tools. This is the foundational
I/O skill — most other skills in this framework depend on it to load source material.

## How it works

1. Read `config.md` to resolve a document name to its Drive file ID
2. Call `mcp__gdrive__read_file` with that ID
3. Return the content (Google Docs come back as markdown, Sheets as CSV)

## Config file

All Drive IDs live in `/Users/maxnerdal/Documents/ai-framework/config.md`.
Read this file first whenever you need a Drive ID. The format is `KEY=value`, one per line.

### Available config keys

| Key | What it points to |
|---|---|
| `DRIVE_ROOT_ID` | Root folder of Max's Drive workspace |
| `DRIVE_CV_FOLDER_ID` | Folder containing CV documents |
| `DRIVE_CV_SHORT_ID` | Short/one-page CV |
| `DRIVE_CV_LONG_ID` | Full detailed CV (primary source for tailoring) |
| `DRIVE_PERSONAL_LETTER_ID` | Base personal/cover letter |
| `DRIVE_APPLICATIONS_FOLDER_ID` | Folder with past application subfolders |
| `DRIVE_PROJECTS_FOLDER_ID` | Project summaries and portfolio |
| `DRIVE_RESULTS_FOLDER_ID` | Education results (parent folder) |
| `DRIVE_RESULTS_GYMNASIUM_ID` | Gymnasium grades |
| `DRIVE_RESULTS_UNIVERSITY_ID` | University transcripts |
| `DRIVE_RESULTS_YRKESHOGSKOLA_ID` | YH (vocational) transcripts |
| `DRIVE_WORK_REFERENCES_FOLDER_ID` | Work reference letters |
| `DRIVE_PROFILE_PIC_FOLDER_ID` | Profile photo folder |
| `DRIVE_PROFILE_PHOTO_ID` | Profile photo file |
| `DRIVE_JOB_PROFILE_ID` | Job search preferences and target roles |
| `DRIVE_JOB_TRACKER_ID` | Job application tracker (Google Sheet) |

### Resolving human-readable names

When the caller asks for a document by name, map it to the right config key:

- "long CV", "full CV", "detailed CV" → `DRIVE_CV_LONG_ID`
- "short CV", "one-page CV" → `DRIVE_CV_SHORT_ID`
- "personal letter", "cover letter", "base letter" → `DRIVE_PERSONAL_LETTER_ID`
- "job profile", "search preferences" → `DRIVE_JOB_PROFILE_ID`
- "job tracker", "application tracker" → `DRIVE_JOB_TRACKER_ID`
- "work references" → `DRIVE_WORK_REFERENCES_FOLDER_ID` (folder — list contents first)
- "projects", "portfolio" → `DRIVE_PROJECTS_FOLDER_ID` (folder — list contents first)
- "profile photo" → `DRIVE_PROFILE_PHOTO_ID`

## Reading a single document

```
1. Read config.md → extract the relevant file ID
2. Call mcp__gdrive__read_file with that ID
3. Return the content
```

## Reading from a folder

For folder IDs (work references, projects, results), you need to list the contents first
since `read_file` only works on individual files:

```
1. Read config.md → extract the folder ID
2. Call mcp__gdrive__search with a query scoped to that folder
3. Read each relevant file by its ID
```

When searching within a folder, use `mcp__gdrive__search` with the document name or type.
The search covers all of the user's Drive, so look at the parent folder of results to
confirm they came from the expected location.

## Searching past applications

Past applications live in subfolders under `DRIVE_APPLICATIONS_FOLDER_ID`. Each subfolder
is named `application-[YYYYMMDD]-[company]-[role]`.

To find past applications for style reference:

```
1. Read config.md → get DRIVE_APPLICATIONS_FOLDER_ID
2. Search for relevant terms (e.g., "CV", "personligt brev", company name, role title)
3. Filter results to those within the applications folder
4. Read the most relevant matches
```

This is useful when tailoring new CVs or letters — well-performing past applications
serve as style references for tone, structure, and emphasis.

## Important notes

- Always read `config.md` fresh rather than caching IDs — the user may update it
- Google Docs are returned as markdown, Sheets as CSV, Presentations as plain text
- If a config key shows `FILL_IN`, that document hasn't been set up yet — tell the user
- The language of documents varies (Swedish and English) — preserve the original language
- For large documents, the full content is returned; there is no pagination
