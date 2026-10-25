# /// script
# requires-python = ">=3.11"
# dependencies = ["requests", "beautifulsoup4"]
# ///
import argparse
import json
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE = "https://basketball.fantasysports.yahoo.com/"
SLUG = "league/uppsalafantasyleague/"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
OUT = Path.home() / ".cache/nba-fantasy-p/ufl-history.json"


def get(url):
    time.sleep(1)
    r = requests.get(url if url.startswith("http") else BASE + url, headers={"User-Agent": UA}, timeout=40)
    r.raise_for_status()
    return r.url, BeautifulSoup(r.text, "html.parser")


def clean(s):
    return re.sub(r"[-]", "", s).strip()


def team_id(a):
    m = re.search(r"/nba/\d+/(\d+)$", a["href"]) if a else None
    return m.group(1) if m else None


def standings(soup):
    for t in soup.find_all("table"):
        head = [clean(th.get_text(" ", strip=True)) for th in t.find("tr").find_all(["th", "td"])]
        if head[:3] == ["Rank", "Team", "W-L-T"]:
            rows = []
            for tr in t.find_all("tr")[1:]:
                c = [clean(td.get_text(" ", strip=True)) for td in tr.find_all("td")]
                if len(c) < 3:
                    continue
                w, l, ti = (c[2].split("-") + ["0", "0", "0"])[:3]
                rows.append({"rank": int(c[0].lstrip("*")), "playoffs": c[0].startswith("*"), "team": c[1],
                             "team_id": team_id(tr.find("a", href=True)), "wins": int(w), "losses": int(l), "ties": int(ti),
                             "moves": c[7] if len(c) > 7 else None})
            return rows
    return []


def podium(soup):
    t = soup.find("table")
    if not t or "1st Place" not in t.get_text():
        return []
    return [clean(td.get_text(" ", strip=True)) for td in t.find_all("tr")[1].find_all("td")[:3]]


def draft(path):
    _, soup = get(path + "/draftresults")
    picks = []
    for t in soup.find_all("table"):
        m = re.match(r"Round (\d+)", t.find("tr").get_text(" ", strip=True))
        if not m:
            continue
        for tr in t.find_all("tr")[1:]:
            c = [clean(td.get_text(" ", strip=True)) for td in tr.find_all("td")]
            if len(c) >= 3:
                picks.append({"round": int(m.group(1)), "pick": int(c[0].rstrip(".")), "player": c[1].split(" (")[0], "team": c[2]})
    return picks


def trades(path):
    _, soup = get(path + "/teams")
    out = {}
    for tr in soup.select("table tr")[1:]:
        c = [clean(td.get_text(" ", strip=True)) for td in tr.find_all("td")]
        if len(c) >= 6:
            out[c[0]] = {"moves": c[4], "trades": c[5]}
    return out


def season(year):
    _, soup = get(SLUG + str(year))
    ids = [m.group(1) for a in soup.find_all("a", href=True)
           if (m := re.search(rf"(?:/{year})?/nba/(\d+)/\d+$", a["href"]))]
    if not ids:
        raise RuntimeError("no league id found on season page")
    lid = max(set(ids), key=ids.count)
    path = f"{year}/nba/{lid}"
    _, soup = get(path + "?lhst=stand")
    picks = draft(path)
    first_round = sorted((p for p in picks if p["round"] == 1), key=lambda p: p["pick"])
    return {"year": year, "league_id": lid, "podium": podium(soup), "standings": standings(soup),
            "draft_order": [p["team"] for p in first_round], "draft": picks, "teams": trades(path)}


def main():
    ap = argparse.ArgumentParser(description="Collect Uppsala Fantasy League history from public Yahoo pages")
    ap.add_argument("--from-year", type=int, default=2011)
    ap.add_argument("--to-year", type=int, default=2025)
    args = ap.parse_args()
    data = json.loads(OUT.read_text()) if OUT.exists() else {}
    for year in range(args.from_year, args.to_year + 1):
        try:
            data[str(year)] = season(year)
            s = data[str(year)]
            print(year, s["league_id"], "teams", len(s["standings"]), "picks", len(s["draft"]), "podium", s["podium"])
        except Exception as e:
            print(year, "failed:", e)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1, ensure_ascii=False))
    print(OUT)


if __name__ == "__main__":
    main()
