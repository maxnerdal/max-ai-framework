---
name: drive-writer
description: >
  Write finalized application documents to Google Drive. Use this skill whenever you need
  to save completed CVs, personal letters, or other application documents to Drive. Creates
  a subfolder in the applications folder with the naming convention
  application-[YYYYMMDD]-[company]-[role] and saves all documents as Google Docs inside it.
  Triggers on: saving to Drive, finalizing application, writing documents to Drive,
  creating application folder.
---

# drive-writer

Save finalized application documents to Google Drive as native Google Docs in a structured
subfolder. This skill is only called after the user has approved the drafts — it's the
last step before an application is considered complete.

## Inputs

1. **Tailored CV** — finalized content from cv-tailorer
2. **Personal letter** — finalized content from personal-letter-writer
3. **Screening answers** — if applicable, from screening-answerer
4. **Archived job post** — from job-post-parser (may already be created)
5. **Job object** — for folder naming (company, role)
6. **Profile photo file ID** — from config.md `DRIVE_PROFILE_PHOTO_ID`

## Process

```
1. Read config.md → get DRIVE_APPLICATIONS_FOLDER_ID and DRIVE_PROFILE_PHOTO_ID
2. Create the application subfolder
3. Create each document as a Google Doc inside the subfolder
4. If the job post was already archived as a standalone doc, note that it should
   be moved into this folder (or create a new copy inside it)
5. Return the folder URL and document links
```

## Folder naming convention

```
application-[YYYYMMDD]-[company]-[role]
```

- Date is the date of finalization (today), not the job posting date
- Company name: lowercase, spaces replaced with hyphens, special characters removed
- Role: lowercase, spaces replaced with hyphens, special characters removed

Examples:
- `application-20260329-spotify-backend-engineer`
- `application-20260401-klarna-data-scientist`

## Creating the subfolder

The gdrive MCP doesn't have a "create folder" operation directly, but you can create a
folder by using `mcp__gdrive__create_file` with mime_type `application/vnd.google-apps.folder`:

```
Call mcp__gdrive__create_file with:
  name: "application-[YYYYMMDD]-[company]-[role]"
  mime_type: "application/vnd.google-apps.folder"
  parent_id: DRIVE_APPLICATIONS_FOLDER_ID
```

Save the returned folder ID — all documents go inside it.

## Documents to create

All documents use `mime_type: application/vnd.google-apps.document`,
`parent_id: [subfolder ID]`, and **HTML-formatted content** (see formatting guide below).

### 1. Tailored CV
```
Name: "CV - [Company] - [Role]"
Content: HTML-formatted CV (see CV HTML template below)
```

### 2. Personal letter
```
Name: "Personligt brev - [Company] - [Role]" (or "Cover Letter" if English)
Content: HTML-formatted letter (see letter HTML template below)
```

### 3. Screening answers (if applicable)
```
Name: "Screening Answers - [Company] - [Role]"
Content: HTML with <h2> per question, <p> per answer
```

### 4. Job post archive
```
Name: "[Company] - [Role] - Job Post"
Content: HTML with metadata header, then job post content as structured HTML
```

## HTML formatting

Google Docs renders HTML passed to `mcp__gdrive__create_file`. Use clean, semantic
HTML — no CSS, no inline styles, no classes. Google Docs applies its own defaults.

**HTML templates live in `templates/`** — read them before creating documents:

| Document | Template |
|---|---|
| CV | `templates/cv.html` |
| Personal letter | `templates/letter.html` |
| Job post archive | `templates/job-post.html` |
| Screening answers | No template — use `<h2>` per question, `<p>` per answer |

Read the relevant template, replace `[bracketed]` placeholders with actual content,
and pass the resulting HTML to `mcp__gdrive__create_file`.

### Key HTML rules
- Use `<h1>` for name/title, `<h2>` for sections, `<h3>` for subsections
- Use `<strong>` for bold, `<em>` for italic
- Use `<ul><li>` for bullet lists
- Use `<p>` for paragraphs (not `<br>` between blocks)
- Use `<hr>` for horizontal rules between major sections
- No inline styles, no CSS, no `<div>`, no `<span>`

## Output

After all documents are created, return:

```
Application saved to Drive:

Folder: [folder name]
URL: [Google Drive folder link]

Documents:
- CV: [link]
- Personal letter: [link]
- Screening answers: [link] (if applicable)
- Job post archive: [link]
```

## Important notes

- This skill only runs after user approval — never save drafts to Drive
- Google Docs are the output format — not .docx uploads. The user exports to PDF manually
- Profile photo CANNOT be embedded via the API — Google Docs ignores `<img>` tags in HTML
  content passed through the MCP. The CV template includes a gray placeholder line at the
  top reminding the user to insert it manually (Insert → Image → By URL). Always include
  this placeholder with the actual Drive photo URL so the user can click through quickly
- If creating the folder fails, don't create orphaned documents — report the error
- After drive-writer completes, the application-finalizer agent updates the tracker
