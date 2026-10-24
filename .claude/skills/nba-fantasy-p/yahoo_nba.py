# /// script
# requires-python = ">=3.11"
# dependencies = ["requests", "beautifulsoup4"]
# ///
import argparse
import datetime as dt
import json
import re
import subprocess
import sys
import time
from functools import lru_cache
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

CONFIG = Path.home() / "Documents/max-ai-framework/config.md"
CACHE = Path.home() / ".cache/nba-fantasy-p"
STATE = Path.home() / ".local/state/nba-fantasy-p"
BASE = "https://basketball.fantasysports.yahoo.com/nba/"
ESPN = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
ET_TZ = ZoneInfo("America/New_York")

TEAM_ALIAS = {"PHO": "PHX", "UTA": "UTAH", "WAS": "WSH", "GSW": "GS", "NYK": "NY",
              "SAS": "SA", "NOP": "NO", "BRK": "BKN", "BKLYN": "BKN", "CHO": "CHA"}
NOT_STARTABLE = {"O", "INJ", "SUSP", "NA"}
DOUBTFUL = {"GTD", "DTD", "Q", "D"}
RESERVE_SLOTS = {"BN", "IL", "IL+", "NA"}
KEEP_BONUS = 0.0005
ROSTER_STATS = ("S_PS7", "S_AL30", "S_AS_2025")
FA_STATS = ("S_PS7", "S_AL30")


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
    a = (abbr or "").upper().lstrip("@")
    return TEAM_ALIAS.get(a, a)


def num(v):
    v = (v or "").strip().rstrip("%")
    if v in ("", "-"):
        return None
    if re.fullmatch(r"\d+:\d\d", v):
        m, s = v.split(":")
        return round(int(m) + int(s) / 60, 2)
    try:
        return float(v)
    except ValueError:
        return v


def clean_label(s):
    s = re.sub(r"[-]", "", s).strip()
    return "Opp" if s.startswith("Opp") else s


# ---------- public pages ----------

_last = [0.0]


def page(path):
    wait = 1.0 - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    r = requests.get(BASE + path, headers={"User-Agent": UA}, timeout=40)
    _last[0] = time.time()
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    if soup.find("table") is None:
        raise RuntimeError(f"No tables on {path}: page layout changed or league no longer public")
    return soup


def parse_player_cell(td):
    a = td.select_one("a.name")
    tp = td.select_one(".ysf-player-name .D-b") or td.select_one(".ysf-player-name span.Fz-xxs")
    team, _, pos = clean_label(tp.get_text(strip=True) if tp else "").partition(" - ")
    status = td.select_one(".F-injury")
    game = td.select_one(".ysf-game-status")
    return {
        "id": a.get("data-ys-playerid") if a else None,
        "name": a.get_text(strip=True) if a else td.get_text(" ", strip=True),
        "team": norm_team(team),
        "positions": [p for p in pos.split(",") if p],
        "status": status.get_text(strip=True) if status else None,
        "game": game.get_text(" ", strip=True) if game else None,
    }


def player_table(table):
    rows = table.find_all("tr")
    header = next((r for r in rows if r.find("th", class_="player") or
                   any(clean_label(th.get_text(" ", strip=True)) in ("Players", "Pos") for th in r.find_all("th"))), None)
    if header is None:
        return []
    labels = [clean_label(th.get_text(" ", strip=True)) for th in header.find_all("th")
              for _ in range(int(th.get("colspan", 1)))]
    out = []
    for tr in rows:
        tds = tr.find_all("td")
        if not tds or not tr.find("td", class_="player"):
            continue
        p, stats = {}, {}
        for label, td in zip(labels, tds):
            if "player" in (td.get("class") or []):
                p |= parse_player_cell(td)
            elif label == "Pos":
                p["selected"] = td.get_text(strip=True)
            elif label in ("Opp", "Roster Status"):
                p["opp" if label == "Opp" else "owner"] = td.get_text(" ", strip=True) or None
            elif label in ("% Ros", "% Start", "Pre-Season", "Current", "GP*", "MPG", "MIN*") or re.fullmatch(r"[A-Z0-9%]+\*?", label):
                stats[label.rstrip("*")] = num(td.get_text(strip=True))
        p["percent_owned"] = stats.pop("% Ros", None) or 0.0
        p["percent_started"] = stats.pop("% Start", None)
        p["rank_preseason"] = stats.pop("Pre-Season", None)
        p["rank_current"] = stats.pop("Current", None)
        p["stats"] = stats
        out.append(p)
    return out


