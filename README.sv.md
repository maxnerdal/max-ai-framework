# max-ai-framework

*[English](README.md) · [Svenska](README.sv.md)*

Max Nerdals personliga AI-ramverk för Claude Code. En delad verktygslåda av skills, agents, slash-kommandon, workflows, prompts, templates och MCP-servrar som gör om Claude Code från en generisk assistent till en kontext-medveten kollaboratör över två bolag (Cura Connect AB, Max Nerdal AB) och privatliv.

Detta repo är källan. Det symlinkas in i `~/.claude/` så att varje projekt på maskinen ser samma verktygslåda och samma identitet, oavsett från vilken katalog Claude Code startas.

## Varför det finns

En standard Claude Code-installation startar varje samtal kallt. Den vet ingenting om vem du är, vad du jobbar med, vilka standarder du har eller var den ska hitta dokumenten den behöver. Du hamnar i att förklara samma kontext varje session och bygga om samma automationer i varje repo.

Ramverket löser det genom att pusha fyra saker uppåt:

1. **Identitet, en gång, globalt.** En enda top-level `CLAUDE.md` beskriver vem jag är, vad jag driver och hur min kunskap är strukturerad, så att varje Claude Code-session i vilken katalog som helst startar med rätt antaganden.
2. **Affärskunskap i en Obsidian-vault.** Affärsdokument, brand voice, projektstatus och beslutsloggar bor i en second-brain-vault. Ramverket berättar för Claude hur den ska upptäcka och ladda kontext från vaulten on demand istället för att hårdkoda det.
3. **Återanvändbara förmågor som skills, agents, kommandon, workflows.** Allt jag annars hade skrivit om som en engångsprompt lever här som en versionerad artefakt.
4. **Externa system som MCP-integrationer.** Google Drive, Gmail, Kalender och Google Tasks är kopplade så Claude kan läsa/skriva riktig state, inte bara chatta om det.

Resten av denna README går igenom vart och ett av dessa lager: vad det gör, varför och var det finns.

## Lagren

### Lager 1: Global identitet (`.claude/CLAUDE.md`)

**Vad:** Top-level system-prompten som laddas in i varje Claude Code-session på maskinen. Introducerar mig, bolagen, vaulten, allmänna preferenser (koncisa svar, inga emojis, inga onödiga kommentarer), Gmail/Kalender-kontoruting och area-suffix-konventionen som allt annat i ramverket följer.

**Varför:** Utan detta skulle varje nytt projekt behöva egen bootstrap och Claude skulle ställa samma setup-frågor för evigt. Med det kan jag `cd`:a in i vilket repo som helst (även ett jag skapade för fem minuter sedan) och Claude vet redan setup:en.

**Var:** `.claude/CLAUDE.md` i detta repo, symlinkat till `~/.claude/CLAUDE.md`.

### Lager 2: Obsidian second brain

**Vad:** En Obsidian-vault på `~/Documents/obsidian-vault/` innehåller allt som ändras över tid och inte hör hemma i kod:

- **Affärskontext per area** i `Areas/{Cura Connect, Max Nerdal AB, Personal}/_context/` (brand voice, ICP, operations). Statisk, kanonisk.
- **Varje projekt jag kör**, en anchor-fil per projekt i `Areas/{area}/Projects/<Namn>.md`, med `status: active | paused | done` i frontmatter, en beskrivning, hela plan-checklistan och en decisions log. Supporting docs bor bredvid anchorn (`<Namn>-architecture.md`, `<Namn>-flatten.md`, osv). Projekt som växer förbi ~3 filer promotas till en folder med `Index.md` som anchor.
- **Daily logs** i `Daily logs/YYYY-MM-DD.md` som fångar dagens slice av projektarbetet som `[[wikilinks]]`, tankar, idéer.
- **Idéer** routas till en av tre livscykel-hem: dagens `## Ideas`-sektion (färska), en projekt-anchor (kopplade till aktivt arbete), eller `Areas/{area}/Notes/` (evergreen).
- **Meeting notes**, evergreen SOP:er, cross-area referensmaterial.

**Varför (den verkliga vinsten):** Vaulten gör om "vilket projekt pratar vi om?" till en billig uppslagning istället för en lång fråge-och-svar-runda. När jag säger "let's continue on framework-refaktorn" eller droppar en `[[max-ai-framework-flatten]]`-wikilink, läser Claude *en liten anchor-fil* och vet direkt: vad projektet är, vad som är gjort, vad som är näst på checklistan, vilka beslut som fattats och varför, vilka arkitektur-supporting-docs som finns. Ingen re-briefing, ingen re-förklaring, inga tokens brända på kontext-rekonstruktion. Status-frontmattern gör också att "vad jobbar jag med just nu?" är en enda glob efter `status: active` över alla areor.

