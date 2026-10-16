---
name: overenskommelse-mejl-cc
description: Skapa "Överenskommelse"-mejl (Gmail-utkast) till konsulter utifrån schemaförslag (Excel eller PDF per konsult, t.ex. schema-<namn>-<avd>-<period>.xlsx) eller inklistrat skiftschema. Passen listas per vecka med dag/kväll/natt. Triggers on: överenskommelse, skicka överenskommelser, bokningsmejl till konsulter, presentera konsult för behov, schema-PDF till mejl.
---

# Överenskommelse-mejl till konsulter

Ett mejl per konsult som bekräftar vilka pass vi presenterar personen för. Skapas alltid som Gmail-utkast på `max.nerdal@curaconnect.se` via `mcp__workspace-mcp__draft_gmail_message`. Skicka aldrig direkt.

Avsändare: sätt alltid `from_email: "max.nerdal@curaconnect.se"`. Kontots standard-Send-As är `info@curaconnect.se`, som annars blir avsändare.

## Mall

Ämne: `Överenskommelse`

```
Hej {Förnamn}!

Enligt överenskommelse kommer vi att presentera dig för följande behov:

{Avdelning}, {Ort}

{passlista}

Återkoppla med bekräftelse på att du kommer att acceptera bokningen om vi blir tilldelade passen ovan.

Hälsningar,
```

Avsluta på `Hälsningar,` — Gmail-signaturen läggs på automatiskt (`include_signature` = true). Skriv ingen egen signatur.

## Passlista

Grupperad per ISO-vecka, tom rad mellan veckor. Veckor utan pass utelämnas.

```
v.49
2026, 30/11, mån, natt
2026, 03/12, tor, natt

v.50
2026, 07/12, mån, natt
```

- Rad: `ÅÅÅÅ, DD/MM, veckodag, typ` — nollutfyllt datum, veckodag `mån tis ons tor fre lör sön`.
- Typ från starttid: 06:45 → `dag`, 13:30 → `kväll`, 21:00 → `natt`. Annan starttid → fråga.
- År räknas fram per datum (perioder spänner ofta över nyår). Veckonummer = ISO (v.53 finns 2026).
- Rubrik: avdelning först, ort förkortad som i schemat, t.ex. `Hematologi och njuravdelning, Ö-vik`.

## Input

Prioritet: Excel → PDF → inklistrat. Finns både `.xlsx` och `.pdf` med samma filnamn, läs Excel.

### Schema-Excel (primär källa)
`schema-<namn>-<avd>-<period>.xlsx`, två flikar:
- **sheet1** — en rad per pass: `Datum | Veckodag | Vecka | Start | Slut | Rast (min) | Timmar | Passtyp | Regelbrott`. Datum är Excel-serienummer (`1899-12-30 + n dagar`), Start/Slut är dygnsandel (0.875 = 21:00). Passtyp är redan `dag`/`kväll`/`natt` — använd den direkt. Sista raden `Totalt` ignoreras.
- **sheet2** — summering: Konsult, Avrop, Period, Pass, Timmar, antal per passtyp, timmar per månad. Används för verifiering och regelbrott-sammanfattning.

openpyxl är inte installerat. Läs med `zipfile` + regex (strängar är inline `<is><t>`, ingen sharedStrings.xml):

```python
import zipfile,re,datetime as dt
x=zipfile.ZipFile(f).read('xl/worksheets/sheet1.xml').decode()
for r,body in re.findall(r'<row r="(\d+)"[^>]*>(.*?)</row>',x,re.S):
    a=re.search(r'<c r="A\d+"[^>]*><v>(\d+)</v>',body)
    h=re.search(r'<c r="H\d+".*?<t[^>]*>(.*?)</t>',body,re.S)
    if a and h: date=dt.date(1899,12,30)+dt.timedelta(int(a.group(1))); typ=h.group(1)
```

### Schema-PDF (fallback när Excel saknas)
Header: `{Namn}  {antal} pass  {timmar}`, rad 2 `{Ort} - {Avdelning} · {kod} · {period}`, summering `dag X kväll Y natt Z`, sedan veckorutnät MÅN–SÖN med datum och klockslag under.

`pdftotext -layout` förskjuter kolumnerna — placera **aldrig** pass utifrån layout-text. Använd koordinater:

```bash
pdftotext -bbox schema.pdf - | grep -E '>[0-9]{1,2}/[0-9]{1,2}<|>[0-9]{2}:[0-9]{2}–'
```

Koppla varje klockslag till det datum som ligger närmast ovanför (närmaste datumrad med y < klockslagets y) med minst x-avstånd. Ignorera klockslag i "Regelbrott"-sektionen (de saknar "–sluttid" eller ligger långt under rutnätet).

### Inklistrat schema
Rader med datum, starttid, sluttid, konsultnamn. Gruppera per konsult; se upp med förkortade/dubbla namn.

## Mejladresser
Sök i skickade mejl: `in:sent subject:Överenskommelse` eller konsultens namn (`search_gmail_messages` med `include_headers`). Hittas ingen adress → fråga. Kända:
- Johan Sjödin — sjodda1997@gmail.com
- Oratile Johansson — oratilelexi@gmail.com
- Said Muhena — said_muhena@hotmail.com
- Basireh Heidari — basireh.heidari22@gmail.com

## Verifiering (före utkast)
1. Antal pass per konsult och fördelning dag/kväll/natt ska matcha summeringen (Excel sheet2 eller PDF-header).
2. Stickprov: timmar per vecka (TIM-kolumnen) mot passlängder.
3. Generera listan med ett skript (Python `datetime` för veckodag/ISO-vecka), skriv inte för hand.

## Avslut
Kort tabell: konsult × dag/kväll/natt/totalt + mottagaradress. Nämn regelbrott som schemat flaggar (Excel-kolumnen Regelbrott eller PDF-sektionen) (dygnsvila, >40 h/vecka) — de följer inte med i mejlet men Max bör känna till dem innan utskick.
