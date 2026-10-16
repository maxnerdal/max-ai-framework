---
name: bemlo-ny-kandidat-cc
description: Lägg upp en ny konsult som kandidat i Bemlo (app.bemlo.com) utifrån kandidatkortet i Recman — personuppgifter, biografi, körkort, legitimationsår samt Recman-genererat CV, IVO, HOSP och referenser. Recman läses via API, Bemlo fylls i via Claude in Chrome. Första steget före bemlo-kandidatkoll-cc och bemlo-presentera-cc. Triggers on: lägg upp kandidat i Bemlo, ny konsult i Bemlo, lägg in kandidat, för över konsult från Recman till Bemlo.
---

# Ny kandidat i Bemlo från Recman

Recman är master för kandidatdata ([[Recman]] i `obsidian-vault/Areas/Cura Connect/_context/Recman.md`). Max lägger in konsulten i Recman först: CV-inläsning, IVO/HOSP som certifieringar med filer, personuppgifter. Den här skillen för över det till Bemlo. Följs av `bemlo-kandidatkoll-cc` och, vid avrop, `bemlo-presentera-cc`.

## Input
- Konsultens namn (efternamn räcker) eller Recman candidateId.

## 1. Hämta från Recman (API, bara läsningar)
```bash
python3 -I ~/.claude/skills/bemlo-ny-kandidat-cc/scripts/recman_kandidat.py <efternamn|candidateId> <scratchpad>/recman-<namn>
```
Ger `kandidat.json` och alla kandidatens filer i `files/`. Nyckeln läses ur `~/Documents/hosp-automation/config.md` och skrivs aldrig ut. Fältlistan och övriga endpoints: Recmans Postman-samling (`developers.recman.io`, rå JSON via `documenter.gw.postman.com/api/collections/20051968/UVsMt5Co`). En äldre hjälpartikel nämner 200 anrop per dygn — gissa inte fältnamn i loop.

Kontrollera innan Bemlo:
- Namn i HOSP-utdraget mot Recman/CV (stavning, mellannamn). Bemlo-kortet får samma namn som i Recman.
- Telefonnummer: Recmans `mobilePhone` kan vara felformaterat (`+460…`). Använd `phoneList` eller CV:t, skriv `+46XXXXXXXXX`.
- Legitimerad sedan: står i HOSP-utdraget ("Sjuksköterska sedan ÅÅÅÅ-MM-DD").
- Hämtad-datum för IVO/HOSP: datumet i utdragets rubrik (eller filnamnet `IVO-<Namn>-ÅÅÅÅMMDD.pdf`).
- Underleverantör: `employment[].subcontractorCompanyId` ≠ 0 → konsulten jobbar via eget bolag; ange bolag + org.nr i biografin.

## 2. Bemlo — webbläsare
Claude in Chrome, Cura-kontot (se `bemlo-presentera-cc` för anslutningskoll). Egen flik, stäng när klart.

## 3. Skapa kandidaten
1. `/candidates/managed` → sök efternamn och förnamn var för sig. Finns kandidaten redan → hoppa till steg 4 och uppdatera i stället.
2. "Lägg in kandidat" → dialog med Namn, Yrke, Specialiseringar → "Skapa". Kortet öppnas direkt (`/candidates/<uuid>`).
   - Yrke: skriv "Sjuksköterska" i comboboxen och välj.
   - Specialiseringar blir obligatoriskt när yrket valts. Allmänsjuksköterska → "Leg. Sjuksköterska". Specialistsjuksköterska → specialistområdet. (Specialiseringsfältet i Redigera-formuläret är ett annat fält och lämnas tomt för allmänsjuksköterska, se `bemlo-kandidatkoll-cc`.)

## 4. Fyll i kortet ("Redigera")
| Bemlo-fält | Källa |
|---|---|
| Om kandidaten | Recman `description` (+ underleverantörsrad vid behov) |
| Hemkommun | Recman `city` → kommun (Spånga → Stockholm) |
| Antal års erfarenhet | År sedan legitimation |
| Journalsystem | Finns inte i Recman — lämna tomt, fråga Max om det behövs |
| Körkort | B → "Körkort för manuellt växlad bil"; bara B (auto) → automat |
| E-post, Telefonnummer | Recman |
| Typ av identifikation | "Personnummer", sedan fältet `ÅÅÅÅMMDD-XXXX` |
| Legitimerad sedan | Årsväljare — år ur HOSP |
| HSA-ID | Lämna tomt om okänt |

