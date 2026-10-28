---
name: bemlo-avropssok-cc
description: Sök fram aktiva avrop åt en bevakad konsult och sammanställ en lista som Max kan skicka vidare, som mejlutkast eller tabell. Avropen läses ur avropsdatabasen i första hand; Bemlo bara när databasen inte räcker, och då läkaravrop från JK-kontot och sjuksköterskeavrop från Cura-kontot. Triggers on: kolla avrop åt, vad finns för uppdrag, avropsbevakning, lediga uppdrag till konsult, sök avrop i Bemlo, skicka lista på uppdrag.
---

# Avropssök åt en bevakad konsult

Går igenom de aktiva avropen åt en namngiven konsult, sållar bort det som inte går att svara på,
och lämnar en lista som Max kan skicka vidare. Avropen läses ur avropsdatabasen i första hand och
ur Bemlo när databasen inte räcker. Skillen presenterar ingenting och ändrar ingenting i Bemlo —
den läser.

Konsultregistret: [[Konsultprofiler/Index|Index]] i
`obsidian-vault/Areas/Cura Connect/Notes/Konsultprofiler/Index.md`. **Läs det först.** Det säger vem
som är `bevakad` och därmed får sökas åt. Läs sedan konsultens profilfil i samma mapp: den säger
vilket konto, vilket filter och vad som diskvalificerar ett avrop för just hen. Finns ingen profilfil
är ingen behovsanalys gjord — fråga Max innan du söker.

## Input
- Konsult (namn). Ingen angiven → lista de bevakade ur registret och fråga vilken.
- Ev. avgränsning för den här körningen (region, period, minsta omfattning).

## Databasen först, Bemlo sedan

Avropen ligger i `curaconnect-ai-framework`-databasen, lästa ur Bemlo av avropsscrapern och
mejlflödet. **Sök där först.** Hela listan, skallkraven, zonen, tilldelningskriterierna, perioden,
omfattningen, svarsdagen och uppdragsbeskrivningen finns i tabellen — det är snabbare än Chrome,
det kräver inget kontobyte, och det går att fråga på tvärs över regioner.

Gå till Bemlo bara när något av det här gäller: fältet saknas i raden, raden ser inaktuell ut mot
det du vet, eller du ska presentera någon. Skillen presenterar ingenting, så den behöver sällan
Chrome alls.

```bash
cd ~/Documents/curaconnect-ai-framework
uv run python manage.py shell -c "..."
```

De öppna avropen för ett yrke och en region:

```python
from tenders.models import Tender
import datetime
qs = (Tender.objects
      .filter(status="open", deadline__gte=datetime.date.today(), profession="NURSE")
      .filter(region__icontains="uppsala")
      .select_related("ward").order_by("deadline"))
```

`profession` är `NURSE` eller `DOCTOR`. `region` skrivs på två sätt i tabellen — `UPPSALA` från
mejlflödet och `Region Uppsala` från scrapern — så filtrera alltid med `icontains`, aldrig på exakt
värde, annars tappar du halva träffarna.

Skallkraven ligger i `requirements` som en lista av dictar. De som konsulten måste uppfylla är de
med `required: True` och `kind: "custom"`; `kind: "document"` är pappersarbetet (HOSP, IVO, CV,
SITHS, belastningsregister, referens, överenskommelse) och gäller alla avrop lika.

```python
krav = [k.get("heading") or k.get("title", "")
        for k in (t.requirements or [])
        if isinstance(k, dict) and k.get("required") and k.get("kind") == "custom"]
```

Zon, tilldelning, journalsystem och beskrivning ligger i `source_data`, hela Bemlo-svaret rått,
under `vacancy.tender`:

```python
td = ((t.source_data or {}).get("data") or {}).get("vacancy", {}).get("tender", {})
td["availablePriceGroups"]   # [{title: "Zon 1: Leg. sjuksköterska", basePay: 616, ...}]
td["attributionCriteria"]    # [{type: "FILL_RATE", weight: 50}, {type: "CONTINUITY", weight: 50}]
td["requirements"]["journalSystemRequirements"]   # [{journalSystem: "COSMIC", isRequired: False}]
td["candidateDescription"]   # det konsulten ska läsa
td["vacancyDescription"]     # verksamhetens egen text
td["maxPresentations"]       # kan vara None, då finns ingen gräns
td["fillRate"]               # fyllnadsgraden just nu, 0 betyder att ingen presenterat än
```

Fällor i tabellen:

- **`enforceRows` betyder inte radbaserat.** Flaggan står `True` på avrop som inte kräver hel
  schemarad — 30 B, ORT261022-6, hade `True` och var ändå fritt att plocka pass ur (Max, 2026-10-28).
  Som med priset: skallkraven avgör, flaggan gör det inte. Säg aldrig till en konsult att ett avrop
  är radbaserat med den som enda grund.
