---
name: schemakoll-cc
description: Stäm av schemat i Recman mot det regionen bokat i Bemlo, med Curas egna byten ur Bidplanner lagda ovanpå — för en avdelning och en period. Bemlo läses i Chrome bokning för bokning, Recmans schema och Bidplanners byten läses av ett skript, och skillnaderna listas dag för dag. Triggers on: schemakoll, stämmer Recman med Bemlo, jämför Bemlo-bokningar med Recman, bokningsbekräftelser mot schemat, stäm av schemat, kolla justeringarna, avropsjusteringar mot Recman.
---

# Schemakoll: Bemlo + Bidplanners byten mot Recman

Tre källor, en fråga. **Bemlo** har det regionen bokat, under namnet varje pass presenterades som,
med regionens accepterade avbokningar redan borta. **Bidplanner** har bytena: varje pass behåller
namnet det presenterades under, och vem som arbetar det är tilldelningen med omplaneringens byten lagda
ovanpå i den ordning de gjordes. **Recman** har schemat konsulterna arbetar och får lön efter. Bemlo med
bytena ska vara Recman, pass för pass.

Två sorters byten, två ställen:
- **Planerade byten** — vid presentationen eller i en omplanering — förs in i Bidplanner.
- **Byten vid sjukdom eller förhinder** förs in direkt i Recman. **Regel:** passet den som tar över får
  har den interna anteckningen `BYTE - Konsult B --> Konsult C` — först den som skulle ha passet, sedan den som
  tar det. "Skulle ha passet" är den Bidplanner har på passet, inte nödvändigtvis Bemlo-namnet: har
  ett pass presenterats som Konsult A och planerats om till Konsult B, och Konsult B blir sjuk, skrivs
  `BYTE - Konsult B --> Konsult C`. Schemakoll räknar då inte passet som en skillnad utan listar det under **Byten vid sjukdom
  eller förhinder**.

I Bidplanner är ett byte av ett byte ett nytt byte i
omplaneringen, från den som har passet nu — det presenterade namnet rörs aldrig. `Avrop justeringar.md`
i valvet är ersatt och läses bara med `--justeringar`.

Det är schemat som jämförs, inte registrerat arbete: ett pass som inte är arbetat är kalender, och
kalendern är vad konsulterna har fått veta.

Skillen läser. Den ändrar ingenting i Bemlo, Recman eller valvet. Rättelser görs för hand efter
rapporten.

## Input
- **Avdelning** — som Recman-projektet heter, t.ex. `näva`. Skriptet matchar del av projektets eller
  kundens namn utan hänsyn till prickar, och vägrar om strängen träffar fler än ett aktivt projekt.
- **Period** — en månad, `2026-11`, eller dagar, `2026-11-15:2026-12-14`. Ingen angiven → innevarande
  månad.

## 1. Bemlo, i Chrome

Bemlo har inget API vi betalar för, och scraperkontot stängdes 2026-10-19 för att det frågade för
mycket. Därför läses Bemlo **som en människa läser det**: Max egen inloggning i Chrome, en sida i
taget, bara DOM:en, inga egna anrop mot `api.bemlo.ai`. Ett tiotal sidor per avdelning och månad.

Ladda Claude in Chrome enligt `chrome-browser`-skillen. Öppna en egen flik.

**Stanna om Bemlo visar en inloggningssida eller ett meddelande om att kontot är spärrat.** Logga
inte in, försök inte igen. Säg till Max.

### Bokningarna
Öppna `https://app.bemlo.com/candidates/external` (menyn: Bokningar). Listan är sorterad med senast
skapade först och laddar 30 rader åt gången: scrolla till sista raden tills raderna som syns ligger
före perioden. Läs raderna med:

```js
JSON.stringify([...document.querySelectorAll('[href^="/candidates/contracts/"]')].map(a => {
  const t = a.innerText.split(/\n+/);
  return [a.getAttribute('href').split('/').pop(), t[1], t.find(x => /^[A-ZÅÄÖ]{3}\d{6}-\d+$/.test(x)),
          t.find(x => /^v\d/.test(x)), t.find(x => /^(Bokad|Avbokad)/.test(x)), t.some(x => /Ersättare/.test(x))];
}).filter(r => /* avropets prefix för avdelningen, t.ex. NÄR */ /^NÄR/.test(r[2] || '')))
```

Ett tomt svar betyder att listan inte hunnit ritas — fliken heter då bara "Bemlo". Vänta några sekunder
och kör igen. Svaret kan klippas efter ~1 500 tecken. Ta det i omgångar med `.slice()` hellre än att lita på en
avklippt lista.

Ta med varje rad vars **veckor överlappar perioden**, ersättarbokningar inräknade. En bokning `v45–v49`
hör till november även om den går in i december; `v49` 2026 börjar måndag 30/11. `Avbokad` tas inte med,
men nämn dem i rapporten.

### Passen
För varje bokning: gå till `https://app.bemlo.com/candidates/contracts/<id>/schedule` och kör
innehållet i `scripts/bemloschema.js` i `curaconnect-ai-framework` med `javascript_tool`. Skriptet
väntar själv på att sidan ritats klart och lämnar en rad JSON:

```json
{"id": "...", "name": "...", "ref": "NÄR260915-2", "unit": "...", "status": "Bokad", "scope": 12,
 "shifts": ["3/11 06:45-15:00", ...], "others": 0}
```

