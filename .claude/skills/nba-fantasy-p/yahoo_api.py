# /// script
# requires-python = ">=3.11"
# dependencies = ["requests"]
# ///
import argparse
import datetime as dt
import json
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlencode
from xml.sax.saxutils import escape
from zoneinfo import ZoneInfo

import requests

CONFIG = Path.home() / "Documents/max-ai-framework/config.md"
CREDS = Path.home() / ".config/max-ai-framework/yahoo-oauth.json"
CACHE = Path.home() / ".cache/nba-fantasy-p"
STATE = Path.home() / ".local/state/nba-fantasy-p"
API = "https://fantasysports.yahooapis.com/fantasy/v2/"
AUTH = "https://api.login.yahoo.com/oauth2/"
ESPN = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
ET_TZ = ZoneInfo("America/New_York")

TEAM_ALIAS = {"PHO": "PHX", "UTA": "UTAH", "WAS": "WSH", "GSW": "GS", "NYK": "NY",
              "SAS": "SA", "NOP": "NO", "BRK": "BKN", "BKLYN": "BKN", "CHO": "CHA"}
NOT_STARTABLE = {"O", "INJ", "SUSP", "NA"}
DOUBTFUL = {"GTD", "DTD"}
RESERVE_SLOTS = {"BN", "IL", "IL+", "NA"}
KEEP_BONUS = 0.0005


def load_config():
    cfg = {}
    for line in CONFIG.read_text().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            cfg[k.strip()] = v.strip()
    for k in ("YAHOO_NBA_LEAGUE_ID", "YAHOO_NBA_TEAM_ID"):
        if not cfg.get(k):
            sys.exit(f"{k} missing in {CONFIG}")
    return cfg


def today_et():
    return dt.datetime.now(ET_TZ).date()


def norm_team(abbr):
    a = (abbr or "").upper()
    return TEAM_ALIAS.get(a, a)


# ---------- OAuth ----------

def read_creds():
    if not CREDS.exists():
        sys.exit(f"Missing {CREDS}. Create it with client_id, client_secret (and optionally redirect_uri).")
    return json.loads(CREDS.read_text())


def write_creds(c):
    CREDS.parent.mkdir(parents=True, exist_ok=True)
    CREDS.write_text(json.dumps(c, indent=2))
    CREDS.chmod(0o600)


def token_request(c, **data):
    r = requests.post(AUTH + "get_token", auth=(c["client_id"], c["client_secret"]),
                      data={"redirect_uri": c.get("redirect_uri", "oob"), **data}, timeout=30)
    if r.status_code != 200:
        sys.exit(f"Token request failed ({r.status_code}): {r.text[:300]}")
    t = r.json()
    c["access_token"] = t["access_token"]
    c["refresh_token"] = t.get("refresh_token", c.get("refresh_token"))
    c["expires_at"] = time.time() + int(t.get("expires_in", 3600))
    write_creds(c)
    return c


def access_token():
    c = read_creds()
    if not c.get("refresh_token"):
        sys.exit("Not authorised yet. Run: yahoo_nba.py auth")
    if c.get("expires_at", 0) < time.time() + 60:
        c = token_request(c, grant_type="refresh_token", refresh_token=c["refresh_token"])
    return c["access_token"]


def cmd_auth(args):
    c = read_creds()
    if not args.code:
        q = urlencode({"client_id": c["client_id"], "redirect_uri": c.get("redirect_uri", "oob"),
                       "response_type": "code", "scope": c.get("scope", "fspt-r")})
        print(f"Open, approve, then run again with --code <code>:\n{AUTH}request_auth?{q}")
        return
    token_request(c, grant_type="authorization_code", code=args.code.strip())
    cfg = load_config()
    lk = league_key(cfg)
    root = get(f"league/{lk}/teams")
    for t in root.iter("team"):
        print(text(t, "team_key"), text(t, "name"))
    print(f"Authorised. League {lk}.")


# ---------- Yahoo API ----------

def strip_ns(root):
    for el in root.iter():
        el.tag = el.tag.split("}")[-1]
    return root