def players_list(lid, stat, **filters):
    q = "&".join(f"{k}={v}" for k, v in ({"status": "A", "pos": "P", "stat1": stat, "sort": "AR", "sdir": 1} | filters).items())
    return player_table(page(f"{lid}/players?{q}").find_all("table")[0])


def available(lid, stat, count):
    out = []
    for start in range(0, count, 25):
        batch = players_list(lid, stat, count=start)
        out += batch
        if len(batch) < 25:
            break
    return out[:count]


def team_roster(lid, tid, day=None):
    q = f"?date={day}&stat1=S&stat2=D" if day else ""
    soup = page(f"{lid}/{tid}/team{q}")
    title = soup.title.get_text(strip=True) if soup.title else ""
    for t in soup.find_all("table"):
        players = player_table(t)
        if players and "selected" in players[0]:
            return title.split(" - ")[-1].split(" | ")[0], players
    raise RuntimeError(f"No roster table on team page {tid}")


@lru_cache(None)
def settings(lid):
    soup = page(f"{lid}/settings")
    raw = {}
    for tr in soup.find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["th", "td"])]
        if len(cells) == 2 and cells[0]:
            raw[cells[0].replace("\xa0", " ").rstrip(":")] = cells[1]
    slots = [s.strip() for s in raw.get("Roster Positions", "").split(",") if s.strip()]
    cats = re.findall(r"\(([^)]+)\)", raw.get("Players Stat Categories", ""))
    return {"roster_slots": slots, "categories": cats, "raw": raw}


def league_home(lid, week=None):
    soup = page(f"{lid}" + (f"?matchup_week={week}&module=matchups&lhst=matchups" if week else ""))
    standings = []
    for tr in soup.find_all("table")[0].find_all("tr")[1:]:
        tds = tr.find_all("td")
        link = tr.find("a", href=re.compile(rf"/nba/{lid}/\d+$"))
        if len(tds) >= 3 and link:
            cells = [td.get_text(" ", strip=True) for td in tds]
            standings.append({"rank": cells[0], "team": cells[1], "id": link["href"].rsplit("/", 1)[1],
                              "wlt": cells[2], "waiver": cells[6] if len(cells) > 6 else None,
                              "moves": cells[7] if len(cells) > 7 else None})
    pairs = sorted({tuple(re.search(r"week=(\d+)&mid1=(\d+)&mid2=(\d+)", a["href"]).groups())
                    for a in soup.find_all("a", href=re.compile(r"matchup\?week=\d+&mid1=\d+&mid2=\d+$"))})
    return {"standings": standings, "matchups": [{"week": w, "mid1": a, "mid2": b} for w, a, b in pairs]}


def matchup(lid, tid, week=None):
    q = f"week={week}&mid1={tid}" if week else f"mid1={tid}"
    soup = page(f"{lid}/matchup?{q}")
    tables = soup.find_all("table")
    totals = next(t for t in tables if t.find("th") and t.find("th").get_text(strip=True) == "Team")
    rows = totals.find_all("tr")
    labels = [clean_label(th.get_text(strip=True)).rstrip("*") for th in rows[0].find_all(["th", "td"])]
    teams = []
    for tr in rows[1:]:
        cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
        stats = {l: num(c) for l, c in zip(labels[1:-1], cells[1:-1])}
        teams.append({"name": cells[0], "stats": stats, "category_wins": num(cells[-1])})
    days = sorted({m.group(1) for a in soup.find_all("a", href=True)
                   if (m := re.search(r"date=(\d{4}-\d\d-\d\d)", a["href"])) and "mid1=" in a["href"]})
    ids = [m.group(1) for a in soup.find_all("a", href=True) if (m := re.search(r"mid2=(\d+)", a["href"]))]
    sides = [player_table(t) for t in tables if t.find("td", class_="player")]
    return {"week": week or re.search(r"Week (\d+)", soup.get_text(" ")).group(1),
            "start": days[0] if days else None, "end": days[-1] if days else None,
            "opponent_id": ids[0] if ids else None, "teams": teams,
            "players": {"me": sides[0] if sides else [], "opponent": sides[1] if len(sides) > 1 else []}}


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

