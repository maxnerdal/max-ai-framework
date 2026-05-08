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

This creates the symlink:
- `~/Documents/Claude/Scheduled` → `~/max-ai-framework/claude-cowork/Scheduled`

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

## 5. Copy config files and fill in credentials

Each context has its own config:

```bash
cp personal/config.example.md personal/config.md
cp cura-connect/config.example.md cura-connect/config.md
```

Open each `config.md` and fill in API keys, Drive IDs, and credential paths. These files are gitignored and will never be committed.

## 6. Copy .claude/ contents to ~/.claude

The `.claude/` folder in this repo is the source of truth for global Claude Code config. Copy it to your home directory:

```bash
cp -r .claude/ ~/.claude/
```

> Note: This is a manual step — `.claude/` is not symlinked automatically. When you update agents or commands in the repo, re-run this copy.

## Optional: dedicated server setup

See [docs/server-setup.md](server-setup.md) if you want to run this framework on a dedicated always-on machine.
