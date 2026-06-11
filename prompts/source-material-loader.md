# Source Material Loader

Reusable instructions for loading Drive source material. Referenced by application-drafter
and any skill that needs to load user documents before writing.

## Standard load sequence

Always read config.md first:
```
/Users/maxnerdal/Documents/ai-framework/config.md
```

Then load documents in this order (skip any that aren't needed for the current task):

### 1. Long CV (primary source)
```
mcp__gdrive__read_file(DRIVE_CV_LONG_ID)
```
This is the single source of truth for all experience, skills, and achievements.
Always use this as the base — never the short CV.

### 2. Personal letter (base)
```
mcp__gdrive__read_file(DRIVE_PERSONAL_LETTER_ID)
```
The foundation for all cover letters. Reframe and adapt — don't start from scratch.

### 3. Job profile (preferences)
```
mcp__gdrive__read_file(DRIVE_JOB_PROFILE_ID)
```
Contains target roles, location, salary range, remote preference, and keywords.
Read this when searching for jobs or when screening answers reference salary/availability.

### 4. Work references (for specific examples)
```
mcp__gdrive__search("work reference letter")
```
Filter results to those within DRIVE_WORK_REFERENCES_FOLDER_ID.
Read 1-3 most relevant references. Useful for specific achievements and manager quotes.

### 5. Past applications (style reference)
```
mcp__gdrive__search("CV [role title]") within DRIVE_APPLICATIONS_FOLDER_ID
mcp__gdrive__search("personligt brev [role title]") within DRIVE_APPLICATIONS_FOLDER_ID
```
Read 1-2 past applications for similar roles as style reference.
Past applications guide tone and structure — don't copy content.

## What to do if a config key is FILL_IN

If any Drive ID in config.md shows `FILL_IN`, that document hasn't been set up yet.
Stop and tell the user which key is missing before continuing.

## What to do if a Drive read fails

If `mcp__gdrive__read_file` returns an error:
1. Note the failure in your output
2. Continue with the remaining source material
3. If the long CV fails, stop — it's required for all writing tasks

## Language note

Source material may be in Swedish or English. The output language is always determined
by the job posting, not the source. Translate as needed, preserving proper nouns.
