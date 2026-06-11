# Max Nerdal — Global Claude Context

## Who I am
Max Nerdal, Swedish developer. I work at Cura Connect AB (curaconnect.se) and run Max Nerdal AB as a consultant. Primary spoken language is Swedish; code and technical communication in English.

## My AI framework
This global config is part of `max-ai-framework` — a shared toolkit at `~/Documents/max-ai-framework/` providing skills, agents, commands, workflows, prompts, templates, and MCP servers across all my work. Symlinked into `~/.claude/`.

App code lives in its own repo per app (e.g. `~/Documents/hosp-automation/`, `~/Documents/tradingbots/`, future portfolio site). Each app repo's `CLAUDE.md` `@imports` the relevant Obsidian area context for that work.

## Obsidian — Second Brain
Obsidian vault at `~/Documents/obsidian-vault/` is the single source of truth for business knowledge, brand information, strategy docs, meeting notes, and project state. Areas: Cura Connect, Max Nerdal AB, Personal. Loading rules in `~/.claude/rules/obsidian.md`.

## General preferences
- Concise responses — no trailing summaries, no restating what was just done
- No emojis
- No unnecessary comments in code

## Gmail and Google Calendar
Always use the `workspace-mcp` tools (they take a required `user_google_email` argument), never the hosted `mcp__claude_ai_Gmail__*` / `mcp__claude_ai_Google_Calendar__*` connectors. The hosted connectors are single-account and silently route to the wrong inbox. Accounts: `maxnerdal@gmail.com` (Personal), `max.nerdal@curaconnect.se` (Cura Connect).

## Framework area-suffix convention
Every skill, agent, command, workflow, prompt, and template in `max-ai-framework` carries a primary-beneficiary suffix so the framework can be split per area later without grepping content:
- `-cc` — Cura Connect
- `-p` — Personal
- `-mn` — Max Nerdal AB
- `-s` — Shared (cross-area)

The suffix is on the filename (and the containing folder for skills). It carries through to invocation: `/morning-s`, `/sweep-s`, `/job-application-p`, `@application-drafter-p`, etc. Cross-references inside skills/workflows/agents must use the suffixed names. When in doubt, default to `-s` and promote to a specific area only when the tool grows hard dependencies on that area's data sources, credentials, or conventions. Full rule in `max-ai-framework/CLAUDE.md`.