- **`status: "open"` och svarsdag kvar räcker inte.** Läs `source_status` också: `FILLED` betyder
  att avropet redan är fyllt trots öppen svarsdag. `OPEN_FOR_PRESENTATIONS` är det som går att svara
  på, `URGENT` likaså.
- **Samma `reference` förekommer flera gånger.** Dels på olika enheter i olika regioner — `AVD261023-7`
  är både Avd 5 Jger i Stockholm och Avdelning 63 Hematologi i en annan region. Dels som dubblett av
  samma avrop: `source` säger vilken rad som är hel. `scraper` och `mail` är de lästa raderna;
  `manual` är en handimport, ofta av enhetens lediga pass ur en csv, och den har tom `profession`,
  `requested_hours: None`, tomt `source_status` och tomt `source_data`. 30 B låg 2026-10-28 som två
  rader på det sättet. Ta raden som har `source_data`, och matcha på enhetsnamnet, aldrig på koden
  ensam.
- `requested_hours` är avropets omfattning; summan av passens timmar ska stämma med den. Gör den
  inte det är raden halvläst.

## Webbläsare och konto

Behövs bara när databasen inte räcker, enligt ovan.

Claude in Chrome (`mcp__claude-in-chrome__*`). Två Chrome-profiler med varsin anslutning:

| Yrke | Konto | Organisation |
|---|---|---|
| Läkare | JK | SJV Konsult |
| Sjuksköterska | MN | Cura Connect |

1. `list_connected_browsers`. Saknas den profil du behöver → be Max öppna den Chrome-profilen,
   logga aldrig ut ur den andra.
2. `select_browser` på deviceId. **Visningsnamnen går inte att lita på** — "Browser 1" och
   "Browser 2" byter plats mellan anrop.
3. Öppna `/settings` och läs initialerna under Ditt konto: **JK** eller **MN**. Fel konto →
   byt profil. Hoppa aldrig över kontrollen; en läkarlista hämtad ur Cura-kontot blir tyst fel,
   kontot ser bara ett fåtal gamla läkaravrop.

## Filtrera i Bemlo

Bara när du gått till Bemlo. Filtrerar du i databasen i stället, se ovan.

`/vacancies/tenders`, knappen **Filtrera**. Filtren går att välja på: Utbildning (yrke +
specialisering), Land, Region, Kommun, Verksamhet, Kund, Startdatum, Svarsdag. Låt
**Göm stängda avrop** stå på.

Sätt Utbildning till konsultens yrke och sedan specialiseringen enligt registret. För en konsult
utan specialistbevis, eller med för kort specialisterfarenhet, är **`ingen specialisering`** rätt
val — den ger avropen som accepterar leg. läkare. Att filtrera på konsultens eget specialistområde
ger i stället avrop som kräver specialist.

Fallgropar:
- Filtret nollställs vid varje sidladdning. Gå aldrig till ett avrop och tillbaka och räkna med
  att filtret står kvar — hämta alla länkar först (se nedan).
- Listan laddar 30 rader i taget. Scrolla tills "Visar N resultat" slutar växa, annars tror du att
  du sett allt.
- Klick i yrkeslistan på ren koordinat råkar välja första raden. Skriv i sökfältet först och
  klicka sedan på träffen.

Hämta alla rader på en gång, innan du öppnar något avrop:

```js
const seen = new Map();
const collect = () => document.querySelectorAll('[href^="/vacancies/"]').forEach(a => {
  const h = a.getAttribute('href');
  if (h !== '/vacancies/tenders' && !seen.has(h)) seen.set(h, (a.innerText || '').trim().split('\n')[0]);
});
const scroller = [...document.querySelectorAll('div,main,section')]
  .filter(e => e.scrollHeight > e.clientHeight + 100 && e.clientHeight > 200)
  .sort((a, b) => b.scrollHeight - a.scrollHeight)[0];
collect();
for (let i = 0; i < 40; i++) { scroller.scrollTop += scroller.clientHeight * 0.7; await new Promise(r => setTimeout(r, 300)); collect(); }
({count: seen.size, rows: [...seen.entries()].map(([h, c]) => c + ' ' + h)});
```

## Sålla

Status **Aktiv** betyder inte att avropet går att svara på. Ta bort:
- Avrop vars period redan passerat, ofta med fyllnadsgrad 89–100 %.
- Avrop vars sista svarsdatum passerat. Svarsdagen i dag räknas som kvar, men säg i listan att den
  stänger i kväll — eller ta bort dem om Max ber om det.
- Avrop med skallkrav konsulten inte uppfyller. Vanligaste: krav på erfarenhet från just den
  enheten, krav på antal års klinisk erfarenhet, krav på bifogat specialistbevis.
- Avrop från enheter under konsultens **Enheter att undvika** i registret. En konsult som blivit
  avbokad från en enhet ska inte få tillbaka dess avrop i listan. Matcha på enhetsnamnet, inte på
  avropskodens prefix — flera enheter delar prefix.

