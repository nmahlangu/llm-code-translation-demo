# Getting set up with Claude Code and Codex

Both tools are "coding agents": programs you point at a folder that can
read your files, edit them, and run commands (tests, scripts, compilers),
asking permission as they go. This is the difference from pasting code
into a chat website: the agent executes the work and checks its own
results in a loop instead of guessing once.

They are competing products with the same shape. Claude Code is from
Anthropic, Codex is from OpenAI. Each comes in two forms: a desktop app
with a graphical interface, and a command-line tool that runs in a
terminal. The app and the CLI of each product share the same underlying
agent; the choice is purely about which interface you prefer.

All links and commands below were verified against the official
documentation in June 2026.

---

## Option 1: a graphical interface (the desktop apps)

If you do not live in a terminal, start here; the desktop apps are the
gentler on-ramp and give up nothing that matters for this kind of work.
They use the same models as the command line tools do, so there is no 
reason to think they are worse in any way. In the last month, I've probably
used the Codex app the most, but I've used all four on this list at various times.

### Claude desktop app, Cowork tab (Anthropic)

**Download:** https://claude.com/download
(macOS and Windows; no Linux version, Linux users should use the CLI)

**Sign in:** with your Claude account on first launch. Cowork is
included with any paid plan (Pro, Max, Team, or Enterprise; plans at
https://claude.com/pricing); the free plan does not include it.

**Use:** the app opens to the familiar Claude chat view, which is easy
to get stuck in on a first launch: switch to the **Cowork** tab to get
to the agent. Give it access to the folder you want it to work in, then
describe the outcome you want in plain language. Claude makes a plan,
works through it (creating and editing files, running code in an
isolated sandbox), and delivers the results into your folder while you
watch and can steer. Keep the app open while it runs. You will also see
a **Code** tab; that is the same coding agent as the Claude Code CLI,
with a visual diff view. It works fine for this task too, but Cowork is
the more approachable starting point.

**Auto mode:** Cowork has two settings: **Ask before acting** (the
default: it shows its plan and pauses for your approval) and **Act
without asking** (it proceeds on its own; deleting files always
requires permission regardless). Same advice as everywhere else in this
guide: once you have watched it work for a session or two, "Act without
asking" inside a dedicated folder is the comfortable setting.

### Codex app (OpenAI)

**Download:** https://developers.openai.com/codex/app
(macOS and Windows; no Linux version)

**Sign in:** with your ChatGPT account on first launch. Codex is
included with ChatGPT Plus, Pro, Business, Edu, and Enterprise plans.
An OpenAI API key is an alternative, with usage-based billing.

**Use:** choose a project folder, make sure "Local" is selected so it
works on your machine, and type your first message. The diff pane shows
exactly what changed, and you can leave inline comments for Codex to
address, like reviewing a colleague's work.

**Auto mode:** the default setting already is the auto mode: Codex can
read, edit, and run things freely inside your project folder, and asks
before touching anything outside it or using the network. A permissions
selector under the chat input lets you dial that up or down.

---

## Option 2: the terminal (the CLIs)

Same agents, same capabilities, driven from a terminal instead of a
window. This is how most software engineers run them day to day.

### Claude Code CLI

**Product page:** https://code.claude.com/
**Docs:** https://code.claude.com/docs/

#### Install

macOS / Linux / WSL:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Alternatives: Homebrew (`brew install --cask claude-code`) or Windows
(`winget install Anthropic.ClaudeCode`).

#### Sign in and billing

Run `claude` once and follow the browser login. Two options:

- A Claude subscription (Pro, Max, Team, or Enterprise) includes Claude
  Code usage. Plans: https://claude.com/pricing
- Or an Anthropic Console account with pay-as-you-go API credits. For
  anything beyond occasional use this will almost certainly cost more
  than a subscription, so the subscription is the better choice.

#### Use

```bash
cd ~/projects/my-translation-project
claude
```

Then type what you want in plain language. Claude proposes file edits and
commands, and you approve them.

**Permission modes** (press `Shift+Tab` to cycle):

- **default**: asks before every edit and command. Fine for your very
  first session, while you build a feel for what it does.
- **accept edits**: file edits apply without asking each time; it still
  asks before running commands. This is the auto mode, and it is the
  right setting for beginners once the novelty wears off. In a dedicated
  folder with git underneath (see below), there is nothing it can do
  that you cannot inspect and undo.
- **plan**: read-only. Claude researches and proposes a plan, touching
  nothing. Good for "what would it take to port this?" conversations.

### Codex CLI

**Docs:** https://developers.openai.com/codex/cli
**Repo:** https://github.com/openai/codex

#### Install

```bash
npm install -g @openai/codex
```

Alternatives: Homebrew (`brew install --cask codex`) or the standalone
installer (`curl -fsSL https://chatgpt.com/codex/install.sh | sh`).
Windows users: native PowerShell install or WSL2.

#### Sign in and billing

Run `codex` once; "Sign in with ChatGPT" opens a browser. Codex usage is
included with ChatGPT Plus, Pro, Business, Edu, and Enterprise plans. An
OpenAI API key (usage-based billing) is the alternative.

#### Use

```bash
cd ~/projects/my-translation-project
codex
```

Codex's autonomy is controlled by two dials:

- **Sandbox** (`--sandbox`): `read-only`, `workspace-write` (can edit
  files inside the folder), or `danger-full-access`.
- **Approvals** (`--ask-for-approval`): `untrusted`, `on-request`, or
  `never`.

You rarely need to touch either: the default "Auto" preset
(`workspace-write` plus `on-request`) is the auto mode, and it is the
right setting for beginners. It edits freely inside your project folder
and asks before anything beyond that.

---

## Which model to use

Both vendors let you choose which model does the work, and on hard
tasks the model choice matters more than anything else in this guide,
so it is worth setting explicitly rather than taking whatever the
default is.

**For Claude (Claude Code and the desktop app):** use **Opus** or
**Fable**. Fable 5 is Anthropic's newest and most capable model, the
first of its Mythos-class models released to the public (June 2026);
Opus 4.8 is the tier below it and also excellent. In my experience,
Sonnet gives substantially worse results on this kind of work, and the
speed you gain is not worth what you lose. Set reasoning effort to
**High at a minimum**: the `/effort` command controls this in the CLI,
and on Fable and Opus, Claude Code defaults to xhigh (one step above
High), which is a good place to leave it. The `/model` command
switches models; the desktop app has a model dropdown when you start a
session.

**For Codex:** I use **GPT-5.5** with reasoning effort set to **extra
high** almost all the time. The `/model` command in the Codex CLI lets
you pick both the model and the reasoning level, and the app has the
same picker.

The honest tradeoff: the strongest models at high reasoning effort are
slower and consume your plan's usage allowance faster. For work like
code translation, where a subtle mistake costs you all the review time
this workflow is designed to save, that is the right side of the
tradeoff to be on.

---

## At the end of the day, it does not matter which you pick

Any of the four (two vendors, two interfaces each) can do everything in
this repository, including reproducing the whole translation from the
prompts in the README. Pick whichever feels comfortable and switch
freely later; nothing you learn is wasted, because the workflow is
identical everywhere. The one setting worth carrying with you: turn on
auto mode ("Act without asking" in Cowork, accept edits in the Claude
Code CLI, the default Auto preset in Codex) inside a dedicated folder.
Hand-approving every edit is what
makes these tools feel slow, and a dedicated folder plus git makes auto
mode low-stakes.

## A good first session

1. **Make a dedicated folder.** Copy the code you want translated into a
   fresh directory and run the agent there. The agent works inside that
   folder; your originals elsewhere are untouched.

2. **Use git as the safety net,** even if you never use it otherwise:

   ```bash
   cd my-translation-project
   git init && git add -A && git commit -m "original code, before any agent work"
   ```

   Now every change the agent makes is inspectable (`git diff`) and
   reversible (`git checkout .`). This, plus a dedicated folder, is what
   makes auto mode low-stakes.

3. **Ask for the harness before the translation.** The single biggest
   lever for trust. See the prompts in the [README](README.md); the short
   form is: "Before translating anything, write a test harness that pins
   the current behavior of this code. Show it to me. Then translate and
   iterate until the tests pass."

4. **Review the contract, not the diff.** When it finishes, read the test
   file and the recorded vectors and ask "is this the behavior I care
   about?" instead of reading the translated code line by line.

5. **Talk to it like a colleague.** "Why did you choose math.pow over the
   ** operator?" gets a real answer. "This quantile convention is wrong
   for my field, use type 6" gets a fix, and the tests update with it.
