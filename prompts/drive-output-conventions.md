# Drive Output Conventions

Naming conventions and folder structure for all Drive output. Used by drive-writer
and application-finalizer to ensure consistent, findable file names.

## Application folder naming

```
application-[YYYYMMDD]-[company]-[role]
```

- **Date**: today's date at time of finalization, not the job posting date
- **Company**: lowercase, spaces → hyphens, remove special characters (åäö → aao, etc.)
- **Role**: lowercase, spaces → hyphens, remove special characters, truncate if very long

### Examples
```
application-20260329-spotify-backend-engineer
application-20260401-klarna-data-scientist
application-20260415-voi-technology-senior-ios-developer
application-20260420-svenska-spel-fullstack-utvecklare
```

### Normalizing company and role names
- Remove: `.`, `,`, `(`, `)`, `&`, `/`, `'`, `"`
- Replace spaces with hyphens
- Lowercase everything
- Swedish characters: å→a, ä→a, ö→o (for folder names only — preserve in document content)
- Truncate role to ~4 words if it's very long (keep the most distinctive words)

## Document naming inside the folder

| Document | Name format |
|---|---|
| Tailored CV | `CV - [Company] - [Role]` |
| Cover letter (Swedish posting) | `Personligt brev - [Company] - [Role]` |
| Cover letter (English posting) | `Cover Letter - [Company] - [Role]` |
| Screening answers | `Screening Answers - [Company] - [Role]` |
| Job post archive | `[Company] - [Role] - Job Post` |
| Interview prep | `Interview Prep - [Company] - [Role]` |

Use the human-readable company and role names here (not the normalized folder-name versions).

## Folder location

All application folders are created inside `DRIVE_APPLICATIONS_FOLDER_ID`.

```
applications/
  application-20260329-spotify-backend-engineer/
    CV - Spotify - Backend Engineer
    Personligt brev - Spotify - Backend Engineer
    Spotify - Backend Engineer - Job Post
  application-20260401-klarna-data-scientist/
    CV - Klarna - Data Scientist
    Cover Letter - Klarna - Data Scientist
    Screening Answers - Klarna - Data Scientist
    Klarna - Data Scientist - Job Post
    Interview Prep - Klarna - Data Scientist
```

## Finding existing folders

To locate an existing application folder for a company and role, use:
```
mcp__gdrive__search("application [company] [role]")
```
Filter results to those with `DRIVE_APPLICATIONS_FOLDER_ID` as parent.
Use a partial match — the search doesn't need to be exact.
