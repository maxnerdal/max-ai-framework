Sync Max's Fantasy Premier League team ("Smörblommorna") against the FPL API and update the Obsidian project doc with fresh data + a GW plan for the next deadline.

This is a **read-only** command. It generates a plan; the user executes lineup/captain/transfer changes manually in the FPL app. Automation of writes was evaluated and rejected — the maintenance cost of FPL's short-lived Bearer tokens outweighs the ~2 min/week saved.

## Config

Read from `~/Documents/max-ai-framework/config.md`:
- `FPL_TEAM_ID` — public FPL entry ID (e.g. 8076724)
- `FPL_PROJECT_DOC` — absolute path to the Obsidian project anchor to update
- `FPL_API_TOKEN` — Bearer token for authenticated read of `/api/my-team/` (optional but recommended). Extract from browser: DevTools → Network → any `/api/entry/…` request → Request Headers → `X-Api-Authorization: Bearer <token>`. Paste only the token, skip the "Bearer " prefix.

If `FPL_API_TOKEN` is empty, still run — fall back to post-deadline picks and skip the live-lineup step.

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

5. **Fetch live lineup** (pre-deadline, requires `FPL_API_TOKEN`):
   - If token is set:
     ```
     curl -s -H "X-Api-Authorization: Bearer {FPL_API_TOKEN}" \
       https://fantasy.premierleague.com/api/my-team/{FPL_TEAM_ID}/ -o /tmp/fpl_myteam.json
     ```
   - Verify HTTP 200 + JSON with `picks` key. If 401/403 or non-JSON: warn the user with the "Token refresh" instructions and fall back to post-deadline picks.

6. **Build the analysis** in a single Python block reading from the JSON dumps:
   - Squad table: pick position, role (GK/DEF/MID/FWD), name, team short_name, cost (now_cost/10), GW points, total points, captain/vice
   - Fixture ticker for `next_gw` through `next_gw+4` (5 GWs), one row per player, sorted by team-avg FDR
   - Detect DGW/BGW: if any team has ≠1 fixture in a GW within the window, flag it
   - Bench-order sanity check: current bench outfield order — flag if FWD is not first among outfield subs when a FWD is starting
   - Captain recommendation: for each starter, look up FDR + fixture location for next_gw; recommend highest-ceiling non-injured premium on green fixture
   - VC recommendation: default to premium outfielder with next-best fixture; warn if user has VC on GK
   - **If live my-team was fetched**: compute diff between live picks and recommendation. Group into captain/VC changes, bench-order changes, starting-XI swaps.

7. **Update the project doc** at `FPL_PROJECT_DOC`. Preserve manual sections; rewrite the auto-managed ones (marked with the sentinels below). Sections managed by this command:
   - **Aktuell status** — full replace with latest snapshot (points, rank, bank, value, chips)
   - **Laguppställning (efter GW{current_gw}, före GW{next_gw})** — full replace with post-deadline picks. If live my-team fetched, add a note showing current live state where it differs.
   - **Transfer-historik** — append rows for new transfers since last sync (dedup by GW + element_in + element_out)
   - **Fixture ticker GW{next_gw}–GW{next_gw+4}** — full replace with fresh table
   - **GW{next_gw}-plan** — full replace with recommendation. If live my-team fetched, add a diff subsection showing what needs to change from live → recommendation.
   - **Beslutslogg** — append one dated line summarising the sync + plan

   Use HTML comment sentinels to demarcate auto-managed regions so manual notes above/below are safe:
   ```
   <!-- fpl-p:section=status:start -->
   ...auto content...
   <!-- fpl-p:section=status:end -->
   ```
   Do the same for `lineup`, `ticker`, `plan`. Transfer-historik and Beslutslogg are append-only — locate the section by `## ` heading and add rows without touching earlier ones.

8. **Present the chat summary** — three bullet blocks:
   - **Diff mot förra synken:** what changed in the doc (transfers logged, chip status, rank movement)
   - **GW{next_gw}-plan i korthet:** starting XI in one line, C/VC, key bench-order note
   - **Handling som krävs:** exact list of clicks the user should do in the FPL app (captain change, VC change, bench-order, starting-XI swaps, chip activation, transfers). Base this on the live-vs-recommendation diff when available.

## Token refresh (when live-read fails with 401/403)

If step 5 returns non-JSON or an auth-error payload:

> Bearer-tokenen har gått ut. Så här förnyar du (30 sek):
> 1. Öppna `fantasy.premierleague.com/my-team` i webbläsaren, logga in
> 2. Öppna DevTools (F12) → **Network**-fliken
> 3. Ladda om sidan (Cmd+R)
> 4. Klicka på en request till `/api/entry/{FPL_TEAM_ID}/` (eller vilken `/api/…`-request som helst)
> 5. Fliken **Headers** → scrolla till **Request Headers** → hitta `X-Api-Authorization: Bearer <token>`
> 6. Kopiera bara tokenen (utan "Bearer "-prefixet)
> 7. Klistra in i `~/Documents/max-ai-framework/config.md` under `FPL_API_TOKEN=`
> 8. Kör kommandot igen

Tokens är kortlivade (troligen timmar upp till några dygn). Räkna med att förnya varje gång kommandot ska köra live-lineup-läsning. Om token saknas fungerar kommandot ändå — bara utan diff mot live-uppställning.

## What this command does NOT do

- **Make transfers, set lineup, or activate chips.** All FPL writes are done manually in the app. Rationale: Bearer tokens are short-lived (hours–days), refresh flow is fragile, dataDome anti-bot can block automated requests, and the total time saved (~15 min/season) doesn't justify the maintenance cost.
- **Predict player scores.** Recommendations are based on FDR + recent points + fixture location. No xG/expected-points model.
- **Track leagues beyond your own.** No rival-manager analysis or differential detection.

## When to run

- **Weekly:** Friday morning before deadline (Saturday 13:30 CET usually) to get the plan
- **Post-GW:** Monday morning after games to log transfers + refresh snapshot + update ticker for the next window
- **Ad hoc:** whenever a chip decision or major transfer looms

Command is on-demand only (no cron). Invoke as `/fpl-p`.
