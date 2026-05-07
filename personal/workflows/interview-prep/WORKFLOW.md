# Workflow: Interview Prep

Generates a comprehensive interview preparation document for a job with Interview status
in the tracker. Researches the company, creates likely questions with talking points, and
saves the prep doc to Drive inside the existing application folder.

## Invocation

`/interview-prep` — no arguments needed

Claude reads the tracker, lists all jobs with Interview status, and lets the user pick.

---

## Step 1: List Interview-status jobs

Delegate to the `interview-preparer` subagent with no arguments.

The preparer reads the tracker and presents all jobs with Status = `Interview`:

```
Jobs ready for interview prep:
1. [Company] — [Role]
2. [Company] — [Role]
...
```

**Wait here.** Do not generate anything until the user picks a job.

---

## Step 2: Generate prep (autonomous)

Once the user picks a job, the `interview-preparer` subagent continues:

- Loads the archived job post, tailored CV, and personal letter from the application folder
- Loads work references from Drive
- Researches the company via web search
- Generates the full prep document:
  - Company overview
  - Role-specific questions with talking points
  - Behavioral questions (STAR format)
  - Technical topics (if applicable)
  - Questions to ask the interviewer
  - Key talking points
  - Honest weak spot assessment
- Saves the prep doc to Drive inside the application folder

---

## Step 3: Confirm

Report the Drive link to the prep document.

Encourage the user to:
- Read through it before the interview
- Practice answers out loud
- Review the company overview section day-of

---

## Error handling

- If no jobs have Interview status: tell the user and suggest running
  `/update-application <company> interview` first
- If the application folder is not found in Drive: create one and note it
- If company research returns limited results: note the limitation in the prep doc
