# Plan: Job Application Workflow

## Context
The user wants a full job application workflow in their ai-framework. The workflow goes from a job post (URL or pasted text) all the way to polished documents saved in Google Drive, with a human review step in the middle. The framework uses skills (SKILL.md), agents, and workflows as layers of abstraction — built with the `skill-creator` plugin.

---

## Architecture

The framework follows a three-layer pattern that aligns with industry best practice
across Claude, Gemini, OpenAI, and other agentic frameworks:

- **Skills** — atomic capabilities (portable, LLM-agnostic)
- **Agents** — autonomous multi-skill pipelines (Claude Code subagents, own context window)
- **Workflows** — multi-step orchestration with human checkpoints (portable, LLM-agnostic)
- **Commands** — thin entry points that invoke workflows (Claude Code specific)
- **Prompts** — shared writing principles referenced by skills (portable)

```
skills/                                — Atomic capabilities (portable across Claude, Gemini, OpenAI)
  drive-reader/
    SKILL.md                           — Read Drive docs by ID; optionally search applications/ for past CVs/letters
  job-tracker/
    SKILL.md                           — Read/write job tracker Google Sheet; sorts by deadline, applied jobs at bottom
  job-post-parser/
    SKILL.md                           — URL or pasted text → structured job object + archive to Drive
  job-searcher/
    SKILL.md                           — Read job profile from Drive, search web, return matching posts
  cv-tailorer/
    SKILL.md                           — Job object + CV source (+ optional past applications) → tailored CV
  personal-letter-writer/
    SKILL.md                           — Job object + letter reference (+ optional past letters) → cover letter
  screening-answerer/
    SKILL.md                           — Job object + source material → Q&A answers
  drive-writer/
    SKILL.md                           — Documents → new subfolder named application-[YYYYMMDD]-[company]-[role]
  interview-prepper/
    SKILL.md                           — Job object + company research + user source material → interview prep doc

workflows/                             — Multi-step orchestration with human checkpoints (portable, LLM-agnostic)
  job-application/
    WORKFLOW.md                        — Full instructions for end-to-end job application
  interview-prep/
    WORKFLOW.md                        — Full instructions for interview preparation
  update-application/
    WORKFLOW.md                        — Instructions for updating job tracker status

prompts/                               — Shared writing principles referenced by skills (portable)
  source-material-loader.md            — Reusable instructions for loading Drive source material
  tailoring-principles.md              — Shared writing philosophy (never invent, only reframe)
  drive-output-conventions.md          — Folder naming: application-[YYYYMMDD]-[company]-[role]

templates/                             — HTML templates for Google Docs output (portable)
  cv.html                              — CV structure and formatting
  letter.html                          — Personal letter / cover letter formatting
  job-post.html                        — Archived job post formatting

.claude/                               — Claude Code specific configuration
  agents/                              — Autonomous pipelines (subagents with own context window)
    application-drafter.md             — Runs full drafting pipeline, stops before Drive write
    application-finalizer.md           — Applies user feedback, writes to Drive, updates tracker to Applied
    interview-preparer.md              — Reads tracker for Interview-status jobs, generates prep doc
  commands/                            — Thin entry points that invoke workflows
    job-application.md                 — Slash command: reads and executes workflows/job-application/WORKFLOW.md
    interview-prep.md                  — Slash command: reads and executes workflows/interview-prep/WORKFLOW.md
    update-application.md              — Slash command: reads and executes workflows/update-application/WORKFLOW.md
```

---

## Workflow steps (what the user experiences)

### `/job-application` workflow
1. **Intake** — two modes:
   - *Automatic:* `/job-application` — Claude reads job profile, searches web, checks tracker for duplicates, adds new matches as `Found`, shows jobs with deadlines in next 7 days first, presents shortlist for user to pick from
   - *Manual:* `/job-application <url>` or multiple URLs — skips search, checks tracker for duplicates, proceeds to draft
2. **Draft** — `application-drafter` runs autonomously: reads long CV, personal letter, work references, project summaries, searches past `applications/` for similar roles as style reference, parses and archives job post to Drive
3. **Review checkpoint** — Claude presents all drafts; asks if application form had screening questions (paste them if so)
4. **Feedback** — user says "looks good" or gives specific changes
5. **Finalize** — `application-finalizer` applies changes, saves to `applications/application-[YYYYMMDD]-[company]-[role]/`, updates tracker row to `Applied` with date
6. **Confirm** — Claude reports folder URL and document links; reminds user to set priority and follow-up date in tracker