Code repositories är en dålig plats att förvara det här på. De blir stale, de blandar kod med planer, de sprider ett projekts kontext över flera repon och de cross-länkar inte. Vaulten sitter *ovanför* repona och är single source of truth för *vad som är sant just nu om arbetet*.

**Hur Claude hittar det:** `.claude/rules/obsidian.md` lär Claude när vault-läsningar ska triggas (projektfrågor, "vad jobbar jag med idag", namngivna projekt, `[[wikilinks]]`) och när inte (generiska kodfrågor, verktygsanvändning, system-setup). Read-passively vs. read-conditionally är utspecat per sektion så att vaulten inte skannas för varje prompt. En coupling-regel ser till att en edit på en projekt-anchor också kollar supporting docs för mirror-uppdateringar.

**Var:** Vaulten ligger utanför detta repo (personlig data). Loading-regler: `.claude/rules/obsidian.md`.

### Lager 3: MCP-integrationer

**Vad:** Model Context Protocol-servrar som ger Claude Code riktig läs/skriv-åtkomst till externa system.

- **`workspace-mcp`** (registrerad user-scope via `claude mcp add -s user`): Google Drive, Gmail, Kalender, Google Tasks, Docs, Sheets, Slides, Forms, Contacts. Multi-account by design: varje verktygsanrop tar ett `user_google_email`-argument, så samma server routar till `maxnerdal@gmail.com` eller `max.nerdal@curaconnect.se` per anrop. En server, båda inkorgarna, båda Drive-kontona, båda Tasks-listorna.

**Varför:** Att Claude bara kan "läsa filer" är en hård gräns. Med MCP kan morning briefings hämta olästa mail och dagens kalender. Backlog-items landar i Google Tasks. State bor där jag redan tittar (Gmail, Kalender, Drive, Tasks-appen), inte i en Claude-only sandbox.

**Var:** `.mcp.json.example` visar project-scope-registreringsmönstret för repon som vill bundla sina egna MCP-servrar. Setup: `docs/google-workspace-mcp-setup.md`, `docs/server-setup.md`.

### Lager 4: Skills (`.claude/skills/*/SKILL.md`)

**Vad:** Atomära, portabla förmågor. Varje skill är en folder med en `SKILL.md`-fil med frontmatter som Claude autodiscoverar och triggar när beskrivningen matchar uppgiften.

Nuvarande skills:

- **Delade (`-s`):**
  - `drive-reader-s/` läser Drive-filer efter namn eller ID (CV:n, brev, referenser, tidigare ansökningar).
  - `drive-writer-s/` skriver färdiga dokument till Drive med konventionen `application-YYYYMMDD-företag-roll`.
- **Personliga (`-p`):**
  - `job-post-parser-p/` parsar en URL eller inklistrad annons till ett strukturerat job-objekt, arkiverar posten.
  - `job-tracker-p/` läser/skriver job application tracker Google Sheet.
  - `job-searcher-p/` söker webben efter jobb som matchar min profil, filtrerar dubbletter.
  - `cv-tailorer-p/` föreslår riktade CV-edits per jobb.
  - `personal-letter-writer-p/` skriver skräddarsydda personliga brev i min röst.
  - `screening-answerer-p/` hanterar screening-frågor från ansökningsformulär.
  - `interview-prepper-p/` genererar troliga intervjufrågor och företagsresearch.

**Varför:** Skills hålls små och single-purpose så de kan komponeras. De är portabla (inga Claude-Code-specifika antaganden) så de kan återanvändas i andra harness senare.

**Var:** `.claude/skills/`, symlinkat till `~/.claude/skills/` för global discovery.

### Lager 5: Agents (`.claude/agents/*.md`)

**Vad:** Claude-Code-specifika sub-agents som kör sin egen tool-loop med en begränsad tool-allowlist. Används för de delarna av ett workflow som gynnas av isolation eller en snävare toolset.

- `application-drafter-p.md` kör hela drafting-pipelinen för en jobbansökan (parsar posten, laddar CV + brev, föreslår ändringar) och stannar innan något skrivs, så användaren kan reviewa.
- `application-finalizer-p.md` verkställer de godkända ändringarna: kopierar källdokument till ny folder, applicerar edits, uppdaterar tracker:n.
- `interview-preparer-p.md` kör intervju-prep-flödet från början till slut.

**Varför:** Vissa jobb är röriga nog att förtjäna sitt eget samtal. Agents håller huvudchatten ren och låter mig scopa tools snävt (en agent som gör webbresearch behöver inte också edit-access till vaulten).

