# Dedicated MacBook Setup — Always-On Server for Cowork & Claude Code

## To-do list

**Do physically on the server MacBook:**
- [ ] 1. Install Tailscale + enable SSH

**Do remotely over SSH from main Mac:**
- [ ] 2. Configure macOS system settings for always-on use
- [ ] 3. Install Claude desktop app + Claude in Chrome
- [ ] 4. Clone max-ai-framework and run setup.sh
- [ ] 5. Set up auto-sync LaunchAgent for scheduled tasks
- [ ] 6. Log in to services + enable scheduled tasks in Cowork

**When dummy plug arrives:**
- [ ] 7. Plug in headless display dummy plug and verify display

---

## Step 1 — Install Tailscale + enable SSH (physical, do this first)

This is the only step that requires you to be at the server MacBook. Once done, everything else is remote.

### Enable SSH
`System Settings → General → Sharing`
- Toggle on **"Remote Login"**
- Set **"Allow access for: All users"**

### Install Tailscale
1. Go to [tailscale.com/download](https://tailscale.com/download) and install the macOS app
2. Log in with the **same Tailscale account** as your main Mac
3. In the Tailscale menu bar app, note the `100.x.x.x` IP address

### Test from your main Mac
```bash
ssh username@100.x.x.x
```

### Set up SSH key authentication (on your main Mac)
So you don't have to type a password every time:
```bash
# Generate a key if you don't have one
ssh-keygen -t ed25519

# Copy it to the server MacBook
ssh-copy-id username@100.x.x.x
```

### Optional: give the machine a friendly hostname
In the Tailscale dashboard rename it to something like `cura-server` so you can connect with:
```bash
ssh username@cura-server
```

---

## Step 2 — Configure macOS system settings (remote, via SSH)

### Prevent sleep
```bash
sudo pmset -a sleep 0
sudo pmset -a disablesleep 1
```

### Enable automatic login
This requires the GUI — use Screen Sharing instead of SSH for this step:

On your main Mac, open **Finder → Go → Connect to Server** and enter:
```
vnc://100.x.x.x
```
Then navigate to `System Settings → Users & Groups → Automatic login` and set your user.

> ⚠️ If FileVault is enabled, automatic login will be disabled. You can either turn off FileVault or accept that you'll need to enter the password once after a reboot.

### Set Claude app to auto-start on boot (via LaunchAgent instead of GUI)
Rather than using Login Items in System Settings, create a LaunchAgent over SSH:

```bash
cat > ~/Library/LaunchAgents/com.maxnerdal.claude-autostart.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.maxnerdal.claude-autostart</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/open</string>
        <string>-a</string>
        <string>Claude</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
EOF

launchctl load ~/Library/LaunchAgents/com.maxnerdal.claude-autostart.plist
```

---

## Step 3 — Install Claude desktop app + Claude in Chrome (remote, via Screen Sharing)

Use Screen Sharing (vnc://100.x.x.x) for this step since it involves downloading and installing GUI apps.

On the server MacBook:
- Download and install the Claude desktop app from claude.ai
- Install Google Chrome
- Install the Claude in Chrome browser extension from the Chrome Web Store
- Connect the extension to the desktop app (follow the pairing prompt)
- Log in to Claude with your account

---

## Step 4 — Clone max-ai-framework and run setup.sh (remote, via SSH)

```bash
git clone https://github.com/maxnerdal/max-ai-framework.git
cd max-ai-framework
./setup.sh
```

This creates the symlink:
- `~/Documents/Claude/Scheduled` → `~/max-ai-framework/claude-cowork/Scheduled`

### Set up GitHub SSH authentication for auto-push
```bash
# Generate SSH key on the server MacBook
ssh-keygen -t ed25519 -C "cura-server"

# Copy the public key
cat ~/.ssh/id_ed25519.pub
```
Add it to GitHub: **github.com → Settings → SSH keys → New SSH key**

Then switch the repo remote to SSH:
```bash
cd ~/max-ai-framework
git remote set-url origin git@github.com:maxnerdal/max-ai-framework.git

# Test
ssh -T git@github.com
```

---

## Step 5 — Set up auto-sync LaunchAgent for scheduled tasks (remote, via SSH)

Watches `claude-cowork/Scheduled/` and auto-commits + pushes to GitHub when tasks change.

**1. Create the sync script**
```bash
mkdir -p ~/max-ai-framework/scripts

cat > ~/max-ai-framework/scripts/sync-scheduled-tasks.sh << 'EOF'
#!/bin/bash
REPO="$HOME/max-ai-framework"
cd "$REPO" || exit 1

if ! git diff --quiet claude-cowork/Scheduled/ || git ls-files --others --exclude-standard claude-cowork/Scheduled/ | grep -q .; then
  git add claude-cowork/Scheduled/
  git commit -m "Auto-sync: update scheduled tasks $(date '+%Y-%m-%d %H:%M')"
  git push origin master
fi
EOF

chmod +x ~/max-ai-framework/scripts/sync-scheduled-tasks.sh
```

**2. Create the LaunchAgent**
```bash
cat > ~/Library/LaunchAgents/com.maxnerdal.sync-scheduled-tasks.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.maxnerdal.sync-scheduled-tasks</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/Users/$(whoami)/max-ai-framework/scripts/sync-scheduled-tasks.sh</string>
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
EOF

launchctl load ~/Library/LaunchAgents/com.maxnerdal.sync-scheduled-tasks.plist
```

**3. Verify**
```bash
launchctl list | grep sync-scheduled-tasks
cat /tmp/sync-scheduled-tasks.log
```

### To stop/restart
```bash
launchctl unload ~/Library/LaunchAgents/com.maxnerdal.sync-scheduled-tasks.plist
launchctl load ~/Library/LaunchAgents/com.maxnerdal.sync-scheduled-tasks.plist
```

---

## Step 6 — Log in to services + enable scheduled tasks (remote, via Screen Sharing)

Use Screen Sharing (vnc://100.x.x.x) to open Chrome and log in to:
- [app.bemlo.com](https://app.bemlo.com) — for Bemlo tender monitoring tasks

Then in the Claude desktop app:
- Go to **Settings → Scheduled Tasks**
- Enable the Bemlo monitoring tasks (08:00, 12:00, 16:00)
- Manually trigger one task to verify it runs end-to-end

---

## Step 7 — Plug in headless display dummy plug (when delivered)

Order from **Amazon.se** or **Komplett.se** — search `HDMI dummy plug headless`, around 50–100 kr.

Needed so the MacBook can run with the lid closed while Chrome and Cowork still have a virtual display. Plug it in and verify that Screen Sharing still works and scheduled tasks still run.
