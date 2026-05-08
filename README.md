# max-ai-framework

Max Nerdal's personal AI framework. Version-controlled source of truth for Claude Code configs, skills, agents, and workflows across personal and work contexts.

## Structure

```
max-ai-framework/
  .claude/              — Global Claude Code config (agents, commands, settings)
  personal/             — Personal context: job applications, CV, Drive integration
  cura-connect/         — Work automation for Cura Connect AB
  max-nerdal-ab/        — Consulting work (Max Nerdal AB)
  claude-cowork/        — Cowork scheduled task definitions
  docs/                 — Setup guides
  plan.md               — Framework decisions and open TODOs
  setup.sh              — Creates symlinks on a new machine
```

## Design principles

- **Logic lives in the repo** — skills, agents, workflows are version-controlled and shareable
- **Data never lives in the repo** — personal files stay in Google Drive
- **Config bridges the two** — each context has a `config.md` (gitignored) with keys and IDs
- **Project code lives elsewhere** — projects like `tradingbots` have their own repos; this framework only contains Claude configuration

## Getting started

See [docs/setup.md](docs/setup.md) for setup instructions.

For a dedicated always-on server setup, see [docs/server-setup.md](docs/server-setup.md).
