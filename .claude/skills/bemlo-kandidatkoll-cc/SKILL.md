---
name: bemlo-kandidatkoll-cc
description: Förberedande kontroll av konsulters kandidatkort i Bemlo inför kommande avrop — kontaktuppgifter, specialisering, HOSP/IVO, CV, SITHS, referenser och kompetenser mot enhetens kravprofil, med giltighet räknad fram till förväntad svarsdag. Körs veckor innan avropet publiceras, så att referenser hinner tas. Triggers on: kandidatkoll, förbered presentation, kolla kandidatkort, inför avrop, är konsulten redo att presenteras.
---

# Kandidatkoll inför avrop

Avrop ska helst besvaras inom ~2 timmar efter publicering. Det som tar tid (referenssvar, nya HOSP/IVO-utdrag, SITHS) måste därför vara klart **innan** avropet kommer ut. Den här skillen kontrollerar kandidatkortet mot enhetens kravprofil och listar åtgärder.

Kravprofiler och publiceringsmönster per enhet: [[Avrop-kravprofiler]] i `obsidian-vault/Areas/Cura Connect/Notes/Avrop-kravprofiler.md`. Läs den först.

## När
- Ca 2–3 veckor före förväntad publicering, dvs. ca 2,5–3 månader före behovsstart (se publiceringsmönster i noten). Påminnelser ligger i Google Tasks, Cura Connect — Backlog.
- Som första steg i `bemlo-presentera-cc` (snabbversion: bara kontroll, inga referensutskick).

## Input
- Konsulter (namn).
- Enhet(er) de är tänkta för → kravprofil.
- Förväntad sista svarsdag och uppdragsstart. Okänt → uppskatta från publiceringsmönstret.

## Webbläsare
Claude in Chrome, Bemlo inloggat med Cura-kontot (inte "JK"). Se `bemlo-presentera-cc` för anslutningskoll. Kandidatkort: Bemanning → Kandidater → sök namn.

## Kandidatkortet i Bemlo
- Lista: `/candidates/managed` — kolumner HOSP, IVO, CV (datum) ger snabb överblick. Kort: `/candidates/<id>`.
- Överblick visar biografi, journalsystem, körkort, dokument (namn + uppladdad/hämtad-datum) och kontaktinformation.
- "Redigera" öppnar formulär: Om kandidaten, Yrke, Specialisering, Antal års erfarenhet, Journalsystem (flerval), Körkort, E-post, Telefon, Personnummer, Legitimerad sedan. Spara/Avbryt i bannern överst.
- **Specialisering** på kortet är specialistområde (Akutsjukvård, Intensivvård, Medicinsk vård …), inte "Leg. Sjuksköterska". Lämna tomt för allmänsjuksköterska — "Leg. Sjuksköterska" sätts i presentationens prisgrupp.
- **HLR** har inget fält på kortet — verifieras via uppladdat intyg (dokumentnamn + datum) och besvaras per presentation.
- **Underleverantör** framgår av biografin (t.ex. "jobbar som Underleverantör X AB, org.nr …"). Läs alltid biografin — styr svaret på underleverantörskravet.

## Kontroll per konsult
Giltighet räknas mot **förväntad sista svarsdag**, inte dagens datum.

| Punkt | OK när |
|---|---|
| E-post, telefon, personnummer | Ifyllda på kortet |
| Specialisering | Specialistområde satt om konsulten är specialistsjuksköterska; legitimerad sedan + antal års erfarenhet ifyllda |
| Underleverantör | Biografin anger om konsulten jobbar via eget bolag |
| CV | Finns |
| HOSP | Finns, hämtad ≤ 6 mån före svarsdag |
| IVO | Finns, hämtad ≤ 6 mån före svarsdag |
| SITHS | Kopia av ordinarie kort finns, tydligt namngiven ("SITHS-kort") |
| Referenser | ≥ 2 från de två senaste avslutade uppdragen, ≤ 6 mån vid svarsdag |
| HLR-S / HLR-A | Markerat, och utbildning ≤ 12 mån före uppdragsstart (avtalskrav) |
| Övriga kompetenser | Enligt kravprofil (t.ex. Cosmic, njurmedicin) markerade |
| Karens | Ej anställd i regionen senaste 12 mån (avtalskrav) — fråga vid tveksamhet |

## Åtgärder
- **Kan hämtas själv** (t.ex. e-post ur Gmail via `search_gmail_messages` på `max.nerdal@curaconnect.se`): visa vad som ska ändras på kandidatkortet, ändra efter OK.
- **Kräver Max/konsulten**: samla i en lista — nya referenser (skicka referensformulär), HLR-intyg, SITHS-kopia, kompetenser som inte går att verifiera.
- Döp om otydliga dokument (t.ex. "SITHS-beställning" som egentligen är kortet) efter OK.
- Första körningen per kandidatkort är också kartläggning: notera var fälten ligger i Bemlo och skärp denna skill.

## Avslut
Tabell per konsult: punkt × OK / åtgärdat / saknas, plus en kort åtgärdslista för Max med deadline (= förväntad publicering). Lägg saknade punkter som uppgifter i Cura Connect — Backlog om Max vill.
