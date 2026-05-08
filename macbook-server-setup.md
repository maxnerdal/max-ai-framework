# Dedicated MacBook Setup — Always-On Server for Cowork & Claude Code

## To-do list

- [ ] 1. Buy headless display dummy plug
- [ ] 2. Configure macOS system settings for always-on use
- [ ] 3. Install Tailscale on both Macs
- [ ] 4. Install Claude desktop app + Claude in Chrome
- [ ] 5. Clone max-ai-framework and run setup.sh *(blocked on Claude Code work)*
- [ ] 6. Log in to services in Chrome (Bemlo etc.)
- [ ] 7. Enable and test scheduled tasks in Claude
- [ ] 8. Set up auto-sync LaunchAgent for scheduled tasks

---

## Step 1 — Buy headless display dummy plug

Kjell & Company doesn't stock these. Order from **Amazon.se** or **Komplett.se**.
Search: `HDMI dummy plug headless` — around 50–100 kr.

Needed so the MacBook can run with the lid closed while Chrome and Cowork still have a virtual display to work with.

---

## Step 2 — Configure macOS system settings for always-on use

### Prevent sleep
`System Settings → Battery → Options`
- Enable **"Prevent automatic sleeping when display is off"**
- Set **"Turn display off after"** → Never (or a long interval)

Also run this in Terminal to be safe:
```bash
sudo pmset -a sleep 0
sudo pmset -a disablesleep 1
```

### Enable automatic login (so it boots into a session without you)
`System Settings → Users & Groups`
- Click **"Automatic login"** and select your user
- Enter your password to confirm

> ⚠️ Note: If FileVault (disk encryption) is enabled, automatic login will be disabled. You can either turn off FileVault or accept that you'll need to enter the password once after a reboot.

### Enable SSH (Remote Login)
`System Settings → General → Sharing`
- Toggle on **"Remote Login"**
- Set **"Allow access for: All users"** (or restrict to your user)

Test from your main Mac:
```bash
ssh username@macbook-local-ip
```

### Add Claude desktop app to Login Items (auto-start on boot)
`System Settings → General → Login Items`
- Click **+** and add the Claude desktop app
- Also add **Google Chrome** here so it opens automatically on boot

---

## Step 3 — Install Tailscale on both Macs

Tailscale creates a private encrypted network between your devices. It works from anywhere — home, office, abroad — without port forwarding or a static IP.