- **Skriv långa texter med `form_input`, inte `type`** — `type` tappar tecken i biografin. Efter `form_input`: skriv ett mellanslag + Backspace i fältet så att React registrerar ändringen, annars sparas inte värdet.
- "Spara" i bannern överst. Ladda om sidan och läs av kortet med `get_page_text`.

## 5. Dokument
"Ladda upp..." på en dokumentplats öppnar "Ladda upp dokument": Dokumenttyp, Titel/Hämtad, filinput. Dialogen står kvar öppen efter uppladdning — byt dokumenttyp och fortsätt; stäng med krysset.
- `file_upload` kan bara läsa sessionens mappar → filerna ligger redan i scratchpad från steg 1.
- **CV**: alltid det CV som Recman genererar från profilen — aldrig originalfilen under Filer (det är bara parser-underlaget; Max redigerar och lägger till anställningar i profilen efter inläsning). API:t kan inte generera CV, så:
  1. Kontrollera datumen i `kandidat.json` först. Parsern sparar månadsdatum med dag `00` (`2023-08-00`), som Recman renderar som föregående månad ("Juli 2023"). Rätta till dag `01` via API: `operation: update`, `data: {candidateId, experience|education: {"id": <experienceId|educationId>, startDate, endDate}}` — nyckeln är `id`, inte `experienceId` (då misslyckas anropet tyst). Ett objekt per anrop; bara skickade fält ändras. Läs tillbaka och jämför. `0000-00-00` lämnas orört.
  2. Recman i Chrome: `app.recman.io/user/candidate.php?candidate_id=<id>` → "Ladda ner CV" → standardval: pdf, Svenska, Huvudlogotyp, Profil (bild, generell info, kontaktinfo), Arbetslivserfarenhet, Utbildning; "Spara till profil" urkryssad → "Ladda ner". Filen hamnar i `~/Downloads/<Förnamn>_<Efternamn>.pdf`; kopiera till scratchpad som `CV-<Förnamn>-<Efternamn>.pdf` och kontrollera perioderna med `pdftotext`.
  3. Bemlo: typ CV, titel "CV". Byte av befintligt CV: pennan på kortet → "Välj ersättningsfil" → "Uppdatera" (aldrig "Radera dokument"). Verifiera genom att klicka kortet (förhandsvisning).
- **IVO / HOSP**: typen byter titelfältet mot **Hämtad** (datumväljare, obligatorisk). Välj utdragets datum.
- **Referens**: titel "Referens <Namn>, <Verksamhet>". Källa:
  - Referensformulär (mall "Referenstagning") skickas till referenspersonerna från Recman. Svaren syns under referenspersonen i Recman, men PDF:en skapas på klick via Recmans interna `generate_pdf.php` och **finns inte i API:t** (kontrollerat 2026-10-15: inga fält/scope för formulär). Max laddar ner PDF:erna och lägger dem under Filer på kandidaten → de kommer då med i skriptets nedladdning (`Referenstagning-<Namn>.pdf`).
  - Äldre referenser kan ligga som `referenceCheck` (anteckningar i HTML, ibland fil).
  - Läs PDF:en och jämför perioden med CV:t; flagga avvikelser. Referenskontakter utan svar laddas inte upp.
- **Legitimation**: HOSP-utdraget är beviset; examensbevis är inte legitimation — ladda inte upp det här.
- Övriga dokumenttyper: Annat dokument, Anställningsavtal, Specialisering.

## 6. Avslut
Kör `bemlo-kandidatkoll-cc` på det nya kortet om en enhet är känd. Rapportera kort: vad som lagts in, vad som saknas (referenskontroller, SITHS, HLR, journalsystem) och avvikelser att rätta i Recman (namnstavning, telefonformat).

## Mot automatisering
Bemlos webbapp talar GraphQL mot `api.bemlo.ai/graphql` (skapa kandidat, spara kort, ladda upp dokument). Det är odokumenterat och kan bryta mot användarvillkoren — använd inte utan att Max fattat beslut. Bemlos officiella API är borträknat på kostnad, se beslutsloggen i `curaconnect-ai-framework.md`.
