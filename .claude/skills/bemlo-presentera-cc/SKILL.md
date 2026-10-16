---
name: bemlo-presentera-cc
description: Presentera konsulter på ett avrop i Bemlo (app.bemlo.com) — skapa presentationsutkast, markera passen från överenskommelsen, fyll i krav, bifoga dokument och ladda upp ÖK. Körs i Chrome via Claude in Chrome. Triggers on: presentera i Bemlo, Bemlo-avrop, presentera konsult på avrop, HEM/AVD-avrop, presentation till region.
---

# Presentera konsulter i Bemlo

Följer på `overenskommelse-mejl-cc`: konsulten har fått och bekräftat en överenskommelse (ÖK), nu presenteras samma pass på avropet i Bemlo.

## Input
- Avropskod (t.ex. `HEM261008-10`) eller avropslänk. Länkens UUID skiljer sig mellan konton — sök hellre på koden under Avrop.
- Konsulter som ska presenteras.
- Schema per konsult: `schema-<namn>-<avd>-<period>.xlsx` i `~/Downloads` (läs som i `overenskommelse-mejl-cc`).
- ÖK per konsult: konsultens svar på överenskommelse-mejlet. Hämtas ur Gmail (se nedan); en färdig PDF i `~/Downloads` (`OK-<Namn>-<AVD>-<period>.pdf`) används om Max lagt den där.

## Webbläsare
Använd **Claude in Chrome** (`mcp__claude-in-chrome__*`). Appens inbyggda webbläsare fungerar inte: Bemlo laddar upp filer via File System Access API, som den blockerar (`NotAllowedError ... getFile`).

- Kontrollera med `list_connected_browsers` att Chrome är anslutet. Tom lista → be Max öppna Claude-sidopanelen i Chrome och logga in med max.nerdal@curaconnect.se.
- Kontrollera att Bemlo är inloggat med Cura-kontot (meny med Kandidater, Presentationer, Bokningar). Kontot "JK" är fel — be Max byta, logga aldrig ut själv.
- Öppna en egen flik, stäng den när du är klar.

## Före start — kandidatkoll
Kör kontrollen i `bemlo-kandidatkoll-cc` (snabbversion) på varje konsults kandidatkort innan presentationen skapas. Saknas något som går att fixa direkt (e-post, specialisering, kompetensmarkering) → fixa på kortet efter OK. Saknas något som tar tid (referenser) → säg det direkt och fråga om vi presenterar ändå. Om kollen visar brister var den gjord för sent — notera det så att påminnelsen i Google Tasks kan flyttas tidigare.

## Före start — hämta ÖK ur mejlen
Sök alltid i Gmail först, innan Max ombeds ta fram ÖK:n:
1. `search_gmail_messages` på `max.nerdal@curaconnect.se`, `include_headers`: `from:<konsultens e-post> subject:Överenskommelse` (e-post från kandidatkortet). Inget svar → `subject:Överenskommelse <förnamn>`. Flera trådar → välj den vars passlista matchar presentationen.
2. `get_gmail_thread_content` → kontrollera att svaret kommer från konsulten och bekräftar passen. Inget svar än → säg det och lämna ÖK-kravet tomt.
3. Gör PDF av tråden (Max mejl med passlistan + konsultens svar, med avsändare, mottagare och datum): skriv en enkel HTML i scratchpad och rendera med `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --no-pdf-header-footer --print-to-pdf=<scratchpad>/OK-<Namn>-<AVD>-<period>.pdf file://<html>`. Kontrollera med `pdftotext`.
4. Ladda upp på ÖK-kravet (steg 5 nedan) med titel "Överenskommelse".

## Före start — läs ÖK
Läs varje ÖK (`pdftotext -layout`). Kontrollera att passlistan i det citerade mejlet matchar schemats Excel (antal och datum). Flagga om konsultens bekräftelse är otydlig (t.ex. bara ett ord) — kravet är att datum, parter och period framgår.

## Flöde per konsult
1. **Skapa utkast:** avropet → "Presentera" → Välj kandidat → sök namn → välj → "Skapa presentation". Detta skapar bara ett utkast (URL `/presentations/<id>/edit`); inget skickas. Sidan tar 5–10 s att ladda klart.
2. **Markera pass** under "Kandidatens tillgänglighet". Rutnät per vecka, rader "Rad 1..9", celler "Vakant HH:MM – HH:MM" med en knapp. Matcha på kolumnrubrik (`mån 30/11`) + starttid (06:45 dag, 13:30 kväll, 21:00 natt). Gör det med JavaScript: läs `td` med knapp, kolumnrubrik via cellindex mot tabellens första rad, klicka knappen.
   - Finns passet på flera rader: välj lägsta lediga rad.
   - **Undvik rader som andra konsulter redan presenterats på** — Bemlo visar dem fortfarande som "Vakant". Håll en lista (dag|rad) över tidigare val i samma avrop.
   - Verifiera: antal celler som börjar med "Vald" = antal pass i ÖK. Notera schemakonflikt-varningar ("Vila mellan pass (X timmar)").