def merge_stats(base, lists):
    by_id = {p["id"]: p for p in base}
    for stat, players in lists.items():
        for p in players:
            if p["id"] not in by_id:
                by_id[p["id"]] = {k: v for k, v in p.items() if k != "stats"}
            by_id[p["id"]].setdefault("by_stat", {})[stat] = p["stats"]
    for p in by_id.values():
        p.pop("stats", None)
    return list(by_id.values())


def cmd_dump(args):
    cfg = load_config()
    lid, tid = cfg["YAHOO_NBA_LEAGUE_ID"], cfg["YAHOO_NBA_TEAM_ID"]
    today = today_et()
    m = matchup(lid, tid, args.week)
    week_start = dt.date.fromisoformat(m["start"]) if m["start"] else today
    week_end = dt.date.fromisoformat(m["end"]) if m["end"] else today + dt.timedelta(days=6 - today.weekday())
    nxt_start, nxt_end = week_end + dt.timedelta(days=1), week_end + dt.timedelta(days=7)
    sched = schedule(today, max(nxt_end, today + dt.timedelta(days=6)))
    oid = m["opponent_id"]

    def roster_with_stats(team_id):
        name, players = team_roster(lid, team_id)
        lists = {s: players_list(lid, s, status="ALL", fteam=team_id) for s in ROSTER_STATS}
        return name, merge_stats(players, lists)

    my_name, mine = roster_with_stats(tid)
    opp_name, opp = roster_with_stats(oid) if oid else (None, [])
    fas = merge_stats([], {s: available(lid, s, args.fa_count) for s in FA_STATS})

    for p in mine + opp + fas:
        p["games_left_week"] = games_between(sched, p["team"], max(today, week_start), week_end)
        p["games_next_week"] = games_between(sched, p["team"], nxt_start, nxt_end)
        p["games_next_7"] = games_between(sched, p["team"], today, today + dt.timedelta(days=6))
        ps7 = (p.get("by_stat") or {}).get("S_PS7") or {}
        gp = ps7.get("GP") or p["games_next_7"]
        if gp and ps7:
            p["proj_per_game"] = {k: (round(v / gp, 2) if isinstance(v, float) and "%" not in k else v)
                                  for k, v in ps7.items() if k not in ("GP", "MPG")}

    home = league_home(lid)
    out = {
        "generated": dt.datetime.now(ET_TZ).isoformat(timespec="minutes"),
        "today_et": today.isoformat(),
        "league_id": lid, "team_id": tid,
        "settings": settings(lid),
        "standings": home["standings"],
        "week": {"number": m["week"], "start": week_start.isoformat(), "end": week_end.isoformat(),
                 "next": {"start": nxt_start.isoformat(), "end": nxt_end.isoformat()}},
        "matchup": {"teams": m["teams"], "opponent_id": oid},
        "my_team": {"name": my_name, "roster": mine},
        "opponent": {"name": opp_name, "roster": opp},
        "free_agents": fas,
        "unmapped_teams": sorted({p["team"] for p in mine + opp + fas if p["team"] and p["team"] not in sched}),
    }
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"dump-{today}.json"
    path.write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(path)


def cmd_league(args):
    cfg = load_config()
    lid = cfg["YAHOO_NBA_LEAGUE_ID"]
    home = league_home(lid, args.week)
    if args.details:
        home["matchup_details"] = [matchup(lid, m["mid1"], m["week"]) | {"mid1": m["mid1"]} for m in home["matchups"]]
    print(json.dumps(home, indent=1, ensure_ascii=False))


# ---------- lineup check ----------

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

    return {candidates[i][0]["id"]: slots[j] for i, j in best(0, 0)[1]}


