# Self-improvement

Two directions of capture. Consider both continuously; write neither without asking first.

## Downward — into the project

When we agree on *how* we work in a project — not what the content says — write it into that
project's anchor in the vault, under a heading `## Arbetssätt`, as short imperative rules.
The anchor states the rule; the rationale stays in the project's decision log.

Triggers:
- The user corrects the same thing twice.
- We invent a convention mid-task to get unstuck.
- We put up a guard against a mistake that already happened once.

Do not put content decisions here — those belong in the decision log.

## Upward — into the framework

When the same pattern shows up in a second project, or is obviously not project-specific,
propose promoting it:

- Recurring craft, voice, or domain procedure → a skill in `~/.claude/skills/<name>-<suffix>/` (global, lands in the framework via symlink), not the current repo's `.claude/skills/`
- Reusable writing principle shared by several skills → a prompt in `prompts/`
- Applies to every session regardless of project → a rule in `.claude/rules/`

Rules carry no area suffix (see `obsidian.md`). Skills, agents, commands, workflows, prompts
and templates do — see the suffix table in `CLAUDE.md`.

## Guard

- Propose, then write. Never create or edit a rule, skill, or anchor section unannounced.
- Prefer editing an existing file over adding a new one.
- Do not capture trivia. If it would not change what a future session does, leave it out.
- Style guides are living documents: sharpen the existing skill each time it is used rather
  than writing a complete guide up front. `presentation-writer-p` is the reference example.
