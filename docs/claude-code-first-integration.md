# Getting Started: First Skill and First API Integration

A hand-off guide for someone who has never used Claude Code and wants to automate one real
business process. Written for macOS with the Claude Code desktop app. Takes a couple of hours
for steps 1 to 7, and the API integration is a separate sitting.

The goal of the first session is not a finished automation. It is a repo that exists, one
process written down, and one skill that runs. Everything after that is iteration.

## 0. Before you start

You need:

- A Claude subscription that includes Claude Code (Pro or Max), or API billing.
- Git. Check with `git --version`. macOS prompts to install the developer tools if it is missing.
- A GitHub account, and the `gh` CLI if you want Claude to create the remote repo for you:

```bash
brew install gh && gh auth login
```

Node is not required. The desktop app ships with Claude Code.

## 1. Install the desktop app and sign in

Download the Claude desktop app from [claude.com/download](https://claude.com/download) and sign
in. Claude Code is the Code tab in the sidebar. Everything below happens there, not in the chat tab.

## 2. Make the project folder

One folder per thing you are automating. Not a folder inside Documents that also holds your PDFs.

```bash
mkdir -p ~/Documents/<company>-automation
```

Pick a name you will still recognise in six months. The folder is empty on purpose. Claude fills it.

## 3. Start a session in that folder

In the Code tab, open that folder as the session directory. The session can only read and write
inside the folders you give it, so this choice matters more than it looks.

## 4. Let Claude set up the repo

First prompt of the first session:

> Set this folder up as a new git repo, create a private GitHub repo called `<name>` and push
> the first commit. Add a `.gitignore` that covers `.env`, credentials, tokens and OS junk
> before the first commit, not after.

Claude runs `git init`, `gh repo create` and the first commit. Approve the commands as they come
up. Read what they do before approving. That habit is the whole safety model.

Then:

```
/init
```

This writes a `CLAUDE.md`, the file Claude reads at the start of every future session in this
folder. Right now it will be thin because the repo is empty. Come back and fill it in once you
know what the project is. It is the highest-leverage file in the repo.

## 5. Lock down the secrets before you write any code

Say this explicitly in the session:

> API keys and tokens go in a gitignored `.env` or in `~/.config/`, never in a tracked file,
> never in `CLAUDE.md` and never in a skill. If you need a secret, ask me for the variable name
> and read it from the environment.

Do this before step 8, not during it. Keys that reach a commit have to be rotated, and a private
repo is not a mitigation.

## 6. Write the process down before building anything

This is the step people skip, and it is the one that decides whether any of this works.

Open a session and just talk through the process out loud, the way you would explain it to a new
hire. Then:

> Write what I just described to `docs/process-<name>.md`. Structure it as: trigger, inputs,
> the decision rules, the output, and what a human still has to approve. Ask me about every
> step where I was vague instead of guessing.

Answer the questions it asks. Those questions are the value of this step. Most processes turn out
to contain two or three decision rules nobody had ever written down, and an agent cannot infer
them from good intentions.

You now have a specification. The skill is a translation of it.

## 7. Build the first skill

```
/skill-creator
```

Tell it to build a skill from `docs/process-<name>.md`. A skill is just a folder:

```
.claude/skills/<skill-name>/SKILL.md
```

with YAML frontmatter holding a `name` and a `description`. The description is not documentation,
it is the trigger: it is how Claude decides whether to load the skill at all. Write it as the
phrases you would actually type. A skill with a vague description never fires.

Then test it the only way that counts. Start a fresh session, phrase the request the way you
would on a normal Tuesday, and see whether the skill loads on its own. If it does not, the
description is wrong, not the body.

Commit the skill. From here the repo is the unit of work: every change to the process is a commit,
and you can see what changed and when.

## 8. Add the API integration

Now the part that makes it real. Order matters: read before write.

**8a. Get credentials.** For Fortnox, register an integration in the Fortnox developer portal to
get a client id and secret, then run the OAuth2 authorization code flow with the scopes you need
and store the refresh token. Read the current Fortnox developer docs for the exact flow rather
than trusting any summary of it, including this one. Expect this step to take longer than the code.

**8b. Read-only first.** Ask Claude to write a small script that authenticates and fetches
something harmless, a list of accounts or last month's vouchers, and prints it. No writes. Run it
until it works. This proves the auth, which is where almost all the pain lives.

**8c. Interpret.** Point the skill at a real document and have it propose the output: for a
receipt, the account, the VAT split, the counterparty, the amount. Proposals only, nothing posted.

**8d. Review fifty of them.** Yes, fifty. This is where you find out that your VAT rule has
exceptions and that one supplier sends receipts with the total in the wrong column. Fix the skill,
not the individual cases.

**8e. Only then consider writing back.** For bookkeeping specifically, think hard before you
automate the write at all. A verifikation is something an auditor expects a named human behind,
and a proposal that a person approves in Fortnox is both safer and nearly as fast. "Claude
prepares, I approve" is a finished solution, not a stepping stone to one.

## 9. What the second week looks like

- Fill in `CLAUDE.md` properly, now that you know what the project is.
- When you catch yourself correcting Claude on the same thing twice, that correction belongs in
  `CLAUDE.md` or in the skill, not in your head.
- Second process gets its own skill in the same repo. Shared knowledge gets factored out once
  two skills need it, not before.
- Skills that are genuinely generic across projects can move to `~/.claude/skills/`, where they
  load in every session.

## Mistakes worth avoiding

**Building before writing the process down.** You end up debugging the skill when the problem is
that the process was never agreed.

**Authoring skills in the web UI.** A skill is a folder of files. If the only copy lives in a web
interface it is not versioned, not reviewable and not portable. Write it in the repo and upload
the zip when you need it elsewhere, never the other way around.

**Automating the write step on day one.** The read and interpret steps carry almost all the value
and almost none of the risk.

**Approving commands without reading them.** The permission prompt is the control. Skim it, or it
is doing nothing.
