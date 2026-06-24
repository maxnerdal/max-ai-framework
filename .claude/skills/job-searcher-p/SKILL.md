---
name: job-searcher
description: >
  Search the web for job postings matching the user's job profile. Use this skill whenever
  the user wants to find new jobs, discover open positions, run a job search, or when the
  /job-application workflow is invoked without a specific URL. Reads the job profile from
  Google Drive, searches the web, filters out duplicates already in the tracker, and adds
  new matches. Triggers on: finding jobs, searching for positions, job discovery, "any new
  jobs?", running automatic job search.
---

# job-searcher

Search the web for job postings that match the user's job profile, check the tracker for
duplicates, and present a shortlist of new matches.

## How it works

```
1. Load the job profile from Drive (preferences, target roles, keywords)
2. Build search queries from the profile
3. Search the web using WebSearch
4. Parse each result into a job object (using job-post-parser logic)
5. Check the tracker for duplicates
6. Add new matches to the tracker with status "Found"
7. Present the shortlist to the user
```

## Step 1: Load job profile

```
1. Read config.md → get DRIVE_JOB_PROFILE_ID
2. Call mcp__gdrive__read_file to load the profile
3. Extract: target roles, location, remote preference, keywords, industries, salary range
```

The profile is a Google Doc with sections like "Target Roles", "Location", "Keywords", etc.
Use all of these to construct targeted search queries.

## Step 2: Build search queries

Construct 3-5 WebSearch queries that cover the profile from different angles. Vary the
queries to maximize coverage:

- Combine role titles with location (e.g., "backend developer Stockholm")
- Use industry-specific terms (e.g., "fintech engineer Sweden remote")
- Include Swedish and English variants if the profile suggests both languages
- Add "job" or "ledigt jobb" to help search engines surface job listings

Good queries are specific enough to return relevant results but broad enough to catch
postings with different wordings for similar roles.

## Step 3: Search the web

Call `WebSearch` for each query. For each search result:

- Look at the title and snippet to quickly assess relevance
- Discard results that are clearly not job postings (blog posts, salary surveys, company pages)
- For promising results, call `WebFetch` to get the full posting content

Aim for 5-10 candidate postings across all queries. Don't over-fetch — quality over quantity.

## Step 4: Parse results

For each fetched posting, extract the key fields from the job object schema (defined in
job-post-parser):

- Company, Role, Location, Remote, Deadline
- Brief description (2-3 sentences)

You don't need the full job object at this stage — just enough to present a shortlist.
The full parse happens when the user selects a job to apply for.

## Step 5: Check for duplicates

```
1. Read the job tracker (use job-tracker skill)
2. For each candidate, check if Company + Role already exists (case-insensitive)
3. Skip duplicates — don't add or present them
```

If a duplicate is found with a terminal status (Rejected, Declined, Filled), still skip it
— the user already dealt with that posting.

## Step 6: Add to tracker

For each new (non-duplicate) match:
```
1. Add a row to the tracker with:
   - Company and Role from the posting
   - URL from the search result
   - Status = "Found"
   - Priority = "Medium" (user can adjust later)
   - Deadline if found in the posting
   - Notes = brief 1-line summary
2. Re-sort and write back (per job-tracker skill)
```

## Step 7: Present the shortlist

Show the user a numbered list of new matches, prioritized by:
1. Jobs with deadlines in the next 7 days (flagged as urgent)
2. Jobs with deadlines further out
3. Jobs with no deadline

For each job, show:
```
1. [Company] — [Role]
   Location: [Location] | Remote: [Yes/No/Hybrid]
   Deadline: [date or "Not specified"]
   Summary: [1-2 sentence description]
   URL: [link]
```

End with a prompt like: "Which job(s) would you like to apply for? Give me the number(s)
or paste a different URL."

## When no results are found

If the search returns no new relevant postings:
- Tell the user clearly — "No new matches found for your current profile."
- Suggest they update their job profile if they want to broaden the search
- Mention when the last search was run (check tracker for most recent "Found" entries)

## Important notes

- Always load the job profile fresh — the user may have updated their preferences
- Search results are time-sensitive — job postings appear and disappear quickly
- Some search results may point to aggregator sites (LinkedIn, Indeed) which may not
  render well via WebFetch — extract what you can from the search snippet in that case
- The user's profile may contain both Swedish and English terms — search in both languages
- Don't overwhelm the user — cap the shortlist at ~10 jobs per search session
