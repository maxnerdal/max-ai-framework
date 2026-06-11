# Google Workspace MCP — Setup

Self-hosted multi-account MCP server for Gmail + Google Calendar + Drive + Docs + Sheets + Tasks. Replaces the Claude.ai hosted Gmail and Calendar connectors. Used by `/morning` and any future skill that reads or writes email/calendar.

**Upstream:** [taylorwilsdon/google_workspace_mcp](https://github.com/taylorwilsdon/google_workspace_mcp)
**Mode:** stdio + `--single-user` (NOT OAuth 2.1 — see why below)
**Account routing:** every Gmail and Calendar tool takes a required `user_google_email` argument. Claude must name the account on every call; there is no default.

Project tracker for this setup lives in the vault at `Areas/Max Nerdal AB/Projects/max-ai-framework/max-ai-framework-google-workspace-mcp.md`.

---

## To-do list

- [ ] 1. Create OAuth client in Google Cloud Console (Desktop type)
- [ ] 2. Install `workspace-mcp` via `uvx`
- [ ] 3. Consent both Google accounts
- [ ] 4. Register the MCP with Claude Code (`claude mcp add`)
- [ ] 5. Smoke test from Claude Code

---

## Step 1 — Create OAuth client in Google Cloud Console

The MCP server authenticates against a single OAuth client. Both Google accounts will consent against the same client and store their own refresh tokens locally.

1. Go to [console.cloud.google.com](https://console.cloud.google.com) and sign in as `maxnerdal@gmail.com` (Personal — fewer admin restrictions than the Workspace account).
2. Create (or select) a project — e.g. "max-ai-framework".
3. **APIs & Services → Library** — enable each of:
   - Gmail API
   - Google Calendar API
   - Google Drive API
   - Google Docs API
   - Google Sheets API
   - Google Tasks API
4. **APIs & Services → OAuth consent screen**:
   - User type: **External**
   - App name: "max-ai-framework" (or anything you'll recognise)
   - User support email: your Gmail
   - Scopes: skip — the MCP server requests them at runtime
   - Test users: add both `maxnerdal@gmail.com` and `max.nerdal@curaconnect.se`
   - Publishing status: **Testing** is fine for now (token refresh every 7 days; you can move to "In production" later to remove that limit)
5. **APIs & Services → Credentials → Create Credentials → OAuth client ID**:
   - Application type: **Desktop app**
   - Name: "max-ai-framework local"
   - Click Create
   - Download the JSON
6. Move the downloaded JSON to a non-repo path:
   ```bash
   mkdir -p ~/.config/max-ai-framework
   mv ~/Downloads/client_secret_*.json ~/.config/max-ai-framework/google-oauth-client.json
   ```

> ⚠️ **Workspace admin policy check (Cura account).** Before consenting `max.nerdal@curaconnect.se`, log into [admin.google.com](https://admin.google.com) as the Cura Workspace admin (= you) and verify that third-party OAuth apps are allowed under **Security → API controls → App access control**. If you've left this at default, you should be fine — but check before hitting consent.

---

## Step 2 — Install workspace-mcp via uvx

The MCP server is a Python package. `uvx` runs it without polluting the global Python env.

```bash
# Install uv if you don't have it yet
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify
uvx --version

# Smoke test the server (will exit after auth attempt — that's fine, we'll wire it up properly below)
uvx workspace-mcp --help
```

> The MCP picks up the OAuth client JSON via the `GOOGLE_CLIENT_SECRET_PATH` env var, set in the mcp.json registration below.

---

## Step 3 — Consent both Google accounts

Run the server once interactively to consent each account.

```bash
# Personal account first
GOOGLE_CLIENT_SECRET_PATH=~/.config/max-ai-framework/google-oauth-client.json \
  uvx workspace-mcp --single-user
```

The server will:
1. Print a URL to stderr
2. Open your default browser to the Google consent screen
3. Wait for you to click "Allow"
4. Receive the callback on `localhost:8080` (or whichever port the server picks)
5. Write a refresh token to `~/.google_workspace_mcp/credentials/maxnerdal@gmail.com.json`

When you see "Allow this app to access your Google Account?":
- It will say "Google hasn't verified this app" → click **Advanced → Go to max-ai-framework (unsafe)**
- This is expected for OAuth clients in Testing status. The "unsafe" warning is showing because the app isn't verified by Google — but the app is you, so it's fine.
- Accept all requested scopes.

Once the browser shows "authentication successful", Ctrl-C the server. Refresh token is now stored.

Repeat for the Cura account — switch Google account in the browser (or use a private window logged in as Cura) before clicking "Allow":

```bash
GOOGLE_CLIENT_SECRET_PATH=~/.config/max-ai-framework/google-oauth-client.json \
  uvx workspace-mcp --single-user
```

After both consents, verify two credential files exist:

```bash
ls ~/.google_workspace_mcp/credentials/
# Expected:
# maxnerdal@gmail.com.json
# max.nerdal@curaconnect.se.json
```

---

## Step 4 — Register the MCP with Claude Code

Use `claude mcp add` at user scope so the MCP is available in every project:

```bash
claude mcp add -s user workspace-mcp \
  -e GOOGLE_CLIENT_SECRET_PATH=/Users/maxnerdal/.config/max-ai-framework/google-oauth-client.json \
  -- uvx workspace-mcp --single-user
```

Verify the registration and that the server connects:

```bash
claude mcp list
# Expected output includes:
# workspace-mcp: uvx workspace-mcp --single-user - ✓ Connected
```

> The registration lives in `~/.claude.json` (Claude Code's user-scope config). Do **not** hand-edit `~/.claude/mcp.json` — that path is not read by Claude Code. The committed `.mcp.json.example` in the repo root is a *project-scope* alternative (drop it as `.mcp.json` in any repo where you want the MCP scoped to that project only) but for personal use, user scope is the right default.

Restart Claude Code so it picks up the new MCP registration. MCP tools are discovered at session start.

---

## Step 5 — Smoke test from Claude Code

In a Claude Code session:

```
List events for the next 24 hours on maxnerdal@gmail.com, then list events for the next 24 hours on max.nerdal@curaconnect.se, then list 3 unread emails from each account.
```

Expected:
- Calendar events from both accounts with full titles (no `freeBusyReader` fallback on Cura).
- Unread email from both inboxes, addressed by account.

If Claude tries to call a tool without `user_google_email` and gets a `TypeError` — that's the safety check working as intended.

---

## Troubleshooting

### "Google hasn't verified this app" warning
Expected — your OAuth client is in Testing status. Click Advanced → Go to (unsafe). To remove permanently: move the client to "In production" status in the OAuth consent screen settings.

### Cura account token bombs out every ~7 days
Workspace policy for non-internal OAuth apps. Either:
- Move the OAuth client to "In production" status (removes 7-day refresh expiry for Testing-mode tokens), or
- Live with it — re-running step 3 for the Cura account once a week takes ~30 seconds.

### `freeBusyReader` errors on Cura calendar
Should not happen with this setup — each account is now authenticated directly with its own scopes. If it does happen: confirm you're calling tools with `user_google_email="max.nerdal@curaconnect.se"` and not the Personal email.

### MCP server doesn't start
```bash
# Test the exact command from mcp.json manually:
GOOGLE_CLIENT_SECRET_PATH=/Users/maxnerdal/.config/max-ai-framework/google-oauth-client.json \
  uvx workspace-mcp --single-user
```
Errors print to stderr. Common causes: missing `GOOGLE_CLIENT_SECRET_PATH` env var, wrong JSON path, missing credentials directory.

### Wrong account being used despite explicit `user_google_email`
Should be impossible — taylorwilsdon's stdio mode raises `TypeError` if the argument is omitted. If you see this: open an issue upstream, and in the meantime do not use the MCP for writes.

---

## Why these specific choices

- **taylorwilsdon over aaronsb/j3k0/nspady** — only one with `user_google_email` as a required no-default argument. Per-account safety enforced at the type system, not by convention.
- **stdio + `--single-user`, NOT OAuth 2.1** — OAuth 2.1 mode strips the `user_google_email` parameter (auth via bearer token in HTTP header instead) and is designed for hosted multi-user deployments. Wrong fit here, and breaks the safety story.
- **One OAuth client, two accounts** — both accounts consent against the same client; each gets its own refresh token file. Standard pattern, less to maintain than two clients.
- **OAuth client JSON at `~/.config/max-ai-framework/`** — out of repo (it's a secret), under XDG-style config path.
- **MCP registration via `claude mcp add -s user`, not a hand-edited config file** — Claude Code reads user-scope MCPs from `~/.claude.json` (managed through the CLI), not from `~/.claude/mcp.json` (which it ignores). The repo holds `.mcp.json.example` as a project-scope template only — useful if you want to scope this MCP to a single repo instead.

---

## See also

- Project tracker: `Areas/Max Nerdal AB/Projects/max-ai-framework/max-ai-framework-google-workspace-mcp.md` (vault)
- Upstream MCP: [taylorwilsdon/google_workspace_mcp](https://github.com/taylorwilsdon/google_workspace_mcp)
- Claude Code context loading: `docs/claude-context-loading.md`
- Server setup (always-on machine): `docs/server-setup.md`
