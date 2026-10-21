---
name: lonespec-mejl-cc
description: Mejla lönespecifikationer till Curas konsulter som Gmail-utkast, utifrån en zip med PDF:er som Max exporterat ur Recman. En PDF per konsult, bifogad i ett personligt mejl. Triggers on: lönespecifikationer, lönespec, skicka lönespecar, mejla lönebesked, zip med lönespecar, löneunderlag till konsulter.
---

# Lönespecifikationer till konsulter

Max laddar ner lönespecifikationerna ur Recman som en zip. Skillen packar upp den, matchar varje PDF mot rätt konsult, och skapar ett Gmail-utkast per person med PDF:en bifogad.

**Hämta aldrig lönedata ur Recmans API för det här.** Recmans API har ingen lönespecifikation — bara råa arbetsrader (`work`-scopet: `unitSalaryPrice`, `sumSalary`, `socialCost`). Att bygga en egen specifikation ur dem ger ett annat dokument än det Max godkänt i Recman. Zipen är källan.

**Skicka aldrig.** Allt landar som utkast på `max.nerdal@curaconnect.se` för Max att läsa och skicka själv. En lönespecifikation till fel mottagare går inte att ta tillbaka.

## Input

En zip med en PDF per konsult, exporterad ur Recman för en löneperiod (16:e föregående månad – 15:e innevarande, enligt *Lönehantering* i [[Operations]]). Lägg den i `data/` i projektet eller valfri mapp utanför git — aldrig i ett repo.

## Arbetsgång

1. **Packa upp.** `python3 packa_upp.py <zipen> <målmapp>` (ligger i samma mapp som den här filen). Skriptet packar upp i en egen tom mapp, kör `pdftotext` på varje PDF och skriver ut filnamn + de första raderna text per fil. Läs utskriften — matcha inte på filnamn ensamt, Recmans export namnger inte alltid filerna efter personen.
2. **Matcha PDF → konsult.** Namnet står i PDF-texten. En PDF hör till exakt en person.
3. **Hämta mejladress.** Recman är masterregister: kandidatkortets mejl gäller. Finns ingen tillgång till Recman i sessionen, sök i skickade mejl (`search_gmail_messages`, `in:sent` + namnet, `include_headers: true`). Hittas ingen adress → fråga, gissa aldrig.
4. **Kör kontrollerna nedan.**
5. **Visa tabellen** (konsult × filnamn × mottagaradress) och vänta på Max bekräftelse.
6. **Skapa utkasten**, ett per konsult, med `mcp__workspace-mcp__draft_gmail_message`:
   - `user_google_email: "max.nerdal@curaconnect.se"`
   - `from_email: "max.nerdal@curaconnect.se"` — kontots standard-Send-As är `info@curaconnect.se`, som annars blir avsändare
   - `attachments: [{"path": "<absolut sökväg till PDF:en>"}]`
   - `include_signature: true`, ingen egen signatur i brödtexten

## Mall

Ämne: `Lönespecifikation {månad}`

```
Hej {Förnamn}!

Bifogat hittar du din detaljerade lönespecifikation för {löneperiod} från vårt affärssystem, Recman.
Lönen betalas ut {utbetalningsdatum}.

Om du vill se en mindre specificerad lönespecifikation tillsammans med hur mkt skatt vi drar så kan du logga in i vårt lönesystem, Fortnox med ditt BankID: https://apps.fortnox.se/identity

Tack för att du jobbar hos oss på Cura Connect!
```

