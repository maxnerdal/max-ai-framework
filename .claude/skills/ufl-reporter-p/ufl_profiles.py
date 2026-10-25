# /// script
# requires-python = ">=3.11"
# ///
import json
import re
import sys
from pathlib import Path

HISTORY = Path.home() / ".cache/nba-fantasy-p/ufl-history.json"
VAULT = Path.home() / "Documents/obsidian-vault/Areas/Personal/Projects/Uppsala Fantasy League"
START, END = "<!-- ufl-reporter-p:section=stats:start -->", "<!-- ufl-reporter-p:section=stats:end -->"


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    fm = {}
    for line in (m.group(1).splitlines() if m else []):
        k, _, v = line.partition(":")
        fm[k.strip()] = v.strip()
    return fm


def names_of(fm):
    team = fm.get("lag", "")
    aliases = [a.strip().strip('"') for a in fm.get("tidigare_namn", "").strip("[]").split(",") if a.strip()]
    return [team] + aliases


def finished_seasons(history):
    return {y: s for y, s in history.items() if s["podium"]}


def stats_for(names, seasons):
    rows = []
    for y, s in sorted(seasons.items()):
        n = len(s["standings"])
        hit = next((r for r in s["standings"] if r["team"] in names), None)
        if not hit:
            continue
        slot = next((i + 1 for i, t in enumerate(s["draft_order"]) if t in names), None)
        rows.append({"year": y, "team": hit["team"], "rank": hit["rank"], "teams": n,
                     "record": f"{hit['wins']}-{hit['losses']}-{hit['ties']}", "playoffs": hit["playoffs"],
                     "slot": slot, "trades": (s["teams"].get(hit["team"]) or {}).get("trades")})
    return rows


def render(rows):
    if not rows:
        return "Ingen historik hittad för lagnamnen ovan."
    w = sum(int(r["record"].split("-")[0]) for r in rows)
    l = sum(int(r["record"].split("-")[1]) for r in rows)
    t = sum(int(r["record"].split("-")[2]) for r in rows)
    lines = [
        f"- **Säsonger:** {len(rows)} ({rows[0]['year']}–{rows[-1]['year']})",
        f"- **Titlar:** {sum(r['rank'] == 1 for r in rows)}" + "".join(f" ({r['year']})" for r in rows if r["rank"] == 1),
        f"- **Topp 3:** {sum(r['rank'] <= 3 for r in rows)}",
        f"- **Botten 3:** {sum(r['rank'] > r['teams'] - 3 for r in rows)}",
        f"- **Slutspel:** {sum(r['playoffs'] for r in rows)}",
        f"- **Snittplacering:** {sum(r['rank'] for r in rows) / len(rows):.1f}",
        f"- **Matchrekord totalt:** {w}-{l}-{t} ({w / max(w + l + t, 1):.3f})",
        f"- **Förstaval i draften:** {sum(r['slot'] == 1 for r in rows)}, topp 3-val: {sum((r['slot'] or 99) <= 3 for r in rows)}",
        "",
        "| Säsong | Lagnamn | Plats | Rekord | Draftplats | Trades |",
        "|---|---|---:|---|---:|---:|",
    ]
    lines += [f"| {r['year']} | {r['team']} | {r['rank']}/{r['teams']}{' *' if r['playoffs'] else ''} | {r['record']} | "
              f"{r['slot'] or '–'} | {r['trades'] or '–'} |" for r in rows]
    lines += ["", "\\* = slutspel. Draftplats = position i första rundan (keeper-ligor: kan avvika från lottning)."]
    return "\n".join(lines)


def main():
    history = json.loads(HISTORY.read_text())
    seasons = finished_seasons(history)
    for f in sorted((VAULT / "Managers").glob("*.md")):
        text = f.read_text()
        if START not in text:
            print("skip (no sentinels):", f.name)
            continue
        body = render(stats_for(names_of(frontmatter(text)), seasons))
        text = re.sub(re.escape(START) + ".*?" + re.escape(END), f"{START}\n{body}\n{END}", text, flags=re.S)
        f.write_text(text)
        print("updated", f.name)
    if "--table" in sys.argv:
        print("\n| Säsong | Etta | Tvåa | Trea | Sist |\n|---|---|---|---|---|")
        for y, s in sorted(seasons.items()):
            last = max(s["standings"], key=lambda r: r["rank"])
            print(f"| {y} | " + " | ".join(s["podium"]) + f" | {last['team']} ({last['wins']}-{last['losses']}) |")


if __name__ == "__main__":
    main()
