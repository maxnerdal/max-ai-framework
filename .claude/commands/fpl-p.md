Sync Max's Fantasy Premier League team ("Smörblommorna") against the FPL API and update the Obsidian project doc with fresh data + a GW plan for the next deadline.

## Config

Read from `~/Documents/max-ai-framework/config.md`:
- `FPL_TEAM_ID` — public FPL entry ID (e.g. 8076724)
- `FPL_PROJECT_DOC` — absolute path to the Obsidian project anchor to update
- `FPL_PL_PROFILE_COOKIE` — session cookie `pl_profile` from `fantasy.premierleague.com` (optional but recommended)
- `FPL_SESSIONID_COOKIE` — session cookie `sessionid` from `fantasy.premierleague.com` (optional but recommended)

If cookies are empty, still run — just fall back to post-deadline picks and skip the pre-deadline live-lineup step.

## Steps

1. **Load config** — read `config.md`, extract the FPL keys above. If `FPL_TEAM_ID` is missing, stop and tell the user to fill it in.

2. **Fetch public data** with `curl -s`:
   - `https://fantasy.premierleague.com/api/bootstrap-static/` → `/tmp/fpl_bootstrap.json` (players, teams, events, FDR)
   - `https://fantasy.premierleague.com/api/fixtures/` → `/tmp/fpl_fixtures.json`
   - `https://fantasy.premierleague.com/api/entry/{FPL_TEAM_ID}/` → parse total points, rank, current_event
   - `https://fantasy.premierleague.com/api/entry/{FPL_TEAM_ID}/history/` → chip usage + per-GW summary
   - `https://fantasy.premierleague.com/api/entry/{FPL_TEAM_ID}/transfers/` → transfer log (may be `[]`)

3. **Determine current + next GW** from bootstrap `events`:
   - `current_gw` = event where `is_current: true` (may be null in pre-season)
   - `next_gw` = event where `is_next: true`

4. **Fetch lineup for current GW** (post-deadline snapshot):
   - `https://fantasy.premierleague.com/api/entry/{FPL_TEAM_ID}/event/{current_gw}/picks/` → `/tmp/fpl_picks_gw{current_gw}.json`
   - If 404 (GW not deadline-passed yet), skip.

5. **Fetch live lineup** (pre-deadline, requires cookies):
   - If both cookies are set:
     ```
     curl -s -H "Cookie: pl_profile={FPL_PL_PROFILE_COOKIE}; sessionid={FPL_SESSIONID_COOKIE}" \
       https://fantasy.premierleague.com/api/my-team/{FPL_TEAM_ID}/ -o /tmp/fpl_myteam.json
     ```
   - Verify the response isn't an auth-error redirect (HTTP 200 + JSON with `picks` key). If auth fails, warn the user that cookies have expired and instruct re-export (see "Cookie refresh" below).
   - If cookies missing or expired, use the current-GW picks from step 4 as the working lineup and note that the plan is based on post-deadline snapshot, not live tinkering.

6. **Build the analysis** in a single Python block reading from the JSON dumps:
   - Squad table: pick position, role (GK/DEF/MID/FWD), name, team short_name, cost (now_cost/10), GW points, total points, captain/vice
   - Fixture ticker for `next_gw` through `next_gw+4` (5 GWs), one row per player, sorted by team-avg FDR
   - Detect DGW/BGW: if any team has ≠1 fixture in a GW within the window, flag it
   - Bench-order sanity check: current bench outfield order — flag if FWD is not first among outfield subs when a FWD is starting (common misconfiguration)
   - Captain recommendation: for each starter, look up FDR + fixture location for next_gw; recommend highest-ceiling non-injured premium on green fixture
   - VC recommendation: default to premium outfielder with next-best fixture; warn if user has VC on GK

7. **Update the project doc** at `FPL_PROJECT_DOC`. Preserve manual sections; rewrite the auto-managed ones (marked with the sentinels below). Sections managed by this command:
   - **Aktuell status** — full replace with latest snapshot (points, rank, bank, value, chips)
   - **Laguppställning (efter GW{current_gw}, före GW{next_gw})** — full replace with post-deadline picks
   - **Transfer-historik** — append rows for new transfers since last sync (dedup by GW + element_in + element_out)
   - **Fixture ticker GW{next_gw}–GW{next_gw+4}** — full replace with fresh table
   - **GW{next_gw}-plan** — full replace with recommendation (based on live lineup if cookies work, else on post-deadline snapshot)
   - **Beslutslogg** — append one dated line summarising the sync + plan

   Use HTML comment sentinels to demarcate auto-managed regions so manual notes above/below are safe:
   ```
   <!-- fpl-p:section=status:start -->
   ...auto content...
   <!-- fpl-p:section=status:end -->
   ```
   Do the same for `lineup`, `ticker`, `plan`. Transfer-historik and Beslutslogg are append-only — locate the section by `## ` heading and add rows without touching earlier ones.

8. **Present a summary in chat** — three bullet blocks:
   - **Diff mot förra synken:** what changed in the doc (transfers logged, chip status, rank movement)
   - **GW{next_gw}-plan i korthet:** starting XI in one line, C/VC, key bench-order note
   - **Handling som krävs:** anything the user must do manually in the FPL app (captain change, sub, chip activation)

## Cookie refresh (when auth fails)

If step 5 returns non-JSON or an auth-error payload, tell the user:

> Cookien har gått ut. Så här förnyar du (30 sek):
> 1. Öppna `fantasy.premierleague.com` i webbläsaren, logga in
> 2. Öppna DevTools (F12) → Application → Storage → Cookies → `https://fantasy.premierleague.com`
> 3. Kopiera värdet på cookien `pl_profile` (klicka på raden, kopiera "Value")
> 4. Kopiera värdet på cookien `sessionid`
> 5. Klistra in värdena i `~/Documents/max-ai-framework/config.md` under `FPL_PL_PROFILE_COOKIE=` och `FPL_SESSIONID_COOKIE=`
> 6. Kör `/fpl-p` igen

Then skip the my-team fetch this run and proceed with post-deadline data only.

## What this command does NOT do

- **Make transfers or set lineup for you.** FPL's write endpoints need CSRF + authenticated POST + write permission. All lineup/captain changes must still be done manually in the FPL app. This command generates the *plan*; you execute it.
- **Predict player scores.** All recommendations are based on FDR + recent points + fixture location. No xG/expected-points model.
- **Track leagues beyond your own.** Rival-manager analysis (differentials, template diffing) is out of scope.

## When to run

- **Weekly:** Friday morning before deadline (Saturday 13:30 CET usually) to get the plan
- **Post-GW:** Monday morning after games to log transfers + refresh snapshot + update ticker for the next window
- **Ad hoc:** whenever a chip decision or major transfer looms

Command is on-demand only (no cron). Invoke as `/fpl-p`.
