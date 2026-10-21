---
name: tjanstepension-cc
description: Kvartalets tjänstepension för Curas konsulter — räkna fram underlaget ur Recman, logga det i valvet och mata in premierna som engångsinbetalning i Avanzas Pensionsportal. Körs i Chrome via Claude in Chrome. Triggers on: tjänstepension, kvartalets premier, pensionsunderlag, engångsinbetalning, Pensionsportalen, Avanza pension, pensionsinbetalning.
---

# Tjänstepension per kvartal

Körs första helgfria vardagen efter kvartalsslutet. Premien är 4,5 % av den pensionsgrundande lönen, betald i efterskott som en engångspremie per konsult på en gemensam faktura.

Registret över vilka konsulter som har tjänstepension, vad som räknas som pensionsgrundande, namnskillnaderna mellan systemen och loggen per kvartal: `[[Tjänstepension]]` i valvet. Läs den först — den är sanningen, inte den här filen.

## Input
Kvartalet, t.ex. `2026-Q4`. Inget annat; allt underlag hämtas.

## Gränser
- **Personnummer matas alltid in av Max.** Gäller `Lägg till medarbetare` och ingenting annat i flödet. Avanza slår upp namnet ur folkbokföringen, vilket är kontrollen att rätt person läggs upp.
- **Inskicket är Max beslut.** Fyll i allt, stanna på steg 2 av 2 och be om klartecken. `Lägg in engångsinbetalningar` skapar en faktura som inte går att ändra.
- Logga aldrig ut ur portalen, och rör inga andra konsulter än kvartalets.

## Underlaget — skriptet
I `~/Documents/curaconnect-ai-framework`:

```
./scripts/pensionsunderlag.py 2026-Q4              rapporten
./scripts/pensionsunderlag.py 2026-Q4 --artiklar   artikel för artikel, för avstämning mot Recman
./scripts/pensionsunderlag.py 2026-Q4 --skriv      loggar kvartalet i [[Tjänstepension]]
```

Skriptet summerar `sumSalary` per konsult ur Recmans `work`-scope och drar bort förmåner och viten enligt artikelregistret. Två saker kan det inte avgöra själv:

- **En konsult planen inte nämner.** Ny, eller eget bolag. Lägg id:t i `data/tjanstepension.txt`, med `-` framför om konsulten står utanför planen. Fråga Max — gissa aldrig.
- **En artikel utan regel.** Skrivs ut som en fråga och räknas inte. Visa namnet för Max och placera den i `BENEFIT_WORDS` eller `FEE_WORDS` i skriptet innan något betalas ut.

`--skriv` vägrar så länge något är oplacerat, och vägrar skriva ett kvartal som noten redan har. Spegla varje ändring i planfilen till tabellen i `[[Tjänstepension]]` — filen är gitignorerad och finns bara lokalt.

## Webbläsare
**Claude in Chrome** (`mcp__claude-in-chrome__*`), i en egen flik som stängs efteråt. Max loggar in på <https://pensionsportalen.avanza.se> med BankID — starta aldrig BankID själv.

Rör inte fliken medan Max fyller i något: en omladdning tömmer formuläret han står i.

`find` kostar en modellkörning och tar slut när kontots gräns nås. Läs hellre sidan med `javascript_tool` — tabellen är vanlig DOM och fälten har stabila namn (nedan).

## Lägg till medarbetare
Bara för konsulter som saknas i Medarbetare-listan. Kör gärna detta i förväg för alla konsulter som fått lön det senaste året, så slipper nästa kvartal avbrottet.

1. Max fyller personnummer. Avanza fyller namnet.
2. Du fyller telefonnummer och e-post. E-posten finns på kandidaten i Recman (`scope=candidate`, fältet `email`). **Telefonnummer finns inte i Recmans API** — det står bara på kandidatkortet i webbgränssnittet, så hämta det därifrån eller låt Max skriva det.
3. Förmånsgrupp `Fast belopp`, kostnadsställe `Kostnadsställe 1`, **startmånad = konsultens första lönemånad** (förvalet är innevarande kvartal och är fel för den som börjat senare), **månadspremie lämnas tom**.

