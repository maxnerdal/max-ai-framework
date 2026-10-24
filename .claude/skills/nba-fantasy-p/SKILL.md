---
name: nba-fantasy-p
description: Manage Max's Yahoo Fantasy Basketball team "THE CHAMP" in Uppsala Fantasy League (H2H categories, daily lineups). Weekly matchup plan with per-category projections against this week's opponent, waiver and streaming recommendations with add/drop pairs, lineup fixes, and a league-wide view of all matchups. Reads the league's public Yahoo pages; changes are made in Max's Chrome. Updates the Obsidian project anchor. Triggers on: fantasy basketball, NBA fantasy, THE CHAMP, Yahoo fantasy, matchup this week, who should I stream, waivers, add/drop, set my lineup, category projection.
---

# nba-fantasy-p

Yahoo Fantasy NBA, league `79469`, team `10` ("THE CHAMP"), 12 teams, keeper league, H2H "one win" over 11 categories.

**Lineups are weekly.** The "Weekly Deadline" setting is "Weekly on Monday": the lineup locks for the whole fantasy week (Mon to Sun), and only starters' games count. Max sets it once a week, by Sunday at the latest. Every projection uses the starters × their games that week, never bench games. Add/drops made before the deadline count for the coming week. The `lineup` command and its optimiser still evaluate a single date; for the weekly lineup, use the weekly plan below. All reading goes through `yahoo_nba.py` next to this file, which scrapes the league's public pages (no login) and the ESPN schedule. Run it with `uv run ~/.claude/skills/nba-fantasy-p/yahoo_nba.py <cmd>`.

The Yahoo Fantasy API needs an approved application (applied 2026-10-24). Until it is approved, `yahoo_api.py` stays unused. It has the OAuth client, lineup PUT and add/drop, tested only up to the token exchange. Credentials are in `~/.config/max-ai-framework/yahoo-oauth.json`. If approval comes, switch reads and writes over to it.

## CLI

| Command | What it does |
|---|---|
| `dump [--week N] [--fa-count 50]` | Writes `~/.cache/nba-fantasy-p/dump-<date>.json` and prints the path. |
| `league [--week N] [--details]` | Standings and the week's matchup pairs. `--details` adds each matchup's category totals and both rosters' stats. Use it for the league recap. |
| `lineup [--date] [--notify]` | Read-only check of the lineup for a US Eastern date. Prints the moves that would start more players with games. |
| `schedule [--start] [--end]` | Games per NBA team in a date range. |

### What `dump` contains

- **Settings:** roster slots, the scored categories, and the raw settings. That includes "Max Acquisitions per Week" (4) and the weekly deadline (Monday).
- **League:** standings, the week's dates and the next week's dates.
- **Matchup:** the score for both teams (`stats`, `category_wins`).
- **Players:** `my_team.roster`, `opponent.roster` and `free_agents`. Each player has these fields:
  - `selected`: the roster slot (roster players only)
  - `status`: Q, GTD, O, INJ and so on
  - `opp`: today's opponent
  - `percent_owned`: % rostered in Yahoo leagues
  - `owner`: FA, W (waivers) or a team name
  - `by_stat`: Yahoo's stat views. `S_PS7` is Yahoo's projection for the next 7 days, as totals including projected GP. `S_AL30` is the last-30-day average. `S_AS_2025` is last season's average, for rostered players only.
  - `proj_per_game`: `S_PS7` divided by its GP
  - `games_left_week`, `games_next_week`
- **Check:** `unmapped_teams` must be empty. Otherwise a team abbreviation is missing from `TEAM_ALIAS` and that team's game counts read 0.

FGA and FTA are display-only. They are used only to compute FG% and FT%.

## Modes