Ett avrop kan ha prisrad för Leg. Läkare och ändå ha "bifogat specialistbevis" som skallkrav. Priset
avgör inte, skallkraven gör.

## Läs detaljsidan i Bemlo

**Behövs sällan.** Zon, krav, tilldelningskriterier och uppdragsbeskrivning finns i databasen —
se **Databasen först**. Det här är vägen när raden saknar `source_data`, eller när du vill
kontrollera något mot källan.

Zon, krav och uppdragsbeskrivning står inte i Bemlos lista, bara på avropets egen sida. Öppna varje
kvarvarande avrop och plocka ut delarna i stället för hela sidan:

```js
const t = document.body.innerText, c = document.title.split(' | ')[0];
const g = (a, b, n) => { const i = t.indexOf(a); if (i < 0) return ''; const j = t.indexOf(b, i); return t.slice(i, j < 0 ? i + n : Math.min(j, i + n)).trim(); };
c + '\n' + ((t.match(/Zon [0-9][^\n]*/g) || []).join(' / ') || 'ingen zon')
  + '\n' + g('INFORMATION TILL LEVERANTÖR', 'SKALLKRAV', 500)
  + '\n' + g('SKALLKRAV', 'TILLDELNINGSKRITERIER', 1600);
```

Zonen ligger i prisrubrikerna: `Zon 2: Leg. Läkare`, `Zon 2: Spec. Läkare`. Finns bara en rad för
Leg. Läkare konkurrerar konsulten inte mot specialistpriser alls — värt att nämna.

Skallkraven är ofta förkortade påståenden som "Medveten om att Närhälsan använder omvänd
utvärderingsmodell". Förklaringen står i `INFORMATION TILL LEVERANTÖR`, inte i skallkravet. Söker
du vad ett begrepp betyder: hämta hela informationsblocket ur det avrop som använder det, inte
avtalet och inte webben — enheten definierar sina egna termer i sin egen avropstext. Skriptets
teckengräns ovan klipper det blocket, så höj den för det avropet.

Ett avrop går bara att öppna från det konto som tagit emot det. Samma URL på fel konto ger en sida
som snurrar i all evighet utan felmeddelande och utan rader i konsolen. Snurrar en detaljsida:
byt konto, felsök inte sidan.

## Leverera

Tabell i chatten, sorterad på sista svarsdag:

| Avrop | Enhet | Ort | Zon | Period | Omfattning | Svarsdag |

Inget pris — det är Curas affär, inte konsultens. Lägg de uteslutna avropen i en egen kort tabell
med skälet, så att Max ser att de är bedömda och inte missade.

En avropslista är numrerad, ett avrop per nummer, varje punkt med period och omfattning, sedan
arbetets innehåll, sedan kraven, sedan svarsdagen. Avsluta med vad konsulten ska svara med: vilka
nummer, vilka veckor, vilka journalsystem, och sina två senaste uppdragsgivare för referenstagning.

Tonen står i **Så skriver vi till konsulter** i [[Konsultvägledning]] och gäller listan lika mycket
som ett svarsmejl: sakligt och kort, bara hälsningsfraser, krav skilt från verksamhetsbeskrivning,
inget pris. Läs den innan du skriver mejlet.

Mejlutkast skapas på begäran med `mcp__workspace-mcp__draft_gmail_message`, aldrig med de hostade
Gmail-connectorerna. **Fråga alltid vilken avsändaradress som ska användas** — max.nerdal@ eller
info@curaconnect.se.

**Svarar konsulten på listan, sluta här.** Konversationen som följer — hans frågor om krav och
villkor, hans tillgänglighet, hans besked om vad han inte uppfyller — bärs av `konsultdialog-cc`,
som har formuleringarna och som skriver tillbaka till registret. Skriv inga svar på konsultmejl i
den här skillen.

`draft_gmail_message` kan bara skapa, inte ändra. Ska ett utkast göras om: skapa det nya först,
leta reda på det gamla med `search_gmail_messages` på `in:draft subject:"..."` och lägg TRASH på
det med `modify_gmail_message_labels`. Säg till Max att du gjort det.

## Avslut

Skriv körningens datum och utfall i profilfilens **Logg**. Rör inte **Senast kontaktad** i
[[Konsultprofiler/Index|Index]] — den sätts när vi hört av konsulten, av `konsultdialog-cc`. Hittade du ett nytt
diskvalificerande mönster — ett krav som återkommer och som konsulten aldrig klarar — skriv in det
under konsultens **Diskvalificerar** i profilfilen efter OK från Max, så slipper nästa körning öppna
de avropen.

## Processen i valvet
[[Operations#Konsultmatchning]] — den manuella matchningen som skillen bär sökdelen av. Inventariet: [[Automationer]].