def request(method, path, body=None):
    for attempt in range(3):
        r = requests.request(method, API + path, data=body, timeout=30,
                             headers={"Authorization": f"Bearer {access_token()}",
                                      "Content-Type": "application/xml"})
        if r.status_code < 500:
            break
        time.sleep(2 * (attempt + 1))
    if r.status_code >= 400:
        raise RuntimeError(f"{method} {path} -> {r.status_code}: {r.text[:500]}")
    return strip_ns(ET.fromstring(r.content)) if r.content else None


def get(path):
    return request("GET", path)


def text(el, path, default=None):
    found = el.find(path)
    return found.text if found is not None and found.text is not None else default


def num(v):
    if v in (None, "", "-"):
        return None
    try:
        return float(v)
    except ValueError:
        return v


@lru_cache(None)
def game_key():
    return text(get("game/nba"), ".//game_key")


def league_key(cfg):
    return f"{game_key()}.l.{cfg['YAHOO_NBA_LEAGUE_ID']}"


def team_key(cfg):
    return f"{league_key(cfg)}.t.{cfg['YAHOO_NBA_TEAM_ID']}"


def parse_player(p):
    return {
        "key": text(p, "player_key"),
        "name": text(p, "name/full"),
        "team": norm_team(text(p, "editorial_team_abbr")),
        "positions": [e.text for e in p.findall("eligible_positions/position")],
        "selected": text(p, "selected_position/position"),
        "status": text(p, "status"),
        "injury_note": text(p, "injury_note"),
    }


def settings(lk):
    root = get(f"league/{lk}/settings")
    cats = [{"id": text(s, "stat_id"), "name": text(s, "display_name"),
             "sort_order": text(s, "sort_order"),
             "display_only": text(s, "is_only_display_stat") == "1"}
            for s in root.findall(".//stat_categories/stats/stat")]
    slots = [{"position": text(r, "position"), "count": int(text(r, "count", "0")),
              "starting": text(r, "is_starting_position", "1") == "1"}
             for r in root.findall(".//roster_positions/roster_position")]
    return {"categories": cats, "roster_slots": slots,
            "trade_end_date": text(root, ".//trade_end_date"),
            "max_weekly_adds": text(root, ".//max_weekly_adds"),
            "waiver_rule": text(root, ".//waiver_rule")}


def league_meta(lk):
    root = get(f"league/{lk}")
    return {k: text(root, f".//league/{k}") for k in
            ("name", "current_week", "start_week", "end_week", "start_date", "end_date")}


def game_weeks():
    root = get(f"game/{game_key()}/game_weeks")
    return [{"week": int(text(w, "week")), "start": text(w, "start"), "end": text(w, "end")}
            for w in root.iter("game_week")]


def standings(lk):
    root = get(f"league/{lk}/standings")
    return [{"key": text(t, "team_key"), "name": text(t, "name"),
             "rank": text(t, "team_standings/rank"),
             "wins": text(t, "team_standings/outcome_totals/wins"),
             "losses": text(t, "team_standings/outcome_totals/losses"),
             "ties": text(t, "team_standings/outcome_totals/ties")}
            for t in root.iter("team")]


def roster(tk, date):
    root = get(f"team/{tk}/roster;date={date}")
    return [parse_player(p) for p in root.iter("player")]


def chunks(xs, n=25):
    for i in range(0, len(xs), n):
        yield xs[i:i + n]


def enrich(lk, players):
    by_key = {p["key"]: p for p in players}
    for batch in chunks(list(by_key)):
        keys = ",".join(batch)
        for stype in ("season", "lastmonth"):
            for p in get(f"league/{lk}/players;player_keys={keys}/stats;type={stype}").iter("player"):
                by_key[text(p, "player_key")][f"stats_{stype}"] = {
                    text(s, "stat_id"): num(text(s, "value")) for s in p.findall(".//stats/stat")}
        for p in get(f"league/{lk}/players;player_keys={keys}/percent_owned").iter("player"):
            by_key[text(p, "player_key")]["percent_owned"] = num(text(p, "percent_owned/value")) or 0.0
    return players


