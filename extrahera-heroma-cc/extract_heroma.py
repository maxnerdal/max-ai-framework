import pdfplumber, re, datetime, math
from collections import defaultdict
import sys
PDF = sys.argv[1]  # sökväg till HeromaRapport.pdf
TYP = {"06:45-15:00": ("dag", 7.75), "13:30-21:30": ("kväll", 7.5), "21:00-07:00": ("natt", 10.0)}
WD = ["mån","tis","ons","tor","fre","lör","sön"]
pass_ = defaultdict(list); okanda = []; felv = []
with pdfplumber.open(PDF) as pdf:
    for p in pdf.pages:
        txt = p.extract_text() or ""
        if "Tider" not in txt: continue
        namn = txt.split("\n")[1].strip()
        words = p.extract_words()
        heads = [w for w in words if re.fullmatch(r"\d{6}", w["text"])]
        rows = defaultdict(list)
        for w in heads: rows[round(w["top"])].append(w)
        hrows = sorted(rows.items())
        for i, (top, hs) in enumerate(hrows):
            hs = sorted(hs, key=lambda w: w["x0"])
            dates = [datetime.datetime.strptime(h["text"], "%y%m%d").date() for h in hs]
            colw = (hs[-1]["x0"] - hs[0]["x0"]) / 6
            nxt = hrows[i+1][0] if i+1 < len(hrows) else top + 60
            cell = [w for w in words if top+5 < w["top"] < min(nxt-5, top+60)]
            labels = [w for w in cell if not re.fullmatch(r"[\d:-]+", w["text"])]
            for t in [w for w in cell if re.fullmatch(r"\d\d:\d\d-\d\d:\d\d", w["text"])]:
                lab = min(labels, key=lambda l: (abs(l["top"]-t["top"]-20) > 8, abs(l["x0"]-t["x0"])))
                mon_x = hs[0]["x0"] - (hs[1]["x0"] - hs[0]["x0"]) * 0.5 - 2
                idx = math.floor((t["x0"] - mon_x + 5) / colw)
                idx = max(0, min(6, idx))
                d = dates[idx]
                if lab["text"] == "Fel": felv.append((namn, d, t["text"])); continue
                if t["text"] not in TYP: okanda.append((namn, d, t["text"], lab["text"])); continue
                pass_[namn].append((d, t["text"]))
for namn, lst in pass_.items():
    lst.sort(); print(f"**{namn}**"); cur=None
    kontroll = defaultdict(lambda: [0, 0.0])
    for d, tid in lst:
        v=d.isocalendar()[1]
        if v!=cur: print(f"v.{v}"); cur=v
        print(f"{d.year}, {d:%d/%m}, {WD[d.weekday()]}, {TYP[tid][0]}")
        kontroll[v][0] += 1; kontroll[v][1] += TYP[tid][1]
    print("KONTROLL (antal, timmar) per vecka:", dict(kontroll), "\n")
print("Fel v (ej pass):", felv)
print("Okända tider – fråga användaren:", okanda)
