---
name: konsultdialog-cc
description: Besvara mejl från Curas konsulter om uppdrag, krav och villkor — läser tråden, hämtar Curas formulerade svar ur valvet, föreslår ett svar och skriver efteråt tillbaka vad vi lärt oss om konsulten. Triggers on: svara konsulten, vad svarar vi, konsultens mejl, konsulten frågar om krav, hjälp med svar till konsult, mejl från läkare om uppdrag.
---

# Konsultdialog

Besvarar ett mejl från en konsult och ser till att det vi lär oss hamnar i valvet. Skillen skapar
utkast och skriver valvnoter — den skickar ingenting.

Systerskill till `bemlo-avropssok-cc`, som söker fram avropen och skickar listan. Den här tar
konversationen som följer på listan: konsultens frågor, hans svar på kraven, hans tillgänglighet.

Två noter bär underlaget. **Läs båda innan du skriver något.**

- [[Konsultvägledning]] i `obsidian-vault/Areas/Cura Connect/Notes/Konsultvägledning.md` — Curas
  svar på de återkommande frågorna, i färdig formulering, plus hur ett svar skrivs.
- [[Avropsbevakning-konsulter]] i samma mapp — per konsult: profil, kriterier, vad vi redan vet och
  vad vi aldrig ska fråga om igen.

Handlar frågan om en specifik enhet eller ett specifikt avrop: [[Avrop-kravprofiler]]. Handlar den
om avtalet — taxor, kompetensnivåer, ersättning — gå till avtalsnoten under `Notes/Avtal/` och
citera därifrån, inte ur minnet.

## Input
- Konsult (namn), eller en tråd. Inget angivet → fråga vilken konsult det gäller.
- Finns tråden inte given, sök den: `search_gmail_messages` på konsultens namn eller mejladress,
  och läs hela tråden med `get_gmail_thread_content`.

Använd `mcp__workspace-mcp__*` med `user_google_email`, aldrig de hostade Gmail-connectorerna.

## Läs tråden hela vägen

Läs varje meddelande, inte bara det sista. Tre saker ska vara klara innan du skriver:

1. **Vad konsulten faktiskt frågade**, med hans egna ord. Citera dem för Max när du redovisar vad
   svaret svarar på — han ska kunna se kopplingen utan att öppna mejlet.
2. **Vad vi redan har svarat.** Tråden kan innehålla flera utkast på samma svar, skickade minuter
   isär, som säger delvis olika saker. Det senast skickade är det som gäller. Upprepa inte ett svar
   i en ny formulering; motsäger det tidigare svaret, säg att det var fel och ge det rätta.
3. **Vad konsulten svarat som vi inte visste**, alltså det som ska in i registret efteråt.

## Skriv svaret

Allt om hur svaret skrivs står i [[Konsultvägledning]], under **Så skriver vi till konsulter** och
**Så skrivs ett svar**. Läs båda, följ dem, och återge dem inte här.

Formuleringarna hämtas ur notens poster. Står svaret där, använd det — hitta inte på en ny variant.
Står det inte där, skriv ett svar och lägg till posten efteråt (se **Avslut**).

Lägg utkastet i chatten först. Max vill läsa och ändra innan något hamnar i Gmail — räkna med flera
vändor, och visa bara det som ändrats när han ber om en justering, inte hela mejlet varje gång
annat än på begäran.

## Gmail-utkast

På begäran, med `draft_gmail_message` i konsultens befintliga tråd (`thread_id`). **Fråga vilken
avsändaradress som ska användas** — `max.nerdal@` eller `info@curaconnect.se`; kontots standard är
`info@`.

`draft_gmail_message` kan bara skapa, inte ändra. Ska ett utkast göras om: skapa det nya först,
leta reda på det gamla med `search_gmail_messages` på `in:draft subject:"..."` och lägg TRASH på det
med `modify_gmail_message_labels`. Säg till Max att du gjort det.

## Avslut

Två skrivningar, båda efter OK från Max.

**Konsultens avsnitt i [[Avropsbevakning-konsulter]].** Allt konsulten berättat om sig själv:
tillgänglighet och period, krav han uppfyller och inte uppfyller, regioner och arbetsformer han
utesluter. Skriv in det där det hör — **Sök efter**, **Diskvalificerar**, **Geografi**, **Vet vi
redan** — och plocka samtidigt bort det som nu är besvarat ur det som står som okänt. Poängen med
avsnittet är att nästa körning inte frågar om samma sak igen.

Sätt samtidigt **Senast hörd av** till dagens datum med en rad om vad konsulten sa. Den raden är
skillens, på samma sätt som **Senast körd** tillhör `bemlo-avropssok-cc` — rör inte den.

**En post i [[Konsultvägledning]]** om frågan var ny, eller om ett befintligt svar visade sig behöva
formuleras om. Skärp den befintliga posten i stället för att lägga en ny bredvid. Var frågan en
engångsfråga om ett enskilt avrop hör den inte hit — då räcker registret.

Säg i svaret till Max vad du skrivit och var, i en rad per not, så att han kan rätta direkt.

## Processen i valvet
[[Operations#Uppdragsmatchning befintliga konsulter]] — matchningen vars konversationsdel skillen
bär. Sökdelen: `bemlo-avropssok-cc`. Inventariet: [[Automationer]].