def free_agents(lk, count, sort):
    out = []
    for start in range(0, count, 25):
        root = get(f"league/{lk}/players;status=A;sort={sort};sort_type=lastmonth;start={start};count=25")
        page = [parse_player(p) | {"ownership": text(p, "ownership/ownership_type")}
                for p in root.iter("player")]
        out += page
        if len(page) < 25:
            break
    return out


def matchup(tk, week):
    root = get(f"team/{tk}/matchups;weeks={week}")
    m = root.find(".//matchup")
    if m is None:
        return None
    teams = [{"key": text(t, "team_key"), "name": text(t, "name"),
              "stats": {text(s, "stat_id"): num(text(s, "value")) for s in t.findall("team_stats/stats/stat")}}
             for t in m.findall("teams/team")]
    return {"week": text(m, "week"), "week_start": text(m, "week_start"), "week_end": text(m, "week_end"),
            "status": text(m, "status"), "teams": teams}


# ---------- NBA schedule (ESPN) ----------

def espn_day(day):
    CACHE.joinpath("espn").mkdir(parents=True, exist_ok=True)
    f = CACHE / "espn" / f"{day:%Y%m%d}.json"
    fresh = f.exists() and (day < today_et() - dt.timedelta(days=1) or time.time() - f.stat().st_mtime < 3 * 3600)
    if not fresh:
        r = requests.get(ESPN, params={"dates": f"{day:%Y%m%d}"}, timeout=30)
        r.raise_for_status()
        games = [{"start_utc": e["date"],
                  "teams": [norm_team(c["team"]["abbreviation"]) for c in e["competitions"][0]["competitors"]]}
                 for e in r.json().get("events", [])]
        f.write_text(json.dumps(games))
    return json.loads(f.read_text())


def schedule(start, end):
    out, day = {}, start
    while day <= end:
        for g in espn_day(day):
            for t in g["teams"]:
                out.setdefault(t, []).append({"date": day.isoformat(), "start_utc": g["start_utc"]})
        day += dt.timedelta(days=1)
    return out


def games_between(sched, team, start, end):
    return sum(1 for g in sched.get(team, []) if start.isoformat() <= g["date"] <= end.isoformat())


def cmd_schedule(args):
    start = dt.date.fromisoformat(args.start) if args.start else today_et()
    end = dt.date.fromisoformat(args.end) if args.end else start + dt.timedelta(days=6)
    sched = schedule(start, end)
    rows = sorted(((t, len(gs)) for t, gs in sched.items()), key=lambda x: (-x[1], x[0]))
    print(json.dumps({"start": start.isoformat(), "end": end.isoformat(), "games": dict(rows)}, indent=1))


# ---------- dump ----------

def cmd_dump(args):
    cfg = load_config()
    lk, tk = league_key(cfg), team_key(cfg)
    today = today_et()
    meta = league_meta(lk)
    week = int(args.week or meta["current_week"])
    weeks = {w["week"]: w for w in game_weeks()}
    m = matchup(tk, week)
    wk = weeks.get(week, {})
    week_start = dt.date.fromisoformat((m or {}).get("week_start") or wk["start"])
    week_end = dt.date.fromisoformat((m or {}).get("week_end") or wk["end"])
    nxt = weeks.get(week + 1)
    sched_end = dt.date.fromisoformat(nxt["end"]) if nxt else week_end
    sched = schedule(max(today, week_start), sched_end)

    def with_games(players):
        for p in players:
            p["games_left_week"] = games_between(sched, p["team"], max(today, week_start), week_end)
            if nxt:
                p["games_next_week"] = games_between(sched, p["team"], dt.date.fromisoformat(nxt["start"]),
                                                     dt.date.fromisoformat(nxt["end"]))
        return players

    mine = with_games(enrich(lk, roster(tk, today)))
    opp_key = next((t["key"] for t in (m or {}).get("teams", []) if t["key"] != tk), None)
    opp = with_games(enrich(lk, roster(opp_key, today))) if opp_key else []
    fas = with_games(enrich(lk, free_agents(lk, args.fa_count, args.fa_sort)))

    out = {
        "generated": dt.datetime.now(ET_TZ).isoformat(timespec="minutes"),
        "today_et": today.isoformat(),
        "league_key": lk, "team_key": tk, "league": meta,
        "settings": settings(lk),
        "standings": standings(lk),
        "week": {"number": week, "start": week_start.isoformat(), "end": week_end.isoformat(), "next": nxt},
        "matchup": m,
        "my_roster": mine,
        "opponent": {"key": opp_key, "roster": opp},
        "free_agents": fas,
    }
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"dump-{today}.json"
    path.write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(path)


