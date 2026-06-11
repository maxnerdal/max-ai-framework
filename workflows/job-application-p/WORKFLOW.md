# Workflow: Job Application

End-to-end job application workflow. Takes a job post (URL or pasted text) or runs an
automatic search, produces tailored drafts, waits for user review, then finalizes and
saves to Drive.

## Invocation modes

### Automatic search mode
`/job-application` — no arguments

Claude reads the job profile, searches the web, checks the tracker for duplicates, and
presents a shortlist of new matches for the user to choose from.

### Manual mode
`/job-application <url>` or multiple URLs

Skips the search. Goes straight to drafting for the provided job post(s).

---

## Step 1: Intake

**Automatic mode:**
Invoke the `job-searcher` skill:
1. Read config.md → load job profile from Drive
2. Search the web for matching postings
3. Check tracker for duplicates
4. Add new matches to tracker with status `Found`
5. Present shortlist ordered by deadline (urgent first)

Ask: "Which job(s) would you like to apply for? Give me the number(s) or paste a URL."

Wait for the user's selection before continuing.

**Manual mode:**
Skip search. Proceed directly to Step 2 with the provided URL(s).

---

## Step 2: Draft (autonomous)

Delegate to the `application-drafter` subagent with the job URL or posting text.

The drafter runs autonomously:
- Loads all source material from Drive
- Parses the job post
- Searches past applications for style references
- Tailors the CV
- Writes the personal letter
- Prepares likely screening answers

The drafter presents all drafts in the conversation and ends with the review checkpoint.

---

## Step 3: Review checkpoint (human)

The drafter asks: "Did the application form have any screening questions? Paste them
here if so. Otherwise say 'looks good' or give specific feedback."

**Wait here.** Do not proceed until the user responds.

Possible responses:
- "Looks good" → proceed to Step 5
- Specific feedback → apply changes (Step 4), then re-present for confirmation
- Pasted screening questions → answer them (Step 4), then re-present

---

## Step 4: Feedback loop (if needed)

Apply the user's feedback:
- For CV or letter changes: make targeted edits, re-present the changed sections
- For screening questions: invoke `screening-answerer` skill with the pasted questions
  and present the answers

Ask: "Anything else, or shall I save this to Drive?"

Repeat until the user confirms everything is ready.

---

## Step 5: Finalize

Delegate to the `application-finalizer` subagent.

The finalizer:
- Applies any final edits
- Creates the application subfolder in Drive
- Saves CV, personal letter, screening answers, and job post archive as Google Docs
- Updates the tracker row to `Applied` with today's date

---

## Step 6: Confirm

Report the folder URL and document links (returned by the finalizer).

Remind the user:
- Export CV and letter to PDF before submitting
- Set a follow-up date in the tracker if relevant
- Run `/interview-prep` if they get invited to interview

---

## Error handling

- If WebFetch fails on a URL: ask user to paste the job text
- If a Drive read fails: report the specific error, continue with available material
- If the tracker write fails: report it, the application folder is still saved
