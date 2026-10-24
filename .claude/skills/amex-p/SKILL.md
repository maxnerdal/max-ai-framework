---
name: amex-p
description: Månadens Amex-avräkning för hushållet — läs exporten ur ~/Downloads, tagga raderna privat/gemensam med reglerna i arket, fråga bara om de osäkra, lägg in perioden i Google Sheet-databasen, räkna fram vad partnern ska betala och skriv månadsnoten i valvet. Triggers on: amex, amex-avräkning, kontoutdraget, månadens utgifter, privat eller gemensam, vad ska partnern betala, hushållsekonomi, tagga utgifter.
---

# Amex-avräkning per månad

Körs efter den 24:e, när perioden (25:e förra månaden till 24:e denna) är stängd. Perioden heter efter månaden den slutar i: 25 sep – 24 okt är `2026-10`.

Databasen är Google Sheet-arket i `config.md` (`AMEX_SHEET_ID`), konto `maxnerdal@gmail.com` via `mcp__workspace-mcp__*`. Förståelsen ligger i valvet: `Areas/Personal/Notes/Ekonomi/` med indexet `[[Ekonomi]]` och projektet `[[hushallsekonomi]]`. Läs projektets `## Arbetssätt` först.

## Arket
- **Transaktioner** — en rad per köp, alla månader: `Period | Datum | Beskrivning | Kortmedlem | Belopp | Tagg | Kategori | Företagskandidat | Källa | Referens`. Bara tillägg; `Referens` är unik.
- **Regler** — `Mönster | Kortmedlem | Tagg | Kategori | Företag | Säkerhet | Historik`. Längsta matchande mönster vinner, en regel med kortmedlem går före en utan. `säker` taggas utan fråga, `fråga` föreslås men visas för Max.
- **Avräkning** — en rad per period, formler mot Transaktioner. Max fyller `Hyra` och `Betalt`; `Justering` och `Kommentar` för engångsposter.
- **Inställningar** — kortmedlemmarna, lunchmönster och lunchbelopp, standardandel.

Delat med partnern som läsare. Ändra aldrig delning eller behörighet.

## Flöde

1. **Hämta regler och kända referenser.** `read_sheet_values` på `Regler!A2:G` och `Transaktioner!J2:J`. Spara som JSON i scratchpad: reglerna som lista av rader, referenserna som platt lista.
2. **Tagga exporten.**
   ```
   uv run --no-project --with openpyxl python ~/.claude/skills/amex-p/scripts/amex.py tag ~/Downloads --rules R.json --known K.json
   ```
   Skriptet väljer den nyaste .xlsx i katalogen som har en Amex-rubrikrad (filnamnet spelar ingen roll), sätter period, hoppar över redan kända referenser och taggar. Bekräfta filen och perioden med Max om `periods` innehåller mer än en period eller exporten är äldre än en vecka. Rader som redan finns (`duplicates`) nämns i en mening, inte mer.
3. **Fråga — en gång, i en lista.** Alla rader med `ask: true`, grupperade per kortmedlem, numrerade, med förslaget och varför:
   ```
   <kortmedlem> (12)
    1. 09-03  <handlare>     87 kr   → privat (73/99 hittills)
    2. 09-05  <handlare>  4 212 kr   → ? ny handlare, Resor
   ```
   För rader utan regel föreslår du tagg och kategori själv utifrån handlarnamnet och liknande regler. Max svarar med undantagen ("2 gemensam, resten ok"). Gissa aldrig tyst på en rad utan regel.
4. **Vässa reglerna.** Föreslå efter svaren, i en lista: nya regler för handlare som Max taggat och som troligen återkommer, uppgradering `fråga` → `säker` när historiken är entydig (minst 90 % och minst 5 rader), och nedgradering när Max gick emot en `säker` regel. Skriv till Regler först när Max sagt ja. Uppdatera `Historik` (`rätt/totalt`) på reglerna som användes.
5. **Skriv perioden.** Lägg till raderna sist i Transaktioner (`Källa` = `regel` eller `manuell`). Lägg till periodens rad i Avräkning genom att kopiera formlerna från raden ovanför och byta period. Fråga efter hyran om den inte är densamma som förra månaden.
6. **Månadsnoten.** Ladda ner periodens och de tre föregående periodernas rader ur Transaktioner som JSON (nycklarna `period, date, desc, card, amount, tag, category, foretag`) och kör
   ```
   python3 ~/.claude/skills/amex-p/scripts/amex.py report --tx T.json --period 2026-10 --settlement S.json
   ```
   `S.json` är periodens Avräkning-rad som läst ur arket. Skriv `Areas/Personal/Notes/Ekonomi/<period>.md` med samma rubrik och frontmatter som tidigare noter, rapporten och `## Iakttagelser`: två till fyra konkreta saker som skiljer perioden från snittet, med belopp. Inga råd utan siffror bakom.
7. **Indexet.** Lägg till perioden i båda tabellerna i `[[Ekonomi]]`. Skriv om iakttagelserna där bara om en trend faktiskt ändrats.
8. **Rapportera** till Max: vad partnern ska betala för perioden, saldot i Avräkning, och de rader han ändrade. Föreslå ingen överföring och skicka inget till partnern.

## Gränser
- Arket har svensk locale. Skriv med `USER_ENTERED`, belopp med decimalkomma (`236,59`) och formler med semikolon (`=ROUND(B2*C2;2)`); punkt ger text och komma i en formel blir en decimal. Datum som `2026-10-03`.
- Arket är källan för belopp. Noterna i valvet räknas om ur arket, aldrig tvärtom.
- Radera eller skriv aldrig över rader i Transaktioner. En felaktig tagg rättas i sin cell, och bara efter att Max sagt det.
- Företagskandidater taggas privat tills Max säger att bolaget har intäkter. Flaggan finns för att kunna flytta dem sedan.
- Inga belopp, handlare eller namn i det här repot — det är publikt. Reglerna och alla siffror ligger i arket och valvet.