### Weekly plan (Monday morning, or when Max asks how the matchup looks)
1. Run `dump`.
2. Per-game rate per player: use `proj_per_game` (Yahoo's projection, which already blends history and role). Fall back to `S_AL30` blended with `S_AS_2025` when it is missing. Drop players who are O or INJ, or sit in IL. Weight Q/GTD at 0.5.
3. Rest-of-week projection = current matchup `stats` + Σ(rate × `games_left_week`) over the starters. FG% and FT% come from projected makes and attempts, never from averaging percentages. TO: lower wins.
4. Label each category **säker**, **sväng** or **förlorad**. Safe and lost mean a projected margin above about 10%; anything closer is a swing. Say which categories Max is effectively punting.
5. Write the `matchup` and `status` sections of the anchor and append one line to Beslutslogg.

### Waivers and streaming
1. Use today's dump.
2. Score each available player by Σ of z-scores over the **swing** categories × `games_left_week`. The z-scores are taken from `proj_per_game` against the rostered pool. When two days or fewer are left in the week, also show the next-week value from `games_next_week`.
3. Drop candidates: my weakest players on the same measure, never one of my top 8 by `percent_owned`.
4. Count adds already made this week from Transaktioner against the limit of 4 per week. Waiver players (`owner` starting with W) clear after 3 days, so they don't help this week.
5. Present at most 5 numbered pairs: `+ Add (team, games left, categories helped) / − Drop (why)`. Write them to the `waivers` section.

### Making changes (Chrome, only after Max says yes)
Load the `anthropic-skills:chrome-browser` skill first. Max is logged in to Yahoo in his Chrome.
- **Add/drop:** go to `basketball.fantasysports.yahoo.com/nba/79469/players`, search the player, click the add button, choose the drop, and confirm. Do only the numbered pairs Max approved, one at a time. Report each result and append it to Transaktioner.
- **Lineup:** go to `basketball.fantasysports.yahoo.com/nba/79469/10`. Make the moves from `lineup`, or use Yahoo's "Start Active Players" button and then check with `lineup` again.
- Never accept or propose trades, and never change settings.

### League recap (Sunday night or Monday)
Run `league --week N --details`. Write about every team: the result, the categories won, standout players. Lead with the closest matchups, decided by the fewest categories or the tightest margins. A pending feature; agree on format and destination with Max the first time.

### Weekly lineup (by Sunday)
Run `dump --week <next week>`. Then choose the 9 starters that maximise Σ(per-game z-score × games that week), within the slot constraints, using `optimize` from the script. Flag Q/D/GTD players and check their news before Max locks the lineup. Z-scores must use the same basis as the pool: compare `proj_per_game` against the `S_PS7` per-game values of all rostered players in the 12 teams (`players_list(..., "S_PS7", status="ALL", fteam=1..12)`). Never mix a projection with last season's averages.

Keeper league: never suggest dropping a high-ownership core player on the strength of a few games of projection. Before proposing any drop, read `## Strategi` in the anchor. Players listed under "Släpps inte" are never drop candidates and are excluded from swap tests.

The launchd plist in `launchd/` was built for daily lineups. It is not installed now that lineups are weekly.

Lineup logic:
- Maximise starters with a game. Healthy players go before Q/GTD.
- Never start O, INJ, SUSP or NA. Never move players in IL or players whose game has started.
- Break ties on `percent_owned`, and prefer keeping players in their current slot.

## Vault anchor

`YAHOO_NBA_PROJECT_DOC` (`Areas/Personal/Projects/THE CHAMP.md`). The auto-managed regions use sentinels, and everything outside them belongs to Max:
```
<!-- nba-fantasy-p:section=status:start --> ... <!-- nba-fantasy-p:section=status:end -->
```
Sections:
- `status`: record, rank, this week's score per category
- `matchup`: a projection table with columns category | me | opponent | class
- `waivers`: the current pairs

Replace each only between its sentinels. `## Transaktioner` and `## Beslutslogg` are append-only. Lineup checks are not logged to the anchor.

## Chat summary

After a run, give three blocks:
- **Veckoläge:** the score now, safe/swing/lost categories, games left for each side.
- **Förslag:** the numbered add/drop pairs and any lineup moves.
- **Handling:** what needs Max's yes.

## Fragility

Scraping depends on Yahoo's HTML. `page()` raises an error when a page has no tables, and the parser keys on header labels, not column positions. When something breaks, fetch the page, look at the header row of its table, and fix `player_table` or `matchup`. Requests are throttled to one per second; a dump makes about 15.
