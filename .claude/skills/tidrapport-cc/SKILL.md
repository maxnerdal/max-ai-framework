---
name: tidrapport-cc
description: Månadens tjänstgöringsrapport för en avdelning — hämta den registrerade tiden ur Recman, skapa PDF:en med signaturrad och skicka den till avdelningen för signering. Används för kunder som inte följer upp tidrapporter via avropssystemet. Triggers on: tidrapport, tjänstgöringsrapport, skicka tidrapport för signering, arbetad tid till avdelningen, underlag för signering, NÄVA tidrapport, månadens timmar till kunden.
---

# Tidrapport för signering

Steg 9 i faktureringsflödet i `[[Operations]]`: *skicka tidrapport för signering till avd som inte följer upp tidrapporter via avropssystemet*. Avdelningen signerar arbetad tid, och fakturan hängs på den signaturen. Görs för NÄVA idag, men inget i flödet är NÄVA-specifikt — vilken kund som helst i Recman kan rapporteras.

Körs efter att registrerat arbete är granskat (steg 6), så att det som står på rapporten är det som faktureras.

## Input
Kunden och månaden. Utan månad tas förra månaden, som är den som faktureras.

## Underlaget — skriptet
I `~/Documents/curaconnect-ai-framework`:

```
uv run scripts/tidrapport.py NÄVA 2026-10     månadens rapport
uv run scripts/tidrapport.py NÄVA             förra månaden
uv run scripts/tidrapport.py --kunder         kunder med registrerad tid den månaden
```

`uv run`, inte `./scripts/...` — PDF:en skrivs med WeasyPrint ur projektets venv.

Skriptet gör exakt det som gjordes för hand på `Registrerat arbete → Artikelvy`: artikeltyp timmar, en kund, en månad. Resultatet blir en PDF i `data/tidrapporter/`, som inte checkas in — den har konsulternas namn i sig.

Kunden matchas på del av namnet, utan hänsyn till versaler eller prickar: `nava`, `NÄVA` och `närvård` når alla samma avdelning. Matchar strängen flera kunder listas de och skriptet stannar — fel avdelning på en signerad rapport är en felaktig faktura.

## Läs utskriften innan PDF:en går iväg
Skriptet skriver ut artiklarna raderna ligger på:

- **Bara `SKR - SSK - Normaltid`** (eller motsvarande normaltidsartikel) — det är vad avdelningen signerar för.
- **En jour- eller beredskapsartikel med** är också typ timmar och hamnar på rapporten utan att säga ifrån. Stäm av att det är meningen innan rapporten skickas.
- **`obs: rader med status ...`** — raderna är inte attesterade i Recman. Granska dem (steg 6) först.

OB, helg- och jourtillägg är `hourAddition` och räknas aldrig med: de ligger ovanpå samma pass som timraden och skulle lägga samma timme på rapporten två gånger. Frånvarorader likaså utanför.

## Rapporten läses live
Recman är registret, så en rad som ändras efter att en rapport signerats syns i en ny utskrift av samma månad. Det är rätt väg, men det betyder att en omkörning kan skilja sig från det som är signerat. **Spara den signerade PDF:en** — den är beviset, inte utskriften.

(Vid bygget skilde september 2026 med 0,25 h mot den signerade rapporten: en rad hade rättats i Recman efteråt.)

## Utskicket
Rapporten går till avdelningen för signering som ett **Gmail-utkast med PDF:en bifogad**. Den signerade kopian går sedan vidare till Denise på Msana som fakturabilaga.

**Skicka aldrig.** Utkastet landar på `max.nerdal@curaconnect.se` för Max att läsa och skicka själv.

1. **Kopiera PDF:en till `~/.workspace-mcp/attachments/`.** Gmail-servern läser bilagor bara därifrån; en PDF i `data/tidrapporter/` avvisas med "local file access is limited to the server's permitted directories" och utkastet blir aldrig till. Kopian raderas när utkastet är skapat — originalet ligger kvar i `data/`.
2. **Slå upp mottagaren** i tabellen nedan.
3. **Visa Max** mottagare, månad, radantal och summa, och vänta på bekräftelse.
4. **Skapa utkastet** med `mcp__workspace-mcp__draft_gmail_message`:
   - `user_google_email: "max.nerdal@curaconnect.se"`
   - `from_email: "max.nerdal@curaconnect.se"` — kontots standard-Send-As är `info@curaconnect.se`, som annars blir avsändare
   - `attachments: [{"path": "/Users/maxnerdal/.workspace-mcp/attachments/<filen>.pdf"}]` — absolut sökväg, under den mappen
   - `include_signature: true`, ingen egen signatur i brödtexten

### Mall

Ämne: `Tjänstgöringsrapport {enhet} {månad} {år}`

```
Hej {Förnamn}!

Här kommer tidrapport för {månad}.

Med vänliga hälsningar,
```

Kort. Mottagaren vet vad rapporten är och vad hen ska göra med den — timantal, avstämningsinstruktioner och påminnelser om att signera hör inte hemma i mejlet. Står det i PDF:en ska det inte upprepas här.

### Mottagare per kund

| Kund | Mottagare | Adress |
| --- | --- | --- |
| Närvårdsavdelningen i Uppsala (NÄVA) | Jeanette Lindesjö | jeanette.lindesjo@regionuppsala.se |

Står kunden inte i tabellen finns ingen mottagare bestämd. **Fråga Max vem rapporten ska till — gissa aldrig**, och fyll på tabellen med svaret. Listan växer allteftersom fler kunder får rapporten.

## Gränser
- Inga konsultnamn i exempel, commits eller anteckningar. PDF:erna stannar i `data/`.
- Rör inget i Recman. Skriptet läser bara; rättelser görs för hand i Recman och rapporten körs om.
