---
name: screening-answerer
description: >
  Answer screening questions from job application forms. Use this skill whenever the user
  pastes screening questions from an application form, or when preparing likely answers for
  common application questions (motivation, salary expectations, experience, availability).
  Triggers on: answering application questions, screening questions, application form Q&A,
  "the form asks...", pasted form questions.
---

# screening-answerer

Generate answers to screening questions from job application forms. Uses the job object
and the user's source material to produce authentic, specific answers.

## Inputs

1. **Screening questions** — pasted by the user from the application form (required)
2. **Job object** — from job-post-parser (required)
3. **Long CV** — from Drive at `DRIVE_CV_LONG_ID`
4. **Base personal letter** — from Drive at `DRIVE_PERSONAL_LETTER_ID`
5. **Work references** — from `DRIVE_WORK_REFERENCES_FOLDER_ID` (for concrete examples)

## Process

```
1. Read config.md → load source material via drive-reader
2. Categorize each question (see question types below)
3. Draft an answer for each question using source material
4. Present all answers for user review before finalizing
```

## Question types and how to handle them

### Motivation / "Why do you want this role?"
- Draw from the job object (what makes the role interesting) and the user's background
  (what connects their experience to this company/role)
- Be specific — reference the company's product, mission, or team
- Never write generic motivation — tie it to real details

### Experience / "Describe your experience with X"
- Search the CV and work references for relevant experience
- Use specific projects, technologies, durations, and outcomes
- If the user doesn't have direct experience, say so honestly and describe
  adjacent experience

### Salary expectations
- If the job profile has salary info, use that range
- Otherwise, give a reasonable range or say "open to discussion"
- Match currency and format to the posting's country

### Availability / start date
- Default to "flexible" unless the user has specified otherwise
- If the user has noted availability constraints in their profile, use those

### Years of experience
- Calculate from the CV's work history — count relevant roles only
- Be accurate — don't round up

### Technical questions
- Answer based on what's in the CV and work references
- Be specific about versions, tools, and contexts where possible
- Don't claim expertise the user doesn't have

### Free-form / "Tell us about yourself"
- Treat like a condensed personal letter — 3-4 sentences connecting background to role
- Reuse themes from the personal letter but don't copy it verbatim

### Yes/No or multiple choice
- Answer directly based on the CV and job profile
- Add a brief clarification if helpful (e.g., "Yes — I have 3 years of Python experience")

## Writing principles

Same as the other writing skills: **never invent, only reframe.**

- Every answer must be grounded in the user's actual source material
- Match the language of the application form (Swedish or English)
- Be concise — most form fields have character limits. Aim for the most impactful answer
  in the fewest words unless the question explicitly asks for detail
- Professional but human — not robotic template answers

## Output

Present all Q&A pairs clearly:

```
**Q1: Why are you interested in this role?**
A: [answer]

**Q2: Describe your experience with distributed systems.**
A: [answer]

...
```

Ask the user to review and adjust before these get submitted. Screening answers are
often the first impression — they should be accurate and polished.

## Proactive common questions

Even before the user pastes actual screening questions, the application-drafter agent
may ask this skill to prepare likely answers for common question types (motivation,
salary, experience level, availability) as a starting point. These drafts save time
if the form does ask these questions.

## Important notes

- Character limits matter — if the user mentions a limit, respect it strictly
- Some forms have fields for links (portfolio, LinkedIn, GitHub) — remind the user
  to fill those in manually since we don't store those URLs in source material
- Never submit answers automatically — always present for user review first
