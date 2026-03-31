# Setup

Steps to get this framework running on a new machine.

## 1. Install Claude Code

```bash
npm install -g @anthropic-ai/claude-code
```

Requires Node.js 18+. Check your version with `node --version`.

## 2. Authenticate Claude Code

```bash
claude
```

Follow the prompts to log in with your Anthropic account.

## 3. Install required plugins

```bash
claude plugin install skill-creator
```

| Plugin | Purpose |
|--------|---------|
| `skill-creator` | Build, test, and iterate on skills in this framework |

## 4. Set up personal config

```bash
cp config.example.md config.md
```

Then open `config.md` and fill in your Google Drive folder and file IDs. `config.md` is gitignored and will never be committed.

## 5. Verify setup

```bash
claude plugin list
```

You should see `skill-creator` listed as enabled.

## 6. Install jq (required for statusline)

```bash
brew install jq
```

## 7. Configure statusline

Run this slash command inside Claude Code:

```
/statusline show model name, folder name (not full path), and context usage as a 10-character block progress bar with the scaled percentage number next to it. Use pipe separators between items. Scale the percentage so that 80% real usage shows as 100% (since Claude compacts at 80%). Color the bar green under 50%, yellow 50-65%, orange 65-95%, and blinking red with a skull emoji at 95%+. Keep it compact – dim the model and folder name, bright colors only on the bar.
```

Claude Code will generate the script and update `~/.claude/settings.json` automatically.
