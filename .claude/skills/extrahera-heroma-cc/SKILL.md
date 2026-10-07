---
name: extrahera-heroma-cc
description: Extrahera alla arbetspass per konsult och vecka ur en Heroma-rapport (PDF, "Personlig arbetstid") och lista dem i standardformat, inför jämförelse med Recman.
---

# Extrahera pass ur Heroma-rapport

Heroma-rapporten "Personlig arbetstid" (t.ex. Region Uppsala) är en PDF med en sida (ibland två) per person. Varje person har ett veckorutnät "Tider" (V. xx, Mån–Sön med datum ÅÅMMDD), där varje pass står som en tid ("06:45-15:00") med en etikett under ("Ssk 46400"). Under rutnätet finns "Summering av arbetstid" med timmar och antal arbetstillfällen (Arb.tillf.) per vecka.

## Arbetsgång

1. Kör `python3 extract_heroma.py <rapport.pdf>` (ligger i samma mapp som den här filen, kräver `pdfplumber`). Skriptet placerar passen utifrån x-koordinater. Läs inte av sidorna med ögat, men titta gärna på en sida som bild för att förstå layouten.
2. Så placeras passen på rätt dag:
   - Vanliga pass står i sin dags kolumn.
   - **Nattpass (21:00-07:00) ritas förskjutna en halv kolumn åt höger, mitt emellan två dagar. De hör till den VÄNSTRA dagen, alltså dagen då passet börjar.** Det är bekräftat med verkliga data: ett nattpass lagt på den högra dagen skulle krocka med ett dagpass 06:45 följande morgon.
3. **"Fel v" (Felaktig vila, t.ex. 21:30-06:45) är inga pass** utan markerar för kort vila mellan två pass. Ta inte med dem som pass, men nämn dem för användaren.
4. Passtyper:
   - 06:45-15:00 → dag (7:45 h)
   - 13:30-21:30 → kväll (7:30 h)
   - 21:00-07:00 → natt (10:00 h)
   - Andra tider: fråga användaren och gissa inte.
5. **Kontrollera** att KONTROLL-raderna (antal pass och timmar per vecka) stämmer med "Summering av arbetstid" (Arb.tillf. och Arbetstid) för varje person. Om något avviker: titta på sidan som bild och fråga användaren.
6. Presentera per konsult och vecka i det här formatet:

```
**Namn**
v.41
2026, 09/10, fre, natt
2026, 11/10, sön, dag
```

7. Avsluta kort med hur filen tolkats (passtyper, nattpass på startdatum, "Fel v" exkluderat) och de frågor som återstår.

## Fråga användaren när du är osäker

- **Vilka som är användarens konsulter.** Rapporten kan innehålla egen och inhyrd personal ("Hyr …").
- **Namnmatchning mot Recman.** Vissa står bara med förnamn, och samma förnamn kan finnas hos flera personer.
- Okända tider, etiketter eller avvikelser mot summeringen.

## Jämförelse med Recman (nästa steg)

Matcha namnen (fråga om något är osäkert) och jämför pass för pass per datum. Matcha nattpass på startdatum. Lista per konsult:
- pass som bara finns i Heroma
- pass som bara finns i Recman
- pass där passtypen skiljer sig

Verifiera kolumnplaceringen mot en sidbild första gången en ny rapportlayout dyker upp.