# ---------- lineup ----------

def startable_slots(p):
    pos = set(p["positions"])
    if pos & {"PG", "SG"}:
        pos.add("G")
    if pos & {"SF", "PF"}:
        pos.add("F")
    return pos | {"Util"}


def weight(p, plays):
    po = p.get("percent_owned") or 0.0
    if p["status"] in NOT_STARTABLE:
        return None
    if not plays:
        return po / 1000
    return (500 if p["status"] in DOUBTFUL else 1000) + po


def optimize(candidates, slots):
    @lru_cache(None)
    def best(i, used):
        if i == len(candidates):
            return 0.0, ()
        top = best(i + 1, used)
        p, w = candidates[i]
        if w is None:
            return top
        elig = startable_slots(p)
        for j, s in enumerate(slots):
            if not used >> j & 1 and s in elig:
                v, rest = best(i + 1, used | 1 << j)
                v += w + (KEEP_BONUS if p["selected"] == s else 0)
                if v > top[0]:
                    top = (v, ((i, j),) + rest)
        return top

    return {candidates[i][0]["key"]: slots[j] for i, j in best(0, 0)[1]}


def plan_lineup(players, slot_counts, sched, day, now_utc):
    games = {t: [g for g in gs if g["date"] == day.isoformat()] for t, gs in sched.items()}

    def locked(p):
        return any(dt.datetime.fromisoformat(g["start_utc"].replace("Z", "+00:00")) <= now_utc
                   for g in games.get(p["team"], []))

    slots = [s["position"] for s in slot_counts for _ in range(s["count"])
             if s["starting"] and s["position"] not in RESERVE_SLOTS]
    fixed, movable = {}, []
    for p in players:
        if p["selected"] in {"IL", "IL+", "NA"} or locked(p):
            fixed[p["key"]] = p["selected"]
            if p["selected"] in slots:
                slots.remove(p["selected"])
        else:
            movable.append(p)
    candidates = [(p, weight(p, bool(games.get(p["team"])))) for p in movable]
    candidates.sort(key=lambda c: -(c[1] or -1))
    assigned = optimize(tuple(candidates), tuple(slots))
    target = {p["key"]: assigned.get(p["key"], "BN") for p in movable}
    changes = [(p, p["selected"], target[p["key"]]) for p in movable if p["selected"] != target[p["key"]]]
    idle = [p["name"] for p in movable if target[p["key"]] == "BN" and games.get(p["team"])
            and p["status"] not in NOT_STARTABLE]
    return target, fixed, changes, idle


def roster_xml(day, target):
    players = "".join(f"<player><player_key>{escape(k)}</player_key><position>{escape(v)}</position></player>"
                      for k, v in target.items())
    return (f'<?xml version="1.0"?><fantasy_content><roster><coverage_type>date</coverage_type>'
            f"<date>{day}</date><players>{players}</players></roster></fantasy_content>")


def log(line):
    STATE.mkdir(parents=True, exist_ok=True)
    with (STATE / "lineup.log").open("a") as f:
        f.write(f"{dt.datetime.now().isoformat(timespec='seconds')}\t{line}\n")


def notify(msg):
    subprocess.run(["osascript", "-e", f'display notification "{msg}" with title "nba-fantasy-p"'],
                   check=False, capture_output=True)