- `{löneperiod}` och `{utbetalningsdatum}` räknas fram per körning — se [Löneperiod och utbetalning](#löneperiod-och-utbetalning). Skriv dem som `16 september–15 oktober 2026` och `den 25 oktober`.
- `{månad}` är utbetalningsmånaden med litet begynnelsebokstav, inte löneperiodens startmånad: perioden 16/9–15/10 betalas ut i oktober och ger ämnet `Lönespecifikation oktober`.
- `{Förnamn}` är konsultens förnamn. Max mall skriver det som Recmans sammanfogningsfält `@candidate.firstName` — här sätts det riktiga förnamnet in, utkastet ska inte innehålla fältnamnet.
- Texten slutar på `Tack för att du jobbar hos oss på Cura Connect!`. Lägg inte till `Hälsningar,` eller någon egen signatur — Gmail-signaturen läggs på automatiskt (`include_signature: true`).
- Fortnox-länken är en del av mallen och ska vara klickbar men oförändrad.

## Löneperiod och utbetalning

Löneperioden är **16:e föregående månad till 15:e innevarande månad**, och lönen betalas ut **den 25:e**
i den månad perioden slutar. Processen kan börja den 16:e, när perioden just stängt (*Lönehantering* i
[[Operations]]).

**Hämta perioden ur PDF:erna, inte ur dagens datum.** Specifikationen skriver själv vilken period den
gäller, och det är den som ska stå i mejlet. Dagens datum används bara som rimlighetskontroll: ligger
perioden i PDF:erna inte närmast före dagens datum är det antingen en gammal zip eller en körning i
efterhand — fråga Max.

Räkna fram och kontrollera med ett skript, skriv inte datum för hand:

```python
import datetime as dt

MONTHS = ["januari","februari","mars","april","maj","juni",
          "juli","augusti","september","oktober","november","december"]

def period(end_year: int, end_month: int) -> tuple[str, str]:
    """Perioden som slutar den 15:e i end_month, och utbetalningsdagen."""
    slut = dt.date(end_year, end_month, 15)
    start = dt.date(end_year if end_month > 1 else end_year - 1, end_month - 1 or 12, 16)
    ar = "" if start.year == slut.year else f" {start.year}"
    return (
        f"{start.day} {MONTHS[start.month - 1]}{ar}–{slut.day} {MONTHS[slut.month - 1]} {slut.year}",
        f"den {slut.day + 10} {MONTHS[slut.month - 1]}",
    )
```

- **Årtal.** Perioden spänner över nyår i januarikörningen: `16 december 2026–15 januari 2027`. Står båda
  datumen samma år skrivs årtalet bara en gång.
- **Den 25:e är inte alltid en bankdag.** Faller den på helg eller svensk helgdag betalas lönen normalt ut
  närmast föregående bankdag — men det är Curas och Fortnox praxis som avgör, inte den här filen. Räkna
  fram den 25:e, kontrollera veckodag och helgdag, och **fråga Max om det riktiga datumet** innan utkasten
  skapas. Skriv aldrig ett datum i mejlet som inte är en bankdag.
  Nära i tiden: 25 oktober 2026 är en söndag, och 25 december 2026 är juldagen.

## Kontroller före utkast

Det här är skillens egentliga arbete. En felparad bilaga läcker en kollegas lön.

1. **Antal.** Antal PDF:er = antal konsulter som ska ha mejl. Oparade PDF:er och konsulter utan PDF listas för Max — fortsätt inte förbi dem utan besked.
2. **En per person.** Två PDF:er som matchar samma namn, eller en PDF där två namn förekommer, stoppar körningen. Fråga.
3. **Namn mot adress.** Läs namnet i PDF:en mot namnet som äger mejladressen. Snarlika namn i registret (samma förnamn, dubbelnamn) → fråga.
4. **Period.** Alla PDF:er ska gälla samma löneperiod, och den perioden ska vara den som står i mejlet. En avvikare är troligen en gammal fil som följt med i zipen.
5. **Efter utkasten:** öppna ett par utkast och kontrollera att bilagan är rätt persons fil.

## Personuppgifter

Lönebelopp och personnummer stannar i PDF:erna. Skriv aldrig ut belopp per person i chatten, i repot eller i valvet — tabellen i avslutet innehåller namn, filnamn och mejladress, inget mer. Zipen och de uppackade filerna ligger utanför git och städas när utkasten är skapade.

## Fråga användaren när

- En PDF inte går att matcha mot en konsult, eller matchar flera.
- En konsult saknar mejladress i Recman.
- Zipen innehåller fler eller färre PDF:er än väntat.
- Löneperioden i någon PDF skiljer sig från de övriga.

## Avslut

Kort tabell: konsult × filnamn × mottagaradress × utkast skapat. Nämn vad som inte gick att matcha och vad Max behöver kontrollera innan utskick.
