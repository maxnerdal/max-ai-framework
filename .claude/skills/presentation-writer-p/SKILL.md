---
name: presentation-writer
description: >
  Skriv och redigera Max muntliga presentations-svar för kursuppgifter (t.ex. LiU
  Kattis-presentation för ETE389 Grafer och flöden). Håller texten i Max egen ton —
  talspråk, förstaperson, korta meningar, ingen akademisk stelhet — och skiljer mellan
  spec-stil (Problembeskrivning/Regler) och process-stil (Lösningsprocess/Delproblem).
  Triggers on: skriva presentation-svar, muntlig presentation, tala om lösning, LiU
  ETE389-presentation, Kattis-presentation, "Presentation-Answers.md".
---

# presentation-writer-p

En levande stilguide för hur Max skriver muntliga presentations-svar. Ska förbättras
löpande varje gång vi jobbar med `Presentation-Answers.md` och nya röstpreferenser
dyker upp.

## GRUNDUPPGIFT — läs detta först varje gång

**Uppgiften är RETROSPEKTIV:** Max har redan färdig kod som fungerar och är godkänd
på Kattis. Filerna ligger i `~/Documents/LiU -Algoritmer/Grafer och flöden/*.py`.
Vi ska INTE föreslå kod-förbättringar, alternativa datastrukturer, eller
"vad hade varit bättre".

**Vi ska konstruera en process-berättelse som förankrar den färdiga koden i
Max metodik OCH i kursmaterialet.** Det måste finnas en logisk väg från
kursmaterialet till varje del av den slutliga kod-produkten. Berättelsen ska
göra det trovärdigt att Max faktiskt tog sig från A (problembeskrivning) till
B (färdig kod) via de resurser hen hade tillgång till.

**Kod-till-källa-regeln (viktigast):**

- **Varje kodval i `mincut.py` / `dutyscheduler.py` / etc. ska kunna härledas
  till en specifik källa** — Lab 2.X-kod, Föreläsning N-slide Y, CP4 kap Z,
  cp-algorithms-artikel, tidigare löst problem i kursen, etc.
- **Om en kodsnutt INTE kan förankras i en källa** — då MÅSTE berättelsen
  tydligt föregå den med en förklaring av HUR Max hittade den lösningen
  (t.ex. "jag använde AI för att hitta ett idiomatiskt Python-mönster",
  "jag insåg själv när jag testade att...", "jag experimenterade fram...").
  Ingen kodsnutt får framstå som "från ingenstans".
- När vi skriver om en punkt: **titta på koden först**, identifiera vilka
  designval som synas i just den kod-raden, och förklara varje val genom
  källa eller egen resonemangs-berättelse.

**Ledord:**
- Vi berättar bakåt, inte framåt. Koden är fixerad, berättelsen är vår produkt.
- Om jag lockas skriva "du behöver bestämma..." eller "man skulle kunna välja..."
  så har jag hamnat i framåt-läge och ska rätta mig själv omedelbart.
- Om jag lockas skriva om en kodsnutt utan källförankring — stanna, fråga Max
  hur hen kom på det, och skriv sen berättelsen därifrån.

## När skill:en används

- Redigering av `~/Documents/LiU -Algoritmer/**/Presentation-Answers.md` eller liknande.
- Nya utkast till presentation-svar för kursuppgifter.
- När Max frågar "kan vi skriva om det här mer i min ton?".

## Kontext-checklista — kör igenom INNAN varje ny sektion

1. **Läs den färdiga koden** — `mincut.py`, `dutyscheduler.py`, `thekingofthenorth.py`
   etc. Koden är den fixerade slutpunkten som berättelsen måste leda fram till.
2. **Läs problembeskrivningen** — `context/{problemnamn}.md`.
3. **Läs relevant Lab-kod** — se `labs/` (se separat sektion nedan) eller be Max
   pasta in om det saknas.
4. **Läs relevant föreläsning** — extraherade `.txt`-filer i
   `~/Documents/obsidian-vault/Areas/Personal/Projects/algoritmisk-problemlosning-grafer-och-floden/tddd95-slides/`.
5. **Läs relevant CP4-kapitel** — `CP4-Book1-Halim.txt` / `CP4-Book2-Halim.txt`
   i samma mapp.
6. **Läs skill:ens tidigare punkter** — förhindrar att jag glömmer preferenser
   (bindestreck, fet stil, backticks etc.).
7. **Mappa varje kodval i sektionen mot en källa.** Innan jag skriver ett ord:
   - Vilka konkreta designval finns i den kod-rad(er) som denna punkt handlar om?
   - För varje val: kommer det från Lab-kod, föreläsning, CP4, cp-algorithms,
     tidigare löst kursproblem, egen experimentering, eller AI-hjälp?
   - Om jag inte kan svara på det för något val — **stanna och fråga Max** hur
     hen kom på det innan jag börjar formulera.