3. **Krav:**
   - Från profilen följer normalt med: e-post, telefon, personnummer, legitimerad sedan, pris, CV, HOSP, IVO (kontrollera "Hämtad"-datum ≤ 6 mån), ofta njurmedicin/Cosmic.
   - "Endast en konsult får presenteras per pass" → Ja.
   - Underleverantör → läs kandidatkortets biografi. Jobbar konsulten via eget bolag → Ja och ange bolag + org.nr i "Beskrivning av kandidaten". Annars Nej.
   - Personbevis (börkrav) → kryssa "Hoppa över".
   - HLR-S / HLR-A, Cosmic, njurmedicin → fråga Max om det inte är förifyllt.
   - Tilldelningskriterier → Kontinuitet: skriv aktivt `0` (tomt fält blockerar inskick). Fyllnadsgrad räknas automatiskt.
4. **Dokument:** "Ladda upp" på ett krav öppnar "Välj dokument" med kandidatens befintliga dokument — klicka kortets titel för att bifoga.
   - SITHS: dokumentet kan heta "SITHS-beställning" men vara själva kortet.
   - Referenser: om fler än två finns → fråga Max vilka. Flagga referenser äldre än 6 månader.
   - "Ladda upp" på ett redan ifyllt krav ersätter dokumentet — kontrollera vilken plats som är tom innan.
5. **ÖK-uppladdning:** `file_upload` får bara läsa sessionens mappar, inte `~/Downloads`. ÖK gjord ur Gmail ligger redan i scratchpad; en PDF från `~/Downloads` kopieras dit först. Sedan: ÖK-kravets "Ladda upp" → "Ladda upp dokument" → titel "Överenskommelse" → `file_upload` på filinputen ("Välj fil...") → "Ladda upp". En kvarhängande "Uppdatera dokument"-dialog stängs med Escape — klicka aldrig "Radera dokument".
6. **Spara och verifiera:** "Spara", ladda om sidan, kontrollera:
   - texten "Alla skallkrav måste uppfyllas" saknas
   - antal "Vald" = antal pass
   - Kontinuitet = 0, e-post ifylld, rätt referenser och ÖK bifogade
7. **Skicka:** bara efter uttryckligt klartecken från Max ("skicka"). Annars lämna utkastet.

## Ersättare för en bokad konsult
När en bokad konsult inte kan ta pass presenteras en ersättare på bokningen, inte på avropet.
1. Bokningar (`/candidates/external`) → sök den bokade konsulten. Varje rad är en bokning (`/candidates/contracts/<uuid>`); flera kan täcka samma vecka. Fliken **Schema** på bokningssidan visar bara den bokningens pass — öppna dem tills passen hittas.
2. "Hantera" (högerpanelen) → "Presentera ersättare" → "Välj kandidat" → "Skapa presentation". Skapar ett utkast märkt "Ersättare" (`/presentations/<id>/edit`); inget skickas.
3. Kandidatuppgifter, CV, HOSP, IVO och kandidatens övriga dokument följer med från kortet. Referens: "Ladda upp" på kravet → välj en referens (en per krav; nytt klick ersätter). Övriga referenser ligger kvar under Övriga dokument.
4. Under "Kandidatens tillgänglighet" visas hela bokningens pass som "Bokad". Klicka passen som ska ersättas → "Ersätter". Gör det med JavaScript: `td button` i sektionen, dag via `table.rows[0].cells[td.cellIndex]`.
5. Krav som i avropsflödet: ÖK som Annat dokument (skallkrav), kontinuitetsunderlag (börkrav) → Hoppa över om konsulten inte arbetat på enheten, Kontinuitet `0`.
6. Spara, ladda om, verifiera antal "Ersätter". Skicka bara efter klartecken.

## Kända egenheter
- Ja/Nej-knappar fastnar ibland inte vid första klicket, och sidan flyttar sig mellan klick. Klicka en i taget, kontrollera visuellt eller efter omladdning. Räknare: "Övriga krav x/4" — ett Nej på börkrav räknas som ej uppfyllt.
- Direktlänk till ett avrop kan fastna på laddningssnurra; gå via Avrop-listan.
- `scroll` fungerar dåligt; använd `scroll_to` med ref eller `scrollIntoView` via JavaScript.

## Avslut
Kort lista per konsult: antal pass, bifogade dokument, kravsvar, öppna flaggor (otydlig bekräftelse, gamla referenser, vilovarningar, >40 h/vecka).