Skriptet är långt. Lägg det i sidans `localStorage` första gången (`localStorage.setItem('cura_bemloschema',
<källan som sträng>)`) och kör sedan `await eval(localStorage.getItem('cura_bemloschema'))` på varje
sida — `localStorage` följer med mellan sidorna på samma domän.

**Kontrollera varje rad innan den sparas:**
- `name` tomt → sidan hann inte ritas. Kör om på samma sida.
- `shifts.length` ≠ `scope` → läsningen når inte Bemlos eget "N pass". Ta en skärmdump och se efter
  innan raden används. (Schemafliken visar alla konsultens pass de veckorna; pass från en annan
  bokning ritas i grått och räknas i `others`, inte i `shifts`.)
- Långa bokningar ger långa svar. Klipps svaret, filtrera `shifts` på periodens månader i anropet,
  men skriv då in den filtrerade längden — `scope`-kontrollen gäller bara en hel läsning.

Spara en rad per bokning i `data/schemakoll/<avdelning>-<period>.jsonl` i `curaconnect-ai-framework`.
`data/` checkas aldrig in; filen har konsulternas namn.

Stäng fliken när alla bokningar är lästa.

## 2. Skriptet

I `~/Documents/curaconnect-ai-framework` (eller arbetskopian, som behöver en `.env`):

```
uv run scripts/schemakoll.py 2026-11 --bemlo data/schemakoll/nava-2026-11.jsonl --projekt näva
```

Skriptet läser Recmans bemanningskalender för projektet och perioden, läser bytena för de vunna
avropen i Bemlo-filen ur Bidplanner, lägger dem på Bemlos pass och jämför på datum och passtyp.
Arbetskopian läser produktionens databas om den inte startats med `--db`. Passtyp ur starttid: dag från 06,
kväll från 12, natt från 20 — Bidplanners standard.

### Hur bytena läses
Ur Bidplanner: presenterat namn är det sparade Bemlo-namnet, annars namnet avbokningen gjordes
under, annars tilldelningen. Vem som arbetar är tilldelningen med alla byten i omplaneringarna, i
ordning. Ett pass utan någon på är `obemannat` — inte en avbokning, och det förväntas inte i Recman.

Med `--justeringar`, ur noten:
- En rubrik `**... - NÄR260915-2 - 2026 - NOV**` ger avropet och året till raderna under.
- `12/11, tor, dag - Anna --> Bodil` byter passet som presenterades som Anna. `--> avbokning`
  tar bort det.
- Raderna matchas på **det presenterade namnet**, i notens ordning. Två rader samma dag — Annas pass
  avbokat, Bodils givet till Anna — påverkar inte varandra.
- Korta namn ("Yrsa TT", "Yrsa W") matchas mot Bemlos fullständiga: förnamnets början, sedan
  initialerna. Ett felstavat förnamn ("Bodli") godtas bara när en person är klart närmast.

## 3. Rapporten

Visa rapporten för Max som den är, och lägg till en tolkning per avsnitt:

- **Skiljer sig** — dag för dag. Recmans egna anteckningar står under: `avbokad:` är anteckningen på
  den förväntade personens obokade rad, `bokad:` på raden som ligger där i stället. De förklarar oftast
  skillnaden (sjuk, tenta, "X ersätter Y").
  - *Recman har någon annan* och anteckningen säger varför → ett byte gjort efter bokningen som saknas
    i `Avrop justeringar.md`. Föreslå raden att lägga till; skriv den inte själv.
  - *Recman har någon annan* och passet saknar BYTE-anteckning → ett byte vid sjukdom eller förhinder som
    inte fått sin anteckning, eller ett planerat byte som saknas i omplaneringen. Fråga Max vilket.
  - *Saknas i Recman* utan anteckning → passet är bokat i Bemlo men inte inlagt. Ska läggas in.
  - *Bokad i Recman men finns inte i Bemlo* → ett pass utan bokning bakom sig. Är det ett byte, för in
    det i omplaneringen. **Regel:** har avdelningen bokat passet direkt med oss, utanför Bemlo, skriver
    Max "direktbokning" i passets interna anteckning i Recman — då listas det för sig under
    **Direktbokningar, utan Bemlo** och inte som en skillnad. Recman har ingen uppdatering i API:t, så anteckningen skrivs
    för hand. Fråga Max om det är oklart; gissa inte.
  - *Tiderna skiljer* → rätt person, fel klockslag i ena systemet.
- **Justeringar som inte hittar sitt pass** — ett byte för ett pass Bemlo inte har. Oftast avbokat av
  regionen eller aldrig bokat, utan att Bidplanner fått veta det.
- **BYTE-anteckningar som inte går ihop** — anteckningen namnger någon annan än den som är bokad, eller
  någon som inte skulle ha passet enligt Bemlo med Bidplanners byten — till exempel Bemlo-namnet på
  ett pass som redan planerats om. Rätta anteckningen i Recman.
- **Avbokningar som Bemlo fortfarande listar** — avbokningen är inte accepterad i Bemlo.
- **Rader i noten att se över** — fel veckodag för datumet, ingen rubrik, ett avrop med justeringar men
  ingen läst bokning.
- **Bokningar där läsningen inte når Bemlos eget passantal** — läs om bokningen innan resten litas på.

## Gränser
- Läs bara. Klicka aldrig "Hantera", "Svara på bokningsbekräftelsen" eller något annat i Bemlo som
  ändrar en bokning.
- En flik, en sida i taget. Ingen loop som öppnar sidor utan att läsa dem.
- Inga konsultnamn i commits, tester eller anteckningar utanför valvet.
