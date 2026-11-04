---
name: sms-cc
description: Skicka ett SMS till en konsult från Curas nummer genom SMS-kanalen i curaconnect-ai-framework, så att det hamnar i samma logg och tråd som Skicka-knappen i Bidplanner. Visar mottagare och text och skickar först efter ett ja. Triggers on: skicka sms, sms:a konsulten, skicka ett sms till, messa konsult, texta konsulten.
---

# SMS till en konsult

Allt går genom `manage.py send_sms`, som kallar samma `sms.send` som Skicka-knappen. **Anropa aldrig
46elks direkt**, varken med curl eller i egen kod: då hamnar meddelandet utanför `SmsMessage`, tråden i
Bidplanner får svar utan fråga, och STOP-spärren och taket på tre SMS om dagen gäller inte.

Svaren behöver ingen åtgärd. De går över webhooken in i databasen och syns under SMS i Bidplanner.

Kör kommandona från `~/Documents/curaconnect-ai-framework`, som har `.env`.

## Input
- **Mottagare** — konsultens namn, del av namnet, Recman-id eller ett nummer. Kommandot vägrar om namnet
  träffar flera; fråga då vilken som avses, gissa inte.
- **Text** — högst 612 tecken. Varje påbörjad del om 153 tecken kostar ungefär 0,52 kr.
- **Avsändare** — `--as` är användarnamnet på den som ber om utskicket, i Max fall `maxnerdal`. Sätt
  aldrig någon annans namn: fältet säger vem som bestämde sig för att skicka.

## 1. Skriv texten
Använd användarens ord om de finns. Skriver du själv: kort, svenska, inga emojis.

Konsulten ser ett okänt nummer, så ett första SMS ska säga att det kommer från Cura Connect.

Handlar texten om pass eller avrop med svarsdag gäller regeln `deadlines`: jämför varje datum mot dagens
datum, stryk det som stängt, skriv fristen vid varje post som har en.

## 2. Provkör
```bash
uv run python manage.py send_sms --to "<mottagare>" --as <användare> --message "<text>" --dry-run
```
Det här skickar ingenting. Det visar vem numret tillhör och säger om STOP eller dygnstaket stoppar
utskicket. Stoppar en spärr är det slutet: kringgå den inte, föreslå telefon eller mejl. Bara konsulten
själv kan häva ett STOP, genom att skriva START.

Säger utdata `Ingen leveransrapport` är `SMS_PUBLIC_URL` tom i `.env`. Rätta det innan du skickar, annars
stannar statusen på Skickat.

## 3. Fråga
Visa mottagarens namn, numret och texten ordagrant, och vänta på ett uttryckligt ja. Ett ja gäller det här
meddelandet till den här mottagaren. Ändras texten eller mottagaren frågar du igen.

## 4. Skicka
Samma kommando utan `--dry-run`. Ett SMS går inte att ta tillbaka, och samma text två gånger är två SMS:
misslyckas kommandot, läs felet innan du försöker igen. En rad med status Misslyckades och utan
46elks-id nådde aldrig fram; ett timeout-fel kan däremot ha gått ut.

## 5. Rapportera
Säg vem det gick till, vad det kostade och att svaret syns under SMS i Bidplanner. Säg "skickat", inte
"levererat": leveransrapporten kommer efteråt och syns i tråden.