def cmd_set_lineup(args):
    day = dt.date.fromisoformat(args.date) if args.date else today_et()
    try:
        cfg = load_config()
        lk, tk = league_key(cfg), team_key(cfg)
        players = enrich(lk, roster(tk, day))
        sched = schedule(day, day)
        target, fixed, changes, idle = plan_lineup(players, settings(lk)["roster_slots"], sched, day,
                                                   dt.datetime.now(dt.timezone.utc))
        summary = "; ".join(f"{p['name']} {a}->{b}" for p, a, b in changes) or "no change"
        if idle:
            summary += f" | playing but benched: {', '.join(idle)}"
        if changes and not args.dry_run:
            request("PUT", f"team/{tk}/roster", roster_xml(day, target))
        mode = "dry-run" if args.dry_run else ("applied" if changes else "ok")
        log(f"{day}\t{mode}\t{summary}")
        print(json.dumps({"date": day.isoformat(), "mode": mode, "changes": [
            {"name": p["name"], "team": p["team"], "status": p["status"], "from": a, "to": b} for p, a, b in changes],
            "fixed": fixed, "playing_but_benched": idle}, indent=1, ensure_ascii=False))
    except (Exception, SystemExit) as e:
        log(f"{day}\terror\t{e}")
        if args.notify:
            notify(f"Lineup failed for {day}: {str(e)[:120]}")
        raise


# ---------- transactions ----------

def cmd_add_drop(args):
    if not (args.add or args.drop):
        sys.exit("Give --add and/or --drop (player keys).")
    if not args.confirm:
        sys.exit("Refusing without --confirm. Only pass it after Max has approved this exact move.")
    cfg = load_config()
    lk, tk = league_key(cfg), team_key(cfg)
    kind = "add/drop" if args.add and args.drop else ("add" if args.add else "drop")
    parts = []
    if args.add:
        parts.append(f"<player><player_key>{escape(args.add)}</player_key><transaction_data><type>add</type>"
                     f"<destination_team_key>{tk}</destination_team_key></transaction_data></player>")
    if args.drop:
        parts.append(f"<player><player_key>{escape(args.drop)}</player_key><transaction_data><type>drop</type>"
                     f"<source_team_key>{tk}</source_team_key></transaction_data></player>")
    faab = f"<faab_bid>{int(args.faab)}</faab_bid>" if args.faab is not None else ""
    body = (f'<?xml version="1.0"?><fantasy_content><transaction><type>{kind}</type>{faab}'
            f"<players>{''.join(parts)}</players></transaction></fantasy_content>")
    root = request("POST", f"league/{lk}/transactions", body)
    status = text(root, ".//transaction/status") if root is not None else None
    tx_type = text(root, ".//transaction/type") if root is not None else None
    print(json.dumps({"type": tx_type or kind, "status": status, "add": args.add, "drop": args.drop}))


def main():
    ap = argparse.ArgumentParser(description="Yahoo Fantasy NBA helper for nba-fantasy-p")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("auth")
    a.add_argument("--code")
    a.set_defaults(fn=cmd_auth)

    d = sub.add_parser("dump")
    d.add_argument("--week")
    d.add_argument("--fa-count", type=int, default=50)
    d.add_argument("--fa-sort", default="AR")
    d.set_defaults(fn=cmd_dump)

    s = sub.add_parser("schedule")
    s.add_argument("--start")
    s.add_argument("--end")
    s.set_defaults(fn=cmd_schedule)

    lu = sub.add_parser("set-lineup")
    lu.add_argument("--date")
    lu.add_argument("--dry-run", action="store_true")
    lu.add_argument("--notify", action="store_true")
    lu.set_defaults(fn=cmd_set_lineup)

    t = sub.add_parser("add-drop")
    t.add_argument("--add")
    t.add_argument("--drop")
    t.add_argument("--faab", type=int)
    t.add_argument("--confirm", action="store_true")
    t.set_defaults(fn=cmd_add_drop)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
