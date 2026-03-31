---
name: job-post-parser
description: >
  Parse a job posting from a URL or pasted text into a structured job object. Use this skill
  whenever you receive a job posting link, pasted job ad text, or need to extract structured
  data from a job listing. Also archives the parsed job post to Google Drive so the content
  is preserved after the original posting goes offline. Triggers on: parsing job posts,
  extracting job details from URLs, structuring job ad data, archiving job listings.
---

# job-post-parser

Parse job postings into a structured job object that all downstream skills consume.
This skill defines the shared schema — cv-tailorer, personal-letter-writer, screening-answerer,
and interview-prepper all depend on it.

## Input modes

### From URL
```
1. Call WebFetch with the URL and prompt: "Extract the full job posting content including
   company name, job title, location, responsibilities, requirements, qualifications,
   benefits, application deadline, and any other relevant details. Return the complete
   text, preserving structure."
2. Parse the fetched content into the job object schema below
```

### From pasted text
```
1. Take the pasted text as-is
2. Parse it into the job object schema below
```

## Job object schema

This is the shared schema used across the framework. All fields are strings unless noted.

```
job_object:
  company:          Company name
  role:             Job title exactly as posted
  location:         City/region, or "Remote"
  remote:           "Yes", "No", "Hybrid", or "Not specified"
  employment_type:  "Full-time", "Part-time", "Contract", "Internship", or "Not specified"
  language:         Language the posting is written in (e.g., "Swedish", "English")

  description:      Brief summary of what the role is about (2-3 sentences)
  responsibilities: List of key responsibilities (array of strings)
  requirements:     List of required qualifications (array of strings)
  nice_to_have:     List of preferred/bonus qualifications (array of strings)
  tech_stack:       Technologies, tools, or frameworks mentioned (array of strings)

  salary:           Salary info if mentioned, or "Not specified"
  benefits:         List of benefits mentioned (array of strings)
  deadline:         Application deadline in YYYY-MM-DD if found, or "Not specified"
  url:              Original posting URL, or "Pasted text"

  raw_text:         The full original posting text, preserved for reference
```

## Parsing guidelines

- **Extract what's there, don't invent.** If a field isn't mentioned in the posting, use
  "Not specified" for strings or an empty array for lists. Never guess or fill in plausible
  values.
- **Preserve the original language.** If the posting is in Swedish, keep `description`,
  `responsibilities`, `requirements`, etc. in Swedish. The `language` field records which
  language was detected.
- **Separate requirements from nice-to-haves.** Postings often mix "must have" and "good to
  have" — split them based on language cues ("required", "must", "krav" vs. "meriterande",
  "bonus", "nice to have", "plus").
- **Normalize the deadline.** Convert any date format to `YYYY-MM-DD`. If the posting says
  "ongoing" or "as soon as possible", set deadline to "Not specified".
- **Keep raw_text complete.** This is the archival copy. Include everything from the posting,
  even boilerplate and legal text.

## Archiving to Drive

After parsing, archive the job post as a Google Doc so the content is preserved even after
the original posting goes offline. This happens during the application workflow — not
standalone parsing.

```
1. Read config.md → get DRIVE_APPLICATIONS_FOLDER_ID
2. Create a Google Doc named "[Company] - [Role] - Job Post"
3. Content: the raw_text field, with a header showing the URL and parse date
4. Save the file ID — drive-writer will move it into the application subfolder later
```

Use `mcp__gdrive__create_file` with mime_type `application/vnd.google-apps.document`.

## Output

Return the job object as a structured block that the caller can reference. Present it
clearly so the user can verify the extraction is correct before downstream skills use it.

Example output format:

```
**Company:** Spotify
**Role:** Backend Engineer
**Location:** Stockholm
**Remote:** Hybrid
**Language:** English
**Deadline:** 2026-04-15

**Description:** Spotify is looking for a backend engineer to join the
content delivery team...

**Requirements:**
- 3+ years experience with distributed systems
- Proficiency in Java or Python
- ...

**Nice to have:**
- Experience with Kubernetes
- ...

**Tech stack:** Java, Python, GCP, Kubernetes, gRPC
```

## Important notes

- The job object schema is the contract between this skill and all writer skills — do not
  add or rename fields without updating downstream consumers
- If WebFetch fails (e.g., the page requires authentication or is behind a paywall), ask
  the user to paste the job posting text instead
- Some job sites load content dynamically — if the fetched content looks incomplete or
  like a login page, tell the user and ask them to paste the text
