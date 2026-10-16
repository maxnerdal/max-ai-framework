"""Hämta ett kandidatkort ur Recman och ladda ner kandidatens filer.

Användning: python3 -I recman_kandidat.py <efternamn|candidateId> <utmapp>
Läser RECMAN_API_KEY ur ~/Documents/hosp-automation/config.md. Bara läsningar.
"""
import base64
import json
import pathlib
import re
import sys
import urllib.parse
import urllib.request

CONFIG = pathlib.Path.home() / "Documents/hosp-automation/config.md"
KEY = re.search(r"^RECMAN_API_KEY=(.+)$", CONFIG.read_text(), re.M).group(1).strip()
FIELDS = (
    "firstName,lastName,title,email,phoneList,mobilePhone,description,address1,postalCode,city,"
    "driversLicense,experience,education,certification,language,employee,employment,skills,"
    "reference,referenceCheck,files,attributes,hpr,updated"
)


def get(scope, **params):
    q = urllib.parse.urlencode({"key": KEY, "scope": scope, **params})
    with urllib.request.urlopen(f"https://api.recman.io/v2/get/?{q}", timeout=60) as r:
        data = json.load(r)
    if not data.get("success"):
        sys.exit(f"Recman-fel: {data.get('error')}")
    return data


def main(who, out):
    out = pathlib.Path(out)
    (out / "files").mkdir(parents=True, exist_ok=True)
    query = {"candidateId": who} if who.isdigit() else {"lastName": who}
    hits = get("candidate", page=1, fields="firstName,lastName", **query)["data"]
    if len(hits) != 1:
        sys.exit(f"{len(hits)} träffar: {[(h['candidateId'], h['firstName'], h['lastName']) for h in hits.values()]}")
    cid = next(iter(hits))
    card = get("candidate", page=1, candidateId=cid, fields=FIELDS)["data"][cid]
    (out / "kandidat.json").write_text(json.dumps(card, ensure_ascii=False, indent=1))
    for f in card.get("files") or []:
        d = get("candidateFile", candidateId=cid, fileId=f["fileId"])["data"]
        (out / "files" / d["name"]).write_bytes(base64.b64decode(d["base64"]))
        print("fil:", d["name"])
    print("kandidat:", cid, card["firstName"], card["lastName"], "->", out / "kandidat.json")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