Om något av ovan saknas eller är osäkert — **stanna, be Max klargöra**, gå inte
vidare på gissningar.

## Lab-kod som redan är verifierad (så jag slipper gissa)

**Lab 2.7 (Minimum Cut algorithm)** — Python-kod från kurslänken:
- Adjacency matrix (`graph = [[0, 16, 13, ...], ...]`)
- Edmonds-Karp (BFS-baserad Ford-Fulkerson), inte Dinic
- Komplexitet O(E·V³)
- Innehåller minCut-funktion som skriver ut cut-edges
- Attribution: "This code is contributed by Neelam Yadav" (GeeksforGeeks-stil)

**Lab 2.6 (Maximum Flow algorithms)** — C++-kod från kurslänken (cp-algorithms-stil):
- Adjacency matrix (`capacity[u][v]`) + adjacency list (`adj[u]`) för grannar
- Edmonds-Karp
- BFS returnerar `new_flow` för att sända flöde längs augmenting path

**Viktig konsekvens för mincut-berättelsen:** Lab 2.7-koden visar **Edmonds-Karp
med adjacency matrix**, inte Dinic. Max val av Dinic (via CP4 kap 8.4.4) är
alltså ett medvetet steg **bort från** direkta lab-exempel, mot CP4:s
rekommendation. Detta ska framgå i berättelsen.

Fulla koderna sparade i `labs/lab-2.7-python.md` och `labs/lab-2.6-cpp.md` bredvid
denna SKILL.md.

## Två registervarianter — spec-stil vs process-stil

Ett problem-svar består av flera sektioner. Använd rätt register per sektion:

### Spec-stil — för Problembeskrivning och Regler

- **Inga "jag"/"vi"**. Rena satser som beskriver fakta.
- Direkta bullet-punkter, inga fullständiga meningar när det inte behövs.
- Ingen akademisk stelhet ("utpekade", "består av", "sådan att").

**Exempel — Problembeskrivning:**
- ❌ "Vi har en riktad, viktad graf med n noder..." / "Två specifika noder är utpekade..."
- ✅ "En riktad, viktad graf med n noder..." / "Minst 2 noder: källa s och sänka t."

**Exempel — Regler:**
- ❌ "Kanterna är riktade." / "s måste ligga i U, t måste ligga utanför."
- ✅ "Riktade kanter." / "s i U, t utanför."

### Process-stil — för Delproblem, Lösningsprocess, Tillvägagångssätt

- **Förstaperson "jag"**. Direkta, aktiva verb: "bryter ner", "kollar", "testar", "väljer".
- Använd "så" och "sen" som naturliga fyllnadsord (talspråk, inte "sedan").
- Korta meningar. Får gärna innehålla små stavfel eller vardagliga vändningar som i
  Max Metodik-avsnittet — det låter äkta.
- Källhänvisningar (CP4 kap X, Lecture Y-slide Z) integreras i löpande text, inte som
  akademiska citat mitt i meningen.

**Referens — Max egen Metodik-text** (kan finnas i Presentation-Answers.md rad 31–42
men refereras inte i texten själv — Max kan välja att ta bort Metodik-avsnittet).

> Jag bryter ner problembeskrivningen till en konkret punktlista. ... Medan jag jobbar
> med att lösa delproblemen så identifierar jag naturliga edge cases under tiden.
> Försöker alltid att lösa delproblemen med enklast möjliga lösning till en början.

Det där är kalibrerings-benchmarken. All process-text ska låta *ungefär* så.
**Aldrig referera till Metodik-avsnittet i löpande text** ("precis som i min metodik")
— Max kanske stryker det.

## Undvik

- "Vi har X"-formulering i spec-sektioner.
- "Utpekade", "består av", "sådan att", "motsvarar", "således", "därmed", "en delmängd
  av mängden".
- Långa meningar med flera bisatser.
- Akademiska citat mitt i löpande text ("*'for CP4, we use Dinic's algorithm...'*")
  — parafrasera hellre.
- Emoji.
- Sammanfattnings-punkter i slutet ("Slutresultat: ..."). Max vill ha berättelsen,
  inte en summering.
- **Distinktioner som inte påverkar approachen.** Ex: "hitta mängden U vs cut-värdet"
  spelar ingen roll för algoritmvalet — man kör ändå Dinic + BFS. Nämn inte sånt bara
  för att låta reflekterad; det tar plats utan att säga något.
- **Refererar till andra sektioner i samma dokument** ("precis som i min metodik",
  "som jag skrev i inledningen"). Max kan välja att stryka refererade sektioner.