### `/interview-prep` workflow
1. Claude reads tracker, lists all jobs with status `Interview`
2. User picks which job to prep for
3. `interview-preparer` agent researches the company, generates likely interview questions, prepares talking points connecting user's experience to the role, suggests questions to ask the interviewer
4. Saves prep doc to Drive inside the existing application folder for that job

### `/update-application` command (v1 manual status update)
- Usage: `/update-application <company> <status>` e.g. `/update-application spotify interview`
- Updates tracker row status and timestamp
- If status is `Interview`, prompts user to run `/interview-prep`
- Statuses `Filled`, `Rejected`, `Declined` stay in tracker for history but sort to bottom of sheet

---

## Build order

Skills must be built in this order (each depends on the previous):

1. `drive-reader` — foundational I/O, all others depend on it
2. `job-tracker` — read/write Google Sheet; needed early since both `job-searcher` and `application-finalizer` depend on it
3. `job-post-parser` — defines the shared job object schema all writers consume
4. `job-searcher` — reads job profile from Drive, checks tracker for duplicates, searches web, adds new rows
5. `cv-tailorer` + `personal-letter-writer` — can be built in parallel
6. `screening-answerer` — simplest logic, built after the writers
7. `drive-writer` — last skill, only needed at finalization
8. `interview-prepper` — can be built after drive-reader and job-post-parser are stable
9. `application-drafter` agent (`.claude/agents/`) — after all input-side skills are stable
10. `application-finalizer` agent (`.claude/agents/`) — after `drive-writer` and `job-tracker` are stable
11. `interview-preparer` agent (`.claude/agents/`) — after `interview-prepper` skill is stable
12. `job-application` + `interview-prep` workflows + commands — last, pure orchestration

Each skill is built using `/skill-creator` (installed plugin).

---

## Key design decisions

- **Screening questions are manually provided in v1** — after clicking Apply and seeing the form, user pastes questions to Claude; the review checkpoint explicitly asks "did the form have screening questions?". Claude may also prepare likely answers for common question types (motivation, salary, experience) as a starting point even without explicit questions.
- **Draft bundle never touches Drive** — the drafter agent assembles all documents in context; Drive writes only happen after user approval via the finalizer
- **Human review is conversational** — Claude presents drafts in the terminal and waits for a response; no async file-based handoff needed
- **Shared job object schema** — defined in `job-post-parser`, used by all three writing skills; must be stable before writers are built
- **config.md is the single source of Drive IDs** — every skill that touches Drive reads it first; path is always `/Users/maxnerdal/Documents/ai-framework/config.md`
- **Job profile lives in Google Drive** — preferences (target roles, location, company size, salary, keywords) stored as a Google Doc at `DRIVE_JOB_PROFILE_ID`; `config.example.md` and `config.md` must be updated to include this key
- **Job tracker is a Google Sheet** — one row per job; columns: Company, Role, URL, Status, Priority, Deadline, Applied date, Follow-up date, Notes. Status values: `Found`, `Applied`, `Rejected`, `Interview`, `Offer`, `Declined`, `Filled`. Priority: `High`, `Medium`, `Low`. Stored at `DRIVE_JOB_TRACKER_ID` in config. Sorted by deadline ascending; terminal statuses (`Applied`, `Rejected`, `Declined`, `Filled`) pinned to bottom. All rows kept permanently for history. Follow-up dates set manually by user.
- **One base CV** — always use `cv` (`DRIVE_CV_ID`) as the source; the workflow copies this file into the application folder and edits the copy
- **CV and letter workflow: copy-and-suggest, not rewrite** — Instead of generating documents from scratch using HTML templates, the workflow copies the user's actual Google Doc files (`cv-long` and the base personal letter) using the Drive API, then suggests targeted changes to strengthen them for the specific role. The user reviews the suggestions, approves or adjusts, and only then are the changes applied to the copy. This preserves the user's own formatting (including profile photo), keeps the core content intact, and gives the user full control. The `templates/` directory and HTML-based approach are replaced by this copy-and-edit model.
- **Job posts archived to Drive** — `job-post-parser` saves raw parsed job object as a doc inside the application folder so content is preserved after the posting goes offline
- **Email status updates are manual in v1** — user runs `/update-application <company> <status>` in terminal; v2 will automate via Gmail MCP
- **Work references included** — `application-drafter` reads `DRIVE_WORK_REFERENCES_FOLDER_ID` and includes relevant references in the draft bundle
- **Language follows the job post** — if the posting is in Swedish, all output is in Swedish; if English, English
- **Output format is Google Docs → PDF** — `drive-writer` creates native Google Docs (not .docx uploads); user exports to PDF before sending. Google Docs supports photo embedding and is already natively in Drive.
- **CV design: clean single-column** — bold section headings, no colour, no icons, generous whitespace. Profile photo top-left, name and contact details alongside it.
- **Profile photo stored in Drive** — located in "Max's Portfolio/profil-pic/"; folder and file IDs to be looked up and added to config as `DRIVE_PROFILE_PIC_FOLDER_ID` and `DRIVE_PROFILE_PHOTO_ID`. `cv-tailorer` instructs drive-writer to embed the photo at the top of every CV.
- **Three-layer architecture (skills → agents → workflows)** — follows Anthropic's recommended pattern, also used by OpenAI, Google Gemini, CrewAI, and Microsoft. Skills are atomic and portable (work across LLMs). Agents are autonomous pipelines in `.claude/agents/` (Claude Code subagents with own context window). Workflows define orchestration with human checkpoints (portable). Commands in `.claude/commands/` are thin wrappers that invoke workflows. This separation keeps the framework portable — skills, workflows, and prompts transfer to other LLMs; only `.claude/` is vendor-specific.

