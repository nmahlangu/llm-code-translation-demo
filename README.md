# Can you trust an LLM to translate code? A verifiable demo

This repository is a small, complete, checkable example of using an LLM
coding agent to translate a library from one language to another:
a JavaScript arithmetic and statistics library, ported to Python, with the
evidence that the port is correct included and reproducible.

It was put together after a conversation about whether these tools can be
trusted with exactly this kind of task. The honest answer is: you should not
trust the model. You should trust the verification harness the model builds
and runs, which you can read in an afternoon. That distinction is the whole
point of this repo.

## The short version

- `original-javascript/mathlib.js` is the original: 17 functions, from
  `add` and `divide` up to sample variance, quantiles, Pearson correlation,
  and least squares regression.
- `translated-python/mathlib.py` is the port, produced by an LLM coding
  agent (Claude Code).
- 139 automated checks establish that the two behave identically. They all
  pass, and you can rerun them with one command (see below).

The key design decision: the definition of "correct" never comes from the
model. It comes from two places that have nothing to do with the model:

1. **The original program, executed.** `generate_vectors.js` runs the real
   JavaScript library with Node.js across 86 input batteries (typical
   values, edge cases, and invalid inputs) and records exactly what it
   returned or threw in `test_vectors.json`. The Python port must reproduce
   every recorded case. The model never gets to decide what the right
   answer is; the original code does.
2. **An unrelated implementation.** Where Python's standard `statistics`
   module computes the same quantity (mean, median, variance, correlation,
   regression, quantiles), the tests require agreement with it. Two
   independent implementations agreeing is strong evidence neither is wrong.

On top of that sit hand-written unit tests for edge cases and error
behavior, and an end-to-end analysis (study hours vs. exam scores:
descriptive statistics, correlation, regression, prediction) with the final
numbers pinned.

## What is in the repo

```
original-javascript/
  mathlib.js            The original library (the input to the translation)
  generate_vectors.js   Executes mathlib.js, records 86 golden input/output cases
  test_vectors.json     The recorded cases (committed so you can inspect them)
translated-python/
  mathlib.py            The Python port (the output of the translation)
  test_parity.py        Replays all 86 recorded cases against the port
  test_mathlib.py       Hand-written unit tests + statistics-module cross-checks
  test_real_world.py    End-to-end analysis with pinned results
  example_analysis.py   The same analysis as a readable, runnable script
GETTING_STARTED.md      Installing and using Claude Code and Codex
```

## Run it yourself (about two minutes)

You need Python 3.10+ with `pytest` (`pip install pytest`; if you use
Anaconda, you already have it). Node.js is only needed if you want to
regenerate the golden vectors.

```bash
cd llm-code-translation-demo

# Run all 139 checks. pytest takes a folder, scans it recursively for
# files named test_*.py (here: test_parity.py, test_mathlib.py,
# test_real_world.py), and runs every test it finds in them.
python3 -m pytest translated-python -q

# Run the end-to-end analysis
python3 translated-python/example_analysis.py

# Optional: re-execute the original JavaScript and regenerate the vectors
node original-javascript/generate_vectors.js
```

Two experiments worth doing, because they are more convincing than any
passing run:

1. **Break the port.** Open `translated-python/mathlib.py` and change
   something subtle: make `variance` divide by `n` instead of `n - 1`, or
   change the quantile interpolation. Rerun pytest and watch the harness
   pinpoint it.
2. **Redo the translation yourself.** Delete `mathlib.py`, open Claude Code
   or Codex in this folder, and ask it to recreate the port until the test
   suite passes (prompt 3 below). This is the actual workflow, live.

## How this repo was made

Everything here, including the tests and this document, was produced by an
LLM coding agent (Claude Code) in a single session. The workflow was four
prompts, and the order matters: the verification harness is built before
the translation, so the translation has something objective to be checked
against. The same prompts work in Codex.

**Prompt 1: make the original code the oracle.**

> Here is a JavaScript math/statistics library (mathlib.js). Write a Node
> script that executes every function across a battery of inputs: typical
> values, edge cases, and invalid inputs that should throw. Record the
> inputs and the exact outputs (or the thrown error) in test_vectors.json.
> The original implementation is the source of truth.

**Prompt 2: write the contract before the port exists.**

> Write a rigorous pytest suite for a Python port of this library, before
> writing the port. Include: a parity test that replays every case in
> test_vectors.json against the port; unit tests for edge cases (empty
> input, single element, negative values, non-integer factorial, constant
> series) and for the exact exception each invalid input raises; and
> cross-checks against Python's statistics module wherever it implements
> the same quantity.

**Prompt 3: translate, and iterate until green.**

> Translate mathlib.js into idiomatic Python (snake_case, type hints,
> standard exceptions, docstrings). Do not change numerical behavior. Run
> the full test suite and keep fixing the port until every test passes.

**Prompt 4: prove it composes.**

> Write an end-to-end example that uses the library to analyze a small real
> dataset (descriptive statistics, quartiles, correlation, regression,
> prediction), plus a test that pins the final numbers. Compute the pinned
> numbers independently with the statistics module first.

The agent runs the tests itself, reads the failures itself, and fixes its
own mistakes before you ever see the result. That loop, not better
guessing, is what changed since the copy-paste-into-a-chat-window era.

## Where human judgment was still required

Translation between languages is not mechanical, and a checklist of the
judgment calls is more reassuring than a claim that there were none. The
test suite is what forces these decisions into the open:

- **Division by zero.** JavaScript returns `Infinity` for `1/0`; Python
  raises. The original library already treats it as an error, so the port
  raises `ZeroDivisionError`. The parity tests pin the behavior.