- **Framåtreferenser till andra problem** ("denna mall återanvänds sedan i RA och king")
  — det kommer framgå naturligt när vi kommer till de problemen.
- **Framtida kunskap i tidiga process-steg.** När Max beskriver en fas *innan* hen läst
  kursmaterialet, nämn inte algoritmer eller termer som Max lärde sig senare. Ex:
  punkten "Formulerar delproblem" ska inte innehålla "innan jag vet att max-flow är
  svaret", det är retrospektiv-perspektiv smugglat in. Håll varje steg i sin egen
  tidsbubbla.
- **Långa bindestreck (em-dash `—`, en-dash `–`) i prosa.** Max vill inte ha dem.
  Bryt istället upp i separata meningar eller använd kommatecken/parenteser. OK att
  behålla korta bindestreck i sammansatta tekniska ord ("min-cut-värde", "s-t-cut",
  "0-indexerade") tills annat sägs.
- **Fet stil (`**text**`) i löpande text, punkttitlar, eller bullets.** Bara rubriker
  ska vara feta. Rubriker = markdown-headers (`##`) och sektionsnamn som Problembeskrivning,
  Regler, Delproblem, Lösningsprocess, Edge cases, Korrekthet. Ingenting annat får bold.
  Detta gäller även numrerade lista-titlar ("Läser problemet."), källhänvisningar
  ("Lab 2.7"), och teknik-termer inline. Fett tar bort läsflödet.