## Engångsinbetalningen
1. Medarbetare → markera kvartalets konsulter. Matcha mot aliastabellen i `[[Tjänstepension]]`; listan innehåller även `Avanmäld`a och många som inte är i planen.
2. **Kontrollera antalet** innan du går vidare — fältet nedtill säger "Ändra N markerade". Enstaka klick fastnar. Lista de ikryssade och jämför mot noten:
   ```js
   Array.from(document.querySelectorAll('input[type=checkbox]')).filter(c => c.checked)
     .map(c => (c.getAttribute('aria-label') || c.labels?.[0]?.textContent || '').replace('Markera ', '').trim())
   ```
3. `Engångsinbetalning` i samma fält. Formuläret har en rad per konsult med `input[name="amount-input-<försäkringsid>"]` och `note-input-<försäkringsid>`, plus en översta rad "Ange belopp för alla" / "Ange kommentar för alla".
4. Fyll belopp och kommentaren `2026 Q4` per rad. Sätt värdet via `HTMLInputElement.prototype.value`-settern och skicka `input`- och `change`-event, annars ser React det inte.
5. **Förfallodatum = körningsdagen + 7 dagar.** Förvalet är sista dagen i nästa månad, vilket är för sent när kvartalet redan dragit över — Max fakturabolag ska hinna betala. **Det fältet tar inte emot ett satt värde**, trots att det läser tillbaka rätt: sätt det i datumväljaren och läs av det på steg 2. I Q3 2026 missades det och fakturan fick förvalet.
6. Läs tillbaka alla rader ur DOM:en och jämför summan mot noten innan du går vidare.
7. `Fortsätt` → steg 2 av 2. Visa Max raderna **och förfallodatumet**, och vänta på klartecken innan `Lägg in engångsinbetalningar`.

## Efter inskick
1. Fakturan laddas ner som `avanza_invoice_<nr>.pdf` i `~/Downloads`. Läs båda sidorna: sida 2 är specifikationen per kostnadsställe, en rad per konsult.
2. Stäm av varje rad och totalen mot checklistan i noten.
3. Skicka fakturan vidare till bokföringens leverantörsadress — den står under *Home* i `[[Tjänstepension]]`. Skriv den inte här: repot är publikt, och adressen tar emot leverantörsfakturor från vem som helst.
4. Skriv in fakturanummer, OCR, belopp och förfallodatum i kvartalets avsnitt i `[[Tjänstepension]]`, och bocka av raderna.

## Kända egenheter
- Månadspremien står kvar på 0 kr för alla — premien är en engångsinbetalning, inte en löpande premie. Sätt aldrig en månadspremie.
- Fakturan kan betalas före förfallodatum; en felsatt förfallodag går inte att ändra i efterhand utan att ringa Avanza.
- Avanmälda konsulter ligger kvar i listan. Status säger inget om planen — planfilen gör det.
- En konsult med eget bolag ser ut som vem som helst i arbetsraderna; `salaryPaid` sätts per rad och duger inte som markör. Därför `-` i planfilen.
- Portalen ersätter Företagswebben, som stänger. Gamla länkar till `foretagswebb.avanza.se` leder rätt ett tag till men ska bytas.

## Avslut
Kort rapport: antal konsulter, summa, fakturanummer, vad som ändrades i planfilen, och allt som lämnades öppet (oplacerade artiklar, konsulter Max inte svarat om).

## Processen i valvet
[[Operations#Tjänstepension — inmatning i Pensionsportalen]] — stegen för hand. Schemat: [[Recurring deadlines#Kvartalsvis — Tjänstepension (Pensionsportalen)]]. Registret och loggen: [[Tjänstepension]].
