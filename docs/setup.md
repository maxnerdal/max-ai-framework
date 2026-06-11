# Setup — New Machine

Steps to get this framework running on a new machine.

## 1. Clone the repo

```bash
git clone https://github.com/maxnerdal/max-ai-framework.git
```

## 2. Run setup.sh

```bash
cd max-ai-framework
./setup.sh
```

This creates these symlinks:
- `~/.claude/CLAUDE.md` → `~/max-ai-framework/.claude/CLAUDE.md`
- `~/.claude/agents` → `~/max-ai-framework/.claude/agents`
- `~/.claude/commands` → `~/max-ai-framework/.claude/commands`

Editing files inside `~/max-ai-framework/.claude/` updates them globally for Claude Code. Other contents of `~/.claude/` (projects, sessions, mcp.json, settings.json) are left alone.

## 3. Install Claude Code

```bash
npm install -g @anthropic-ai/claude-code
```

Requires Node.js 18+. Check with `node --version`.

## 4. Authenticate Claude Code

```bash
claude
```

Follow the prompts to log in with your Anthropic account.

## 5. Copy config and fill in credentials

```bash
cp config.example.md config.md
```

Open `config.md` and fill in Google Drive IDs and OAuth paths. The file is gitignored.

App-specific repos (e.g. `~/Documents/hosp-automation/`) carry their own gitignored `config.md` with that app's secrets.

## Optional: dedicated server setup

See [docs/server-setup.md](server-setup.md) if you want to run this framework on a dedicated always-on machine.