**Var:** `.claude/agents/`, symlinkat till `~/.claude/agents/`.

### Lager 6: Slash-kommandon (`.claude/commands/*.md`)

**Vad:** Användar-triggade entry points invokerade som `/name`.

- `/morning-s` bygger dagens morning briefing i Obsidian daily note (kalender, digest av olästa mail, förfallna tasks per area).
- `/sweep-s` end-of-day-closer som syncar briefingens check-marks med Google Tasks bidirektionellt.
- `/job-application-p` kör jobbansökan-workflow.
- `/interview-prep-p` kör intervju-prep för ett jobb i tracker:n.
- `/update-application-p` uppdaterar en inskickad ansökan (fixar, uppföljningar).

**Varför:** Slash-kommandon är kortaste vägen från "jag vill X" till att Claude gör X. Två-bokstavs-suffixen förhindrar oavsiktliga cross-area-triggers (ett Cura-specifikt kommando ska inte fyra under personligt arbete och vice versa).

**Var:** `.claude/commands/`, symlinkat till `~/.claude/commands/`.

### Lager 7: Workflows (`workflows/<name>/WORKFLOW.md`)

**Vad:** Flerstegs-orkestrering som kombinerar skills och agents till en full pipeline. För tillfället: `job-application-p/`, `interview-prep-p/`, `update-application-p/`.

**Varför:** Skills svarar på "vad kan jag göra?", workflows svarar på "hur passar de här bitarna ihop för det här end-to-end-jobbet?". Att dela upp dem håller de atomära skillsen återanvändbara medan workflow:et fångar den specifika sekvensen för ett use case.

**Var:** `workflows/` i repo-roten.

### Lager 8: Prompts och templates

**Vad:**
- `prompts/` delade skrivkonventioner som appliceras över skills: `tailoring-principles-p.md`, `source-material-loader-p.md`, `drive-output-conventions-p.md`.
- `templates/` HTML-scaffolds för färdiga artefakter: `cv-p.html`, `letter-p.html`, `job-post-p.html`.

**Varför:** Två skills som båda skriver till Drive ska inte vara oense om formattering. Två skills som båda skräddarsyr innehåll ska inte ha varsin motstridig uppfattning om "hur ärligt" skräddarsy får vara. Att centralisera detta i `prompts/` och `templates/` betyder att en tone- eller format-ändring på ett ställe propagerar överallt.

**Var:** `prompts/`, `templates/`.

## Hur global åtkomst funkar

Varje lager ovan behöver kunna nås från vilken katalog som helst på maskinen, inte bara inifrån detta repo. Tre separata mekanismer är i spel:

**1. Symlinks in i `~/.claude/`.** `setup.sh` länkar de repo-kontrollerade delarna av ramverket in i user-scope Claude Code-config-katalogen som varje session läser vid start:

```
~/.claude/CLAUDE.md   ->  ~/Documents/max-ai-framework/.claude/CLAUDE.md
~/.claude/agents      ->  ~/Documents/max-ai-framework/.claude/agents
~/.claude/commands    ->  ~/Documents/max-ai-framework/.claude/commands
~/.claude/rules       ->  ~/Documents/max-ai-framework/.claude/rules
~/.claude/skills      ->  ~/Documents/max-ai-framework/.claude/skills
```

Det är därför `/morning-s`, `@application-drafter-p` och varje skill är tillgängliga oavsett om Claude Code startas i `~/Documents/hosp-automation/`, i en scratch-folder eller var som helst. Hela `~/.claude/` symlinkas *inte* (Claude Code skriver runtime-state där som inte hör hemma i repot). Bara de fem sökvägarna ovan länkas in.

**2. Indirekt referens för workflows.** Workflow-mapparna ligger på `workflows/*/WORKFLOW.md` i detta repo och är *inte* symlinkade. Istället innehåller varje slash-command som äger ett workflow en one-liner typ *"Read and execute the workflow at `workflows/job-application-p/WORKFLOW.md`"*. Eftersom globala `CLAUDE.md` berättar för Claude att ramverket bor på `~/Documents/max-ai-framework/`, resolvas den relativa sökvägen mot repo-roten och filen läses direkt. Workflows är alltså inte "installerade globalt"; de är *refererade* från commands som är det.

**3. MCP-servrar.** Dessa registreras separat, inte via symlinks. `workspace-mcp` registreras user-scope (`claude mcp add -s user ...`) så att varje projekt ser den. Repon kan även registrera egna MCP-servrar project-scope via en `.mcp.json` i repo-roten, som Claude Code plockar upp när den startas inuti det repot. Se `.mcp.json.example` för mallen.