### Install on both Macs
1. Go to [tailscale.com/download](https://tailscale.com/download)
2. Download and install the macOS app on **both** the dedicated MacBook and your main Mac
3. Log in with the **same Tailscale account** on both machines
4. Both Macs will appear in your Tailscale dashboard at [login.tailscale.com](https://login.tailscale.com)

### Find the Tailscale IP
In the Tailscale menu bar app, click the machine name — it shows a `100.x.x.x` address. Or check the dashboard online.

### Test SSH over Tailscale
From your main Mac:
```bash
ssh username@100.x.x.x
```
Replace `100.x.x.x` with the dedicated MacBook's Tailscale IP.

### Set up SSH key authentication (recommended)
So you don't have to type a password every time:
```bash
# On your main Mac — generate a key if you don't have one
ssh-keygen -t ed25519

# Copy it to the dedicated MacBook
ssh-copy-id username@100.x.x.x
```

After this, `ssh username@100.x.x.x` logs in instantly with no password.

### Optional: give the machine a friendly hostname
In the Tailscale dashboard you can rename the machine to something like `cura-server` so you can connect with:
```bash
ssh username@cura-server
```

---

## Step 4 — Install Claude desktop app + Claude in Chrome

On the dedicated MacBook:
- Download and install the Claude desktop app from claude.ai
- Install Google Chrome
- Install the Claude in Chrome browser extension from the Chrome Web Store
- Connect the extension to the desktop app (follow the pairing prompt)
- Log in to Claude with your account

---

## Step 5 — Clone max-ai-framework and run setup.sh

*This step is blocked on the Claude Code work — setup.sh needs to be written first.*

Once ready:
```bash
git clone https://github.com/maxnerdal/max-ai-framework.git
cd max-ai-framework
./setup.sh
```

This creates the symlink:
- `~/Documents/Claude/Scheduled` → `~/max-ai-framework/claude-cowork/Scheduled`

---

## Step 6 — Log in to services in Chrome

Open Chrome and log in to:
- [app.bemlo.com](https://app.bemlo.com) — for Bemlo tender monitoring tasks

Keep sessions alive. Consider using a password manager so re-login is quick if sessions expire.

---

## Step 7 — Enable and test scheduled tasks

In the Claude desktop app:
- Go to **Settings → Scheduled Tasks**
- Enable the Bemlo monitoring tasks (08:00, 12:00, 16:00)
- Manually trigger one task to verify it runs end-to-end

---

## Step 8 — Set up auto-sync LaunchAgent for scheduled tasks

A macOS LaunchAgent is a background process that runs automatically. This one watches the `claude-cowork/Scheduled/` folder for changes and auto-commits + pushes to GitHub whenever a scheduled task is created or modified in Cowork.

### How it works
1. A shell script checks for uncommitted changes in `~/max-ai-framework/claude-cowork/Scheduled/`
2. If changes are found, it commits and pushes to GitHub automatically
3. The LaunchAgent runs the script on a schedule (e.g. every 5 minutes)

### Step-by-step setup

**1. Create the sync script**

Save this as `~/max-ai-framework/scripts/sync-scheduled-tasks.sh`:
```bash
#!/bin/bash
REPO="$HOME/max-ai-framework"
cd "$REPO" || exit 1

# Check if there are any changes in claude-cowork/Scheduled/
if ! git diff --quiet claude-cowork/Scheduled/ || git ls-files --others --exclude-standard claude-cowork/Scheduled/ | grep -q .; then
  git add claude-cowork/Scheduled/
  git commit -m "Auto-sync: update scheduled tasks $(date '+%Y-%m-%d %H:%M')"
  git push origin master
fi
```

Make it executable:
```bash
chmod +x ~/max-ai-framework/scripts/sync-scheduled-tasks.sh
```

**2. Create the LaunchAgent plist**

Save this as `~/Library/LaunchAgents/com.maxnerdal.sync-scheduled-tasks.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.maxnerdal.sync-scheduled-tasks</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/Users/YOUR_USERNAME/max-ai-framework/scripts/sync-scheduled-tasks.sh</string>
    </array>
    <key>StartInterval</key>
    <integer>300</integer>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/sync-scheduled-tasks.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/sync-scheduled-tasks.error.log</string>
</dict>
</plist>
```
> Replace `YOUR_USERNAME` with your actual macOS username.

**3. Load the LaunchAgent**
```bash
launchctl load ~/Library/LaunchAgents/com.maxnerdal.sync-scheduled-tasks.plist
```

**4. Verify it's running**
```bash
launchctl list | grep sync-scheduled-tasks
```

**5. Check the log**
```bash
cat /tmp/sync-scheduled-tasks.log
```

### To stop/restart the LaunchAgent
```bash
# Stop
launchctl unload ~/Library/LaunchAgents/com.maxnerdal.sync-scheduled-tasks.plist

# Start again
launchctl load ~/Library/LaunchAgents/com.maxnerdal.sync-scheduled-tasks.plist
```

### GitHub authentication for auto-push
The sync script pushes to GitHub automatically, so git needs to authenticate without prompting for a password. Set this up once:

```bash
# Use SSH for GitHub (recommended)
# 1. Generate SSH key on the dedicated MacBook (if not already done)
ssh-keygen -t ed25519 -C "cura-server"

# 2. Copy the public key
cat ~/.ssh/id_ed25519.pub

# 3. Add it to GitHub: github.com → Settings → SSH keys → New SSH key

# 4. Change your git remote to use SSH
cd ~/max-ai-framework
git remote set-url origin git@github.com:maxnerdal/max-ai-framework.git

# 5. Test
ssh -T git@github.com
```
