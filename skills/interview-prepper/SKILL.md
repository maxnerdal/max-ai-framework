---
name: interview-prepper
description: >
  Prepare for a job interview by generating likely questions, talking points, and research
  about the company. Use this skill whenever the user has an upcoming interview, wants to
  prep for a specific role, or when a job's status is set to "Interview". Produces a
  comprehensive prep document saved to Drive. Triggers on: interview prep, preparing for
  interview, "I have an interview at...", practice questions, company research for interview.
---

# interview-prepper

Generate a comprehensive interview preparation document for a specific job. Researches the
company, generates likely interview questions, prepares talking points, and suggests
questions the user can ask the interviewer.

## Inputs

1. **Job object** — from the archived job post in the application folder, or from the tracker
2. **Long CV** — from `DRIVE_CV_LONG_ID`
3. **Tailored CV** — from the application folder (if it exists)
4. **Personal letter** — from the application folder (if it exists)
5. **Work references** — from `DRIVE_WORK_REFERENCES_FOLDER_ID`

## Process

```
1. Identify which job to prep for:
   - If the user specifies a company, find it in the tracker
   - If invoked via /interview-prep, list all jobs with status "Interview" and let
     the user pick
2. Load the job post archive from the application folder
3. Load the user's source material (CV, letter, references) via drive-reader
4. Research the company via WebSearch
5. Generate the prep document
6. Save to Drive inside the existing application folder
```

## Company research

Use `WebSearch` to find:
- What the company does, its products/services, recent news
- Company culture and values (from careers page, Glassdoor, press)
- Recent funding, growth, or strategic changes
- The team or department the role sits in (if discoverable)
- Tech blog posts or engineering culture articles (for technical roles)

Synthesize findings into a brief company overview — the user needs enough context to
speak knowledgeably, not a Wikipedia article.

## Prep document structure

```
# Interview Prep: [Role] at [Company]
Date: [today's date]

## Company Overview
[2-3 paragraphs summarizing the company, its products, recent developments,
and culture. Focus on things the user can reference in conversation.]

## Likely Interview Questions

### Role-specific questions
[5-7 questions based on the job posting's requirements]
For each:
- The question
- A suggested talking point connecting the user's experience to the question
- A specific example from the CV or references to mention

### Behavioral questions
[4-5 STAR-format questions common for this type of role]
For each:
- The question
- A suggested situation/task/action/result from the user's background

### Technical questions (if applicable)
[3-5 technical topics likely to come up based on the tech stack]
For each:
- The topic area
- What the user should review or be ready to discuss
- Relevant experience from the CV

### Culture/values questions
[2-3 questions about working style, team fit, motivation]
For each:
- The question
- An authentic answer grounded in the user's actual preferences and experience

## Questions to Ask the Interviewer
[5-7 thoughtful questions the user can ask]
- Mix of role-specific, team, and company questions
- Avoid questions easily answered by the careers page
- Include at least one question showing the user researched the company

## Key Talking Points
[Bullet list of 5-7 things the user should try to work into the conversation]
- Strongest matches between their experience and the role
- Unique perspectives or experiences that differentiate them
- Specific achievements with numbers

## Potential Weak Spots
[Honest assessment of 2-3 areas where the user's background doesn't perfectly
match the job requirements, with suggested ways to address them]
```

## Writing principles

- **Ground everything in source material.** Talking points must reference real experience.
- **Be specific.** "Mention your work on the payment API migration" is better than
  "Talk about your backend experience."
- **Be honest about gaps.** The weak spots section helps the user prepare rather than
  be caught off guard.
- **Match the interview language.** If the job posting and communication have been in
  Swedish, prep in Swedish. If English, English.

## Saving to Drive

Save the prep document as a Google Doc inside the existing application folder:

```
1. Find the application folder for this job in Drive
   (search for "application-*-[company]-[role]" in DRIVE_APPLICATIONS_FOLDER_ID)
2. Create the doc:
   Name: "Interview Prep - [Company] - [Role]"
   mime_type: application/vnd.google-apps.document
   parent_id: [application folder ID]
```

## Important notes

- The prep document is for the user's eyes only — it can be more casual and direct
  than application documents
- If no application folder exists (e.g., the user applied outside this framework),
  create one following the drive-writer naming convention
- Company research via WebSearch may return outdated info — note the research date
- Encourage the user to practice answers out loud, not just read them