- **`power(-8, 0.5)`.** JavaScript gives `NaN`; Python's `**` operator
  silently returns a complex number. The port uses `math.pow` so a
  non-real result is an error, matching the original's contract.
- **Factorial overflow.** JavaScript's 64-bit floats overflow above `170!`.
  Python integers are exact at any size. The port keeps Python's exact
  behavior and documents the difference; the shared domain is what gets
  tested.
- **Which quantile?** The statistics literature has at least nine sampling
  quantile definitions (R's types 1 through 9). The original uses R's
  default, type 7. The tests pin that choice, so a port that quietly used
  a different convention would fail immediately.
- **JavaScript's default sort is lexicographic.** `[10, 9].sort()` stays
  `[10, 9]` unless you pass a comparator. A human translator who missed
  that would produce a median function that is wrong only on some inputs.
  The vector cases include values chosen to catch exactly this.

These are precisely the subtle semantic mismatches that make manual
translation unreliable too. The harness catches them regardless of whether
a human or a model introduces them.

## Using this workflow on your own code

Nothing here is specific to JavaScript or Python. The recipe for
"translate some code from an old language into a new one" is:

1. **If the original still runs, make it the oracle.** Have the agent write
   a harness that executes the original (R, MATLAB, Fortran, SAS, Stata,
   S-PLUS, anything with a runtime you can still invoke) over a battery of
   inputs and records the outputs to a file.
2. **Have the agent write the test suite in the target language first**,
   replaying the recorded vectors and adding edge-case tests.
3. **Then ask for the translation**, with the instruction to run the tests
   and iterate until everything passes.
4. **Review the contract, not the code.** Read the vector file and the
   tests (small, and in plain language) instead of line-by-line reviewing
   the port.

If the original no longer runs, you lose layer 1 but keep layer 2: pin the
expected behavior from documentation, published results, or a reference
implementation, and cross-check against a standard library or package that
computes the same quantities.

A prompt to start from, inside a folder containing the old code:

> This folder contains [language] code that I want ported to [language].
> First, write a test harness in [target language] that pins the current
> behavior: if the original can still be executed, run it over a thorough
> battery of inputs and record the results; otherwise pin expected results
> from [reference]. Show me the harness before translating. Then translate,
> run the tests, and iterate until everything passes. Flag any place where
> the two languages forced a semantic decision.

## Getting set up

See [GETTING_STARTED.md](GETTING_STARTED.md) for installing Claude Code and
Codex (both the desktop apps and the command-line tools), signing in, and
the auto modes worth knowing about.

## FAQ, for the appropriately skeptical

**The model is nondeterministic. How can the output be trustworthy?**
The process is nondeterministic; the artifact is not. The port either
passes 139 deterministic checks or it does not. You are not trusting a
sampling process, you are reading its output's test results. (The same
argument applies to human engineers, who are also nondeterministic.)

**Couldn't the model write tests that its own translation trivially passes?**
That is why the primary oracle is the executed original program, and the
secondary oracle is Python's standard library. Both exist outside the
model. The only way to pass the parity suite is to actually match the
original's behavior. You can also audit the 86 cases in
`test_vectors.json` yourself; they are deliberately human-readable.

**I tried this before and the translation was wrong.**
Two things likely differed. First, pasting code into a chat window gives
you a one-shot guess with no execution; an agent in a terminal runs the
code, sees the failures, and fixes them before showing you anything.
Second, the test-first ordering means a wrong translation cannot be
presented as done; it is caught mechanically, not by your eyeball.

**Do I still need to review anything?**
Yes: the contract. Skim the vector file and the tests and ask whether they
cover what you care about. That is hours less work than reviewing a port
line by line, and it is the same discipline you would want with a human
collaborator. The "judgment" section above is the kind of thing review
should focus on.

**Where does this break down?**
Coverage is the honest limit: the port is proven equivalent on the tested
behavior, not on all conceivable inputs. The mitigation is the same as in
all software engineering: make the battery dense (edge cases, error cases,
property checks like "stddev squared equals variance"), and grow it
whenever a gap is found. For numerical code, floating point tolerance
deserves explicit thought; here parity is required to about 9 significant
digits.

## Where to go next

Two features worth learning once the basic workflow feels comfortable.

**Plan mode, for anything bigger than this demo.** Translating one file
is small enough to just ask for. For a whole package, you want to agree
on the approach before any code changes: in Claude Code, press
`Shift+Tab` until you reach plan mode, and the agent becomes read-only.
It explores the codebase, proposes a step-by-step plan (which files, in
what order, how behavior will be verified), and starts editing only
after you approve. Reviewing a plan is the same kind of leverage as
reviewing the test contract: a few minutes of reading replaces hours of
watching. Other tools have the same idea; in any of them you can simply
say "propose a plan first and do not edit anything until I agree."
Docs: https://code.claude.com/docs/en/permission-modes

**Skills, for when this becomes part of your workflow.** If you find
yourself giving an agent the same instructions repeatedly (the four
prompts in this README are exactly that), you can package them once as a
skill: a folder containing a `SKILL.md` file with the instructions,
placed in `.claude/skills/` for one project or `~/.claude/skills/` to be
available everywhere. You then invoke it by name (`/translate-legacy`)
or let the agent apply it automatically when a task matches its
description. For a lab that needs to modernize old code more than once,
this is a massive time saver: the entire methodology in this repository
(vectors first, tests second, translate, iterate) becomes a single
command you run per codebase, and every student applies the same
discipline without re-explaining it. Skills follow an open standard
(https://agentskills.io) that other tools, including OpenAI's, have
adopted, so the playbook is not locked to one vendor.
Docs: https://code.claude.com/docs/en/skills
