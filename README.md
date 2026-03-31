# ai-framework

A portable, config-driven framework of skills, agents, workflows, and prompts for working with Claude.

## Structure

```
ai-framework/
├── skills/           # SKILL.md files teaching Claude how to do things
├── agents/           # Autonomous workers combining multiple skills
├── workflows/        # Named repeatable multi-step processes
├── prompts/          # Reusable prompt templates
├── config.example.md # Template for personal config (safe to commit)
└── config.md         # Your personal config with real IDs (gitignored)
```

## Setup

1. Copy `config.example.md` to `config.md`
2. Fill in your own Google Drive folder and file IDs
3. `config.md` is gitignored — it will never be committed

## Design principles

- **Logic lives in the repo** — skills, agents, workflows are shareable
- **Data never lives in the repo** — personal files stay in Google Drive
- **Config bridges the two** — `config.md` holds pointers to your data
- **Portable** — clone on a new machine, fill in `config.md`, done

## Skills

| Skill | Description |
|-------|-------------|
| [cv-writer](skills/cv-writer/SKILL.md) | Writes tailored CVs and personal letters from your Google Drive docs |