## Area-suffix-konventionen

Varje skill, agent, command, workflow och prompt taggas efter primär förmånstagare via ett filename-suffix, så att ramverket kan splittas per area senare utan att man grep:ar innehåll.

| Suffix | Area | Exempel |
|--------|------|---------|
| `-cc` | Cura Connect | `hosp-cert-checker-cc.md` |
| `-p` | Personal | `cv-tailorer-p/`, `/job-application-p` |
| `-mn` | Max Nerdal AB | `consulting-proposal-writer-mn/` |
| `-s` | Delad | `/morning-s`, `drive-reader-s/` |

Suffixet följer med hela vägen till invokering: filen `application-drafter-p.md` blir agenten `@application-drafter-p`; filen `morning-s.md` blir kommandot `/morning-s`. Vid tveksamhet: default till `-s` och promota till en specifik area först när verktyget växer hårda dependencies på den area:ns data eller credentials.

## Runtime-tuning

Små config-ändringar som gjorts för att hålla Claude Code smidig dag för dag. Dokumenterat så jag vet varför de finns och kan reproducera dem på en fresh machine.

- **Bred `WebFetch`-permission i `~/.claude/settings.json`.** Research-sessioner brukade avbrytas varje par minuter för att godkänna en ny domän. Nu är `WebFetch` tillåtet globalt. Tradeoff accepterad: vilken URL Claude än väljer att hämta går igenom utan prompt. Säkert på en solo-utvecklarmaskin, skulle inte vara säkert i en delad miljö.
- **`skipDangerousModePermissionPrompt: true`.** Undviker modalen vid varje session-start.
- **Model default: `opus`.** Satt globalt istället för att väljas per session.
- **Voice mode aktiverat (hold-to-talk).** Snabbare än att skriva för långa diktioner.

Projekt-scopade MCP-allowlists (`.claude/settings.local.json`, gitignored) växer över tid när jag godkänner enskilda servrar/domäner. Den filen är inte portabel; de durable-inställningarna finns i `~/.claude/settings.json` och `.claude/settings.json`.

## Designprinciper

- **Delat bibliotek, inte container.** Skills/agents bor här; projektkod bor i eget repo per app (Cura Connect-appar i `~/Documents/hosp-automation/`, `curaconnect-ai-framework`; Max Nerdal AB-appar som tradingbots vart och ett i eget repo).
- **App-repon tillhandahåller projektkontext.** Varje apps `CLAUDE.md` `@`-importerar de relevanta Obsidian area-dokumenten.
- **Obsidian är second brain.** Affärskunskap, brand, strategi, projektstate allt i vaulten. Code repos håller kod och beteende.
- **Logik bor i repot, data gör det inte.** Personliga filer stannar i Google Drive; secrets stannar i gitignored `config.md` eller `~/.config/`.
- **Skills portabla, agents Claude-specifika.** Så att de atomära förmågorna kan återanvändas om jag flyttar bort från Claude Code senare.
- **Inga em-dash i genererat innehåll.** House style.

## Repo-layout

```
max-ai-framework/
  .claude/                    Symlinkat in i ~/.claude/
    CLAUDE.md                 Global identitet + preferenser (Lager 1)
    agents/                   Claude Code sub-agents (Lager 5)
    commands/                 Slash-kommandon (Lager 6)
    rules/obsidian.md         När och hur vaulten ska läsas
    skills/                   Atomära förmågor (Lager 4)
    settings.json             Globala permissions/theme/model
    settings.local.json       (gitignored) Maskin-specifika godkännanden
  workflows/                  Flerstegs-orkestrering (Lager 7)
  prompts/                    Delade skrivprinciper (Lager 8)
  templates/                  HTML-templates för färdiga docs
  docs/                       Setup-guider + referensmaterial
  shell/aliases.sh            Source:ad av ~/.zshrc via setup.sh
  .mcp.json.example           Project-scope MCP-registrerings-mall
  config.example.md           Drive-ID:n + OAuth-paths template
  config.md                   (gitignored) Faktiska ID:n/paths
  setup.sh                    Skapar ~/.claude/-symlinks
  CLAUDE.md                   Repo-nivå-kontext för Claude
```

## Kom igång

Se [docs/setup.md](docs/setup.md) för setup på en fresh machine.

För always-on server-setup: [docs/server-setup.md](docs/server-setup.md).

För Google Workspace MCP-konfigurationen: [docs/google-workspace-mcp-setup.md](docs/google-workspace-mcp-setup.md).

För hur Claude Code hittar kontext (CLAUDE.md-laddningsordning, imports, precedens): [docs/claude-context-loading.md](docs/claude-context-loading.md).