---

## V1 fixes

All resolved. ✓

- **Copy-and-suggest workflow** — implemented via `gdrive.py` script and updated agents. Drafter suggests targeted changes; finalizer copies source docs and applies them.
- **Base personal letter** — user's own letter in Drive at `DRIVE_PERSONAL_LETTER_ID`.

---

## Version 2 (deferred)

These features are out of scope for v1 but should be designed with them in mind:

1. **Messaging integration** — connect Telegram, Discord, or WhatsApp so the user can interact with the workflow conversationally from their phone (trigger searches, review drafts, approve applications)
2. **Job discovery UI** — a lightweight interface to review newly discovered jobs, mark them relevant/irrelevant, and add keywords back to the job profile for better future matching
3. **Scheduled search** — run the job-searcher automatically every other morning and notify the user of new matches (uses Claude Code scheduling)
4. **Draft review UI** — easy-access interface to read and approve application drafts without being in the terminal
5. **Browser automation for screening questions** — use Playwright MCP to log in via Google OAuth, navigate application forms, and extract screening questions automatically. Handles platforms that support "Sign in with Google". Replaces the manual paste step for supported platforms.
6. **Gmail MCP for automatic status updates** — scan inbox for replies from companies in the tracker, detect interview invites and rejections, update tracker status automatically

> Note for v1 design: keep workflow state (tracker sheet, draft bundles) in clean, readable formats so a UI layer can be added on top without reworking the underlying skills.

---

## Files to create/update outside the workflow

- `README.md` (repo root) — update skills table, add workflows and commands sections
- `config.example.md` — add `DRIVE_JOB_PROFILE_ID`, `DRIVE_JOB_TRACKER_ID`, and `DRIVE_PROFILE_PHOTO_ID` keys
- `config.md` — add same keys once Google Sheet and job profile doc are created in Drive
- `SETUP.md` — no changes needed

## Verification

After building:
- Run `/skill-creator` in eval mode on each skill with a real job post URL
- Run the full `/job-application` workflow end-to-end with a test job post
- Confirm a new subfolder appears in `applications/` on Google Drive with correct documents
- Run `/update-application <company> interview` and confirm tracker updates
- Run `/interview-prep` and confirm it lists the correct job and produces a prep doc

---

## Open TODOs

- [ ] Fix paths in `.claude/agents/` — after repo restructure, agents still reference old paths (e.g. `ai-framework/config.md`). Update to `max-ai-framework/personal/config.md` and any other stale references.
- [ ] Resolve `.mcp.json` location — currently at repo root. Decide whether it moves to `.claude/mcp.json` (makes Drive MCP global across all sessions) and update setup instructions accordingly.
- [ ] Test `setup.sh` on a clean machine or by temporarily removing the symlink targets and re-running.
