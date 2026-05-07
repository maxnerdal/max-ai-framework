---
name: cv-tailorer
description: >
  Tailor a CV to a specific job posting. Use this skill whenever you need to create a
  customized CV for a job application. Takes the job object from job-post-parser and the
  user's CV from Drive, then suggests targeted changes that strengthen it for the role.
  The user reviews and approves changes before they are applied to a copy of the source doc.
  Triggers on: writing a CV, tailoring a CV, customizing a resume, creating an application CV,
  adapting CV for a role.
---

# cv-tailorer

Produce a tailored CV by copying the user's CV Google Doc and applying targeted edits.
This preserves the user's own formatting, profile photo, and document structure — only
the content is adjusted for the specific role.

## Inputs

1. **Job object** — from job-post-parser (required)
2. **CV** — the user's CV from Drive at `DRIVE_CV_ID` (required)
3. **Past application CVs** — from the applications/ folder (optional, style reference)

## Process

```
1. Read config.md → get DRIVE_CV_ID and DRIVE_CV_FOLDER_ID
2. Load the CV via mcp__gdrive__read_file
3. Optionally search applications/ for CVs from similar roles (use drive-reader skill)
4. Analyze the job object: what does this role emphasize?
5. Identify targeted changes — additions, removals, reordering, rewordings
6. Present changes as a clear suggestion list (see format below)
7. Wait for user approval
8. After approval: the application-finalizer copies the CV doc into the application folder
   and applies the approved changes to the copy
```

## Suggesting changes

Present changes as a numbered list — be specific and surgical. The goal is to strengthen
the CV for this role without rewriting it. Typical changes:

- **Reorder** — move a bullet point or section up because it's more relevant
- **Expand** — add a sentence or bullet that draws out relevant detail already in the CV
- **Condense** — shorten or remove content that's not relevant to this role
- **Reword** — mirror the job posting's language (e.g. "system integrations" → "data integrations")
- **Profile summary** — rewrite the 2-3 sentence profile to reference this company and role explicitly

Format:
```
Suggested CV changes:

1. Profile summary — rewrite to reference [company] and [role] explicitly:
   NEW: "..."

2. Key Skills — move [skill] to top of list (most relevant for this role)

3. Intelliplan bullet — expand to mention [specific thing from job posting]:
   NEW: "..."

4. [Any other targeted change]
```

Keep the list short — 3-6 changes is usually right. Don't suggest cosmetic edits.

## Tailoring principles

**Never invent, only reframe.** Every claim must trace back to something already in the CV.
Reframing real experience in the language of the job posting is the job — fabricating
experience is not.

- Reorder content so the most relevant experience appears first
- Mirror the job posting's language where natural
- Match the posting's language — Swedish posting → Swedish CV, English → English
- Do NOT use em dashes (—) anywhere in the CV

## Important notes

- The CV is the source of truth — never add experience or skills not already there
- Profile photo and formatting are preserved because we copy the source doc, not recreate it
- If the job requires a skill the user doesn't have, don't add it — the personal letter
  handles gaps
- Preserve dates and company names exactly as they appear in the source CV
