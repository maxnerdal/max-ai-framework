---
name: personal-letter-writer
description: >
  Write a tailored personal letter (cover letter) for a job application. Use this skill
  whenever you need to create a cover letter, motivation letter, or personal letter for a
  job application. Takes the job object and the user's base personal letter from Drive,
  then suggests targeted changes that adapt it to the specific role while keeping the
  user's own voice and structure intact.
  Triggers on: writing a cover letter, personal letter, motivation letter, "personligt brev",
  creating an application letter.
---

# personal-letter-writer

Produce a tailored personal letter by copying the user's base personal letter and applying
targeted edits. The user's own voice, structure, and core content are preserved — only
the role-specific parts are adjusted.

## Inputs

1. **Job object** — from job-post-parser (required)
2. **Base personal letter** — from Drive at `DRIVE_PERSONAL_LETTER_ID` (required)
3. **CV** — from Drive at `DRIVE_CV_ID` (for additional detail to draw from)
4. **Work references** — from `DRIVE_WORK_REFERENCES_FOLDER_ID` (for specific examples)
5. **Past application letters** — from applications/ folder (optional, style reference)

## How the base letter works

The base letter has two types of content:

1. **Fixed sections** — paragraphs the user has written and wants to keep as-is. Do not touch these unless the user explicitly asks. They represent the user's own voice and core arguments.

2. **Bracketed placeholders** — sections marked like `[någon mening om varför man intresserar sig av tjänsten]` or `[här berättar jag att jag har läst det arbetsgivaren är ute efter]`. These are explicit prompts from the user — they must always be filled in with role-specific content.

Always fill every bracket. Never leave a placeholder in the output.

## Process

```
1. Read config.md → get DRIVE_PERSONAL_LETTER_ID, DRIVE_CV_ID,
   DRIVE_WORK_REFERENCES_FOLDER_ID
2. Load the base personal letter via mcp__gdrive__read_file
3. Load the CV for additional detail
4. Optionally load work references for concrete examples
5. Optionally search applications/ for letters from similar roles (drive-reader skill)
6. Analyze the job object: what is this company looking for?
7. Identify every bracketed placeholder and write role-specific content for each
8. Note any other targeted changes that would strengthen the letter for this role
9. Present the complete filled letter with all brackets replaced
10. After approval: the application-finalizer copies the letter doc and applies the changes
```

## Suggesting changes

Present the complete letter with all brackets filled in. Alongside it, call out what you changed so the user can review clearly:

Format:
```
Suggested letter — brackets filled + any other changes:

[Full letter text with all brackets replaced by actual content]

---

Changes made:
- [Bracket 1 description] → filled with: "..."
- [Bracket 2 description] → filled with: "..."
- [Any other change, if made] — [reason]
```

Outside of filling brackets, keep other changes minimal. The fixed sections stay as-is unless there's a strong reason to suggest an edit (e.g. the role name appears incorrectly, or a fixed paragraph is clearly irrelevant to this role).

## Writing principles

**Never invent, only reframe.** Every claim must trace back to the base letter, CV, or
work references. Do not fabricate projects, achievements, or motivations.

- Connect the user's actual experience to the role's specific requirements
- Name the company and role explicitly — no generic statements
- Show, don't tell — reference specific work rather than claiming traits
- Address gaps honestly: adjacent experience or genuine willingness to learn is fine;
  pretending to have a skill is not
- Match the job posting's language — Swedish posting → Swedish letter, English → English
- Do NOT use em dashes (—) anywhere in the letter

## Tone and style

- Professional but personal — a letter from a human, not a template
- Confident without arrogance — state achievements factually
- Concise — aim for 350-450 words total
- Match formality to the company: startup → slightly casual, enterprise → more formal

## Important notes

- The base personal letter is the source of truth for voice and structure
- Work references can provide powerful specific examples — use results or context from
  managers when relevant, but paraphrase rather than copy verbatim
- Date format follows the letter's language: "29 mars 2026" (Swedish) or "March 29, 2026" (English)
- If the user has given feedback on previous letters in this session, apply those preferences