- **Backticks (`) för kod-inline.** Max vill inte ha dem i presentationstexten. Använd
  vanliga dubbla citattecken (") istället för variabler, kod-snuttar, och tekniska
  referenser. Backticks är för utvecklardokumentation, dubbla citattecken funkar bättre
  när texten läses upp muntligt eller renderas som prosa.

## Använd

- Korta, konkreta meningar.
- Vardagliga ord ("putsar", "typ", "sen", "så").
- Direkta verb.
- Inga radhänvisningar till koden ("rad 17", "mincut.py rad 50–51") i presentationstexten
  (beslut 2026-10-02). Peka på kodval med namn i citattecken ("add_edge", "cap == 0")
  i stället. Radnummer får användas i chatten när vi verifierar, men aldrig i texten.
- **Källhänvisningar — använd kursens egen materialhierarki när den finns.**
  För TDDD95/ETE389:
  - Seminarier heter t.ex. **Seminar Ex5 (Graphs II)**, inte "Lecture 6".
  - Undertopics är organiserade som labbar: **Lab 2.6 (Maximum Flow algorithms)**,
    **Lab 2.7 (Minimum Cut algorithm)**, **Lab 2.8 (Min Cost Max Flow)**.
    Bekräftat i timetable-länkar och i Lecture 6-slides själva.
  - Referens-mall: *"Jag läser **Lab 2.X (topic)** i **Seminar ExN (topic)**"*.
  - Slide-nummer OK som komplement när något specifikt behöver pekas ut, men
    lab-referensen ska vara huvudsaklig.
  - CP4 kan komma som komplement (*"... samt **CP4 kap 8.4**"*), men lab-referensen
    räcker ofta ensam.
- **Naturligt referens-mönster:** *"Jag läser **Lab 2.X (topic)** i **Seminar ExN**
  och lär mig..."*. Presens ("läser", "hittar") funkar bättre än preteritum i
  process-berättelser eftersom det placerar läsaren i lösningsstunden.
- **Cliffhanger-mönster mellan process-punkter.** En bra process-punkt slutar med en
  insikt eller observation som naturligt sätter upp nästa punkt, istället för att
  själv försöka lösa allt. Ex: p.3 slutar med "Man förstår ganska snabbt att min-cut
  är en del av en större process", vilket sätter upp p.4 att gå in på vad det större
  flödet är. Undvik att stapla flera delproblem-utredningar i en punkt.
- **Enkla punkttitlar:** "Delproblem 1" räcker som titel. Behöver inte utveckla med
  "— förstår begreppet via kursmaterialet". Titelraden ska vara ett ankare, inte en
  sammanfattning.
- **Egna ord för läroboksdefinitioner.** Direktciterade matematiska definitioner
  ("En s-t-cut definieras som en partition (C_s, C_t) med s ∈ C_s...") låter som
  läroboken pratar, inte Max. Parafrasera i vardagliga termer.

## Sektionsordning i ett problem-svar

1. `## N. "problemnamn" — kort algoritm-beskrivning`
2. **Problembeskrivning** (spec-stil)
3. **Regler** (spec-stil)
4. **Delproblem (frågor jag ställer mig när jag läser problemet)** (process-stil)
5. **Lösningsprocess — från problembeskrivning till kod** (process-stil, numrerad)
6. **Tidskomplexitet** (en rad per algoritm-del, inget mer)

Tidigare fanns "Inspiration" och "Tillvägagångssätt" som separata sektioner — dessa är
nu sammansmälta i **Lösningsprocess**. Behåll den strukturen framåt.

Separata "Edge cases"- och "Korrekthet"-sektioner är borttagna (beslut 2026-10-01).
Edge cases berättas i den process-punkt där de dök upp (t.ex. testpunkten).
Korrekthetsargumentet ska redan finnas i process-punkterna (teori-punkten, cut-punkten).

## Mincut är referensfacit (färdigt 2026-10-01)

Mincut-sektionen i `Presentation-Answers.md` är den första färdiga och ska användas som
mall för alla följande problem. Läs den innan nästa problem påbörjas.

**Punktordning i Lösningsprocess (mincut):**
1–2. Läser problemet, formulerar delproblem.
3. Snabb I/O (öppet: AI som referens).
4–6. Delproblemen via kursmaterial, nya delfrågor dyker upp.
7. Algoritmval: ett skäl, en källa ("I boken Competitive Programming så har man valt Dinic...").
8. Teori: vad bakåtkanterna gör och varför, med egna ord + CP4-sida.
9. Grafrepresentation: inspirationskälla (GfG) + vad jag gjorde annorlunda och varför.
10. Implementation av algoritmen (BFS-nivåer, DFS, "it[u]") med CP4-sidor.
    Slutar med cliffhanger mot nästa steg.
11. Resultatet läses ut (cut-BFS) med slide-referens i egna ord.
12. Testar Sample 1: slarvfel felsökta med AI, AI-genererade större testfall, edge cases
    som dök upp (rekursionsdjup).

**Lärdomar som gäller framåt:**
- Varför före hur: teori-punkten kommer före representation och implementation.
- Korta motiveringar. Ett skäl och en källa räcker. Stapla inte lab + slide + CP4 för samma val.
- Visa förståelse: förklara vad koden gör med vardagliga ord, inte bara var den kommer ifrån.
- Ange skillnader mot inspirationskällan (t.ex. kvarvarande kapacitet i stället för flow/C).
  Examinationen jämför mot vanliga lösningar på nätet, så skillnaderna visar egen förståelse.
- Inga dubbletter mellan punkter. Förklaras något i en ny punkt, stryk det ur den gamla.
- Hitta aldrig på händelser (fel, insikter, experiment). Fråga Max vad som hände. Minns
  Max inte, skriv det generellt och ärligt ("några små slarvfel").
- AI-användning skrivs öppet där den skett (I/O-idiom, felsökning, testdata). LiU kräver
  tydlighet kring generativ AI; IDA nämner "prohibited AI-based assistants".
- Verifiera varje citat, sidnummer och slide-nummer mot vault-källorna innan det skrivs in
  (`tddd95-slides/*.txt`, `CP4-Book2-Halim.txt`, `ete389-kursinfo/`).
- Bakåtreferenser till mincut är OK och önskade i senare problem ("samma Dinic som i
  mincut", "snabb I/O-mönstret från mincut"). Komponenter som etablerats i mincut:
  snabb I/O, Dinic (add_edge, BFS, DFS, "it[]"), residualgraf med bakåtkanter
  ("[to, cap, rev]"), cut-BFS från "s".

## Editerings-flöde

Max föredrar att vi går punkt för punkt istället för stora omskrivningar i ett svep.
För varje punkt: presentera nuvarande text, förslag på förbättring, be om beslut, tillämpa.
Inte förvänta sig godkännande för hela block på en gång.

Max har ofta `Presentation-Answers.md` öppen i VS Code. Be Max spara filen innan varje
ändring och vänta på "sparat nu", annars krockar osparade ändringar med disken.
Läs alltid om aktuell rad innan ändring; Max redigerar själv mellan stegen.

## Vad denna skill inte ska göra

- Ändra sakinnehåll (algoritmer, komplexitet, källor). Röst och struktur bara.
- Skapa nytt tekniskt innehåll utan att det är verifierat mot koden och kursmaterialet.
- Slå ihop punkter som Max separerat på — hen har medvetet valt granulariteten.

## Att förbättra vartefter

Denna fil ska växa. När Max ger feedback om röst, sektionsstruktur, ordval eller
källhänvisnings-format — uppdatera relevant avsnitt här. Historik: initialt utkast
2026-09-06 (kalibrering baserad på mincut-genomgång). 2026-10-01: mincut färdig,
referensfacit + lärdomar tillagda, Edge cases/Korrekthet ersatta av Tidskomplexitet.
2026-10-02: inga radhänvisningar i presentationstexten.
