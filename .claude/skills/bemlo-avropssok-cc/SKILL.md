---
name: bemlo-avropssok-cc
description: Sök fram aktiva avrop i Bemlo åt en bevakad konsult och sammanställ en lista som Max kan skicka vidare, som mejlutkast eller tabell. Läkaravrop hämtas från JK-kontot, sjuksköterskeavrop från Cura-kontot. Triggers on: kolla avrop åt, vad finns för uppdrag, avropsbevakning, lediga uppdrag till konsult, sök avrop i Bemlo, skicka lista på uppdrag.
---

# Avropssök åt en bevakad konsult

Går igenom Bemlos avropslista åt en namngiven konsult, sållar bort det som inte går att svara på,
och lämnar en lista som Max kan skicka vidare. Skillen presenterar ingenting och ändrar ingenting
i Bemlo — den läser.

Konsultregistret: [[Avropsbevakning-konsulter]] i
`obsidian-vault/Areas/Cura Connect/Notes/Avropsbevakning-konsulter.md`. **Läs det först.** Det
säger vilket konto, vilket filter och vad som diskvalificerar ett avrop för just den konsulten.
Står konsulten inte där, fråga Max om uppgifterna och lägg till ett avsnitt efter körningen.

## Input
- Konsult (namn). Ingen angiven → lista de bevakade ur registret och fråga vilken.
- Ev. avgränsning för den här körningen (region, period, minsta omfattning).

## Webbläsare och konto

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

## Filtrera

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

## Läs detaljsidan

Zon, krav och uppdragsbeskrivning står bara på avropets egen sida, inte i listan. Öppna varje
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

Mejlutkast skapas på begäran med `mcp__workspace-mcp__draft_gmail_message`, aldrig med de hostade
Gmail-connectorerna. **Fråga alltid vilken avsändaradress som ska användas** — max.nerdal@ eller
info@curaconnect.se.

Skriv sakligt och kort, i punktform där det passar. Inga inledningar, inga sammanfattningar, ingen
artighet utöver hälsningsfraserna. En avropslista är numrerad, ett avrop per nummer, varje punkt
med period och omfattning, sedan arbetets innehåll, sedan kraven, sedan svarsdagen. Avsluta med vad
konsulten ska svara med: vilka nummer, vilka veckor, vilka journalsystem, och sina två senaste
uppdragsgivare för referenstagning.

**Svar på ett mejl följer konsultens egen ordning.** Gå igenom hans punkter i den ordning han tar
upp dem, en rubrik per fråga, svaret i punktform under. Skriv inte om ordningen efter vad du
tycker är viktigast — han läser svaret bredvid sin egen fråga.

**Tackar konsulten nej med hänvisning till "kraven", är svaret en kartläggning, inte en ursäkt.**
Lista de skallkrav som återkom i uppdragen, avdubblade och ordagrant citerade, och be honom markera
dem han inte uppfyller eller inte är bekväm med. Svaret går in under **Diskvalificerar** i
registret och gör nästa lista kortare och träffsäkrare.

Listan ska bara innehålla krav vars svar vi faktiskt inte känner till, och som handlar om vad
konsulten kan och vill göra: kompetens, erfarenhet av en viss verksamhet, journalsystem, körkort,
patientbegränsningar. Tre saker hålls utanför:

- **Formalia och pappersarbete** — SITHS-kort och tillitsnivå, HLR-intyg, karens, belastnings-
  registret, HOSP, IVO. Inget konsulten råder över; det hör hemma i kandidatkollen.
- **Det vi redan vet.** Står svaret på kandidatkortet eller i registret, fråga inte. Att fråga en
  läkare med många år i yrket om han har två års klinisk erfarenhet efter legitimation säger bara
  att vi inte läst hans kort.
- **Schemavillkor**, som att konsulten ska ta hela veckor. Det är ett villkor i det enskilda
  avropet, inte en egenskap hos konsulten, och täcks av frågan om vilka veckor som är aktuella.

Håll isär krav och beskrivning i svaret. Det som står under SKALLKRAV är ett krav. Det som står i
verksamhetsbeskrivningen eller informationen till leverantör beskriver arbetet, och enheten kan
inte kräva mer än avtalets grundnivå med stöd av det. Säg det rakt ut till konsulten, annars läser
han en bred verksamhetsbeskrivning som en kravlista och tackar nej i onödan.

`draft_gmail_message` kan bara skapa, inte ändra. Ska ett utkast göras om: skapa det nya först,
leta reda på det gamla med `search_gmail_messages` på `in:draft subject:"..."` och lägg TRASH på
det med `modify_gmail_message_labels`. Säg till Max att du gjort det.

## Avslut

Uppdatera konsultens **Senast körd** i [[Avropsbevakning-konsulter]]. Hittade du ett nytt
diskvalificerande mönster — ett krav som återkommer och som konsulten aldrig klarar — skriv in det
under konsultens **Diskvalificerar** efter OK från Max, så slipper nästa körning öppna de avropen.

## Processen i valvet
[[Operations#Uppdragsmatchning befintliga konsulter]] — den manuella matchningen som skillen bär sökdelen av. Inventariet: [[Automationer]].