def plan_lineup(players, roster_slots, sched, day, now_utc):
    games = {t: [g for g in gs if g["date"] == day.isoformat()] for t, gs in sched.items()}

    def locked(p):
        return any(dt.datetime.fromisoformat(g["start_utc"].replace("Z", "+00:00")) <= now_utc
                   for g in games.get(p["team"], []))

    slots = [s for s in roster_slots if s not in RESERVE_SLOTS]
    fixed, movable = {}, []
    for p in players:
        if p["selected"] in {"IL", "IL+", "NA"} or locked(p):
            fixed[p["id"]] = p["selected"]
            if p["selected"] in slots:
                slots.remove(p["selected"])
        else:
            movable.append(p)
    candidates = [(p, weight(p, bool(games.get(p["team"])))) for p in movable]
    candidates.sort(key=lambda c: -(c[1] or -1))
    assigned = optimize(tuple(candidates), tuple(slots))
    target = {p["id"]: assigned.get(p["id"], "BN") for p in movable}
    changes = [(p, p["selected"], target[p["id"]]) for p in movable if p["selected"] != target[p["id"]]]
    return target, fixed, changes


def active_starters(players, sched, day, slots):
    playing = {t for t, gs in sched.items() if any(g["date"] == day.isoformat() for g in gs)}
    return sum(1 for p in players if slots.get(p["id"], p["selected"]) not in RESERVE_SLOTS
               and p["team"] in playing and p["status"] not in NOT_STARTABLE)


def log(line):
    STATE.mkdir(parents=True, exist_ok=True)
    with (STATE / "lineup.log").open("a") as f:
        f.write(f"{dt.datetime.now().isoformat(timespec='seconds')}\t{line}\n")


def notify(msg):
    msg = msg.replace('"', "'")
    subprocess.run(["osascript", "-e", f'display notification "{msg}" with title "nba-fantasy-p"'],
                   check=False, capture_output=True)


def cmd_lineup(args):
    day = dt.date.fromisoformat(args.date) if args.date else today_et()
    try:
        cfg = load_config()
        lid, tid = cfg["YAHOO_NBA_LEAGUE_ID"], cfg["YAHOO_NBA_TEAM_ID"]
        _, players = team_roster(lid, tid, day)
        sched = schedule(day, day)
        target, fixed, changes = plan_lineup(players, settings(lid)["roster_slots"], sched, day,
                                             dt.datetime.now(dt.timezone.utc))
        now_active = active_starters(players, sched, day, {})
        best_active = active_starters(players, sched, day, target | fixed)
        lost = best_active - now_active
        moves = [{"name": p["name"], "team": p["team"], "status": p["status"], "from": a, "to": b}
                 for p, a, b in changes]
        summary = "; ".join(f"{m['name']} {m['from']}->{m['to']}" for m in moves) or "optimal"
        log(f"{day}\t{'fix' if lost > 0 else 'ok'}\tactive {now_active}/{best_active}\t{summary}")
        if lost > 0 and args.notify:
            notify(f"{day}: {lost} more starter(s) with games possible. Open Yahoo or ask Claude.")
        print(json.dumps({"date": day.isoformat(), "active_now": now_active, "active_best": best_active,
                          "moves": moves, "fixed": fixed}, indent=1, ensure_ascii=False))
    except Exception as e:
        log(f"{day}\terror\t{e}")
        if args.notify:
            notify(f"Lineup check failed for {day}: {str(e)[:120]}")
        raise


def main():
    ap = argparse.ArgumentParser(description="Yahoo Fantasy NBA helper for nba-fantasy-p (public league pages)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("dump")
    d.add_argument("--week")
    d.add_argument("--fa-count", type=int, default=50)
    d.set_defaults(fn=cmd_dump)

    lg = sub.add_parser("league")
    lg.add_argument("--week")
    lg.add_argument("--details", action="store_true")
    lg.set_defaults(fn=cmd_league)

    s = sub.add_parser("schedule")
    s.add_argument("--start")
    s.add_argument("--end")
    s.set_defaults(fn=cmd_schedule)

    lu = sub.add_parser("lineup")
    lu.add_argument("--date")
    lu.add_argument("--notify", action="store_true")
    lu.set_defaults(fn=cmd_lineup)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
