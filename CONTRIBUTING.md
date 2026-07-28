# contributing to canvas-sak

thanks for considering it. bug reports, documentation fixes, and questions are all
real contributions — you do not need to write code to be useful here.

this tool is used by teachers to manage real courses, so the bar for anything that
writes to canvas is "we understood what it would do before it did it". that shapes
most of the conventions below.

## quickest possible start

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/SJSU-CS-systems-group/canvas_sak)

that gives you python, the package installed, and pytest already set up — nothing to
install locally. it also works locally: vs code → **dev containers: reopen in
container**.

ci builds this container and runs the suite inside it on every change, so if it's
broken, that's a bug worth reporting.

## local setup

if you'd rather not use the container:

```bash
git clone https://github.com/SJSU-CS-systems-group/canvas_sak.git
cd canvas_sak
python -m venv .venv
.venv/bin/pip install -e . pytest
```

requires python 3.10 or newer and git. that's it — **you do not need a canvas
account or an api token to work on this project.** the whole test suite mocks the
canvas api, so you can develop and test offline.

you only need a real token if you want to exercise a command against a live course.
`canvas-sak help-me-setup` explains where the config file goes.

## the two commands you need

```bash
.venv/bin/pytest -q          # run the tests — 232 of them, under a second
.venv/bin/canvas-sak --help  # list the subcommands
```

there is no lint or format gate yet, so don't worry about a style check failing.
just match the style of the file you're editing.

## how the project is laid out

```
canvas_sak/canvas_sak.py    the click entry point that registers every subcommand
canvas_sak/core.py          canvas api helpers shared across commands
canvas_sak/commands/*.py    one file per subcommand
tests/test_*.py             one file per subcommand, canvas api mocked out
docs/                       tutorial / how-to / explanation / reference
scripts/                    maintenance helpers, see below
```

### docs

`docs/reference/commands.md` is **generated** — don't edit it by hand. if you add a
command or an option, regenerate it:

```bash
python scripts/gen_command_reference.py
```

ci runs the same script with `--check` and fails if the committed copy has drifted, so
the reference can't quietly fall out of date.

everything else under `docs/` is hand-written.

**a new subcommand is a new file in `canvas_sak/commands/`.** follow an existing one
— `todo.py` and `settings_navigation.py` are good models.

### releases (maintainers)

**canvas-sak ships on [pypi](https://pypi.org/project/canvas-sak/). github releases are
not used** — the tags on this repo stop at v1.1 and the release pages there are
historical only. `CHANGELOG.md` is the release notes of record, which is why prs are
asked to add an entry saying *why* a change exists.

to cut a release:

```bash
# 1. bump version in pyproject.toml
# 2. move the CHANGELOG "## Unreleased" entries under the new version + date
git commit -am "Release vX.Y.Z"
rm -rf dist/ build/           # stale artifacts here will break the upload
python -m build
twine check dist/*
twine upload dist/*
# verify what you actually published, not what you built:
python -m venv /tmp/v && /tmp/v/bin/pip install --no-cache-dir canvas-sak==X.Y.Z
cd /tmp && /tmp/v/bin/canvas-sak --version
git push
```

## two conventions that are easy to miss

**1. anything that modifies canvas must default to a dry run.**

commands that change state take a `--no-dryrun` flag. the default (`--dryrun`) prints
what *would* happen and changes nothing. this is not optional politeness — someone is
running your code against a live gradebook, and the first run should never be the
destructive one.

**2. bug fixes start with a failing test.**

the order we use:

1. reproduce the bug — actually run it and see it happen
2. add a test that fails because of it
3. fix it
4. confirm the test passes

for a new feature, same shape: write the test first, then build it. the tests are
fast and fully mocked, so this costs you very little.

## pull requests

- **say why.** the diff shows what changed; only you can explain why it should. this
  is the field reviewers care about most.
- **one concern per pr.** a focused change gets reviewed in a day; a sweeping one sits
  for weeks because nobody has a free hour.
- **include a test.** for a bug fix, a test that fails before your change and passes
  after is the clearest possible argument that you fixed it.
- **add a changelog entry.** put it under `## Unreleased` in [CHANGELOG.md](CHANGELOG.md).
  say why the change exists, not just what it does — look at the existing entries,
  they're the model.
- **flag breaking changes** explicitly, with a note on what users must do differently.
- **don't worry about a perfect first submission.** we'll review, suggest, and help.
  a pr that needs work is far more welcome than one that never gets opened.

planning something large? **open an issue first.** not bureaucracy — we would rather
talk through the approach than have you spend a weekend on a direction we can't merge.

## finding something to work on

- [good first issues](https://github.com/SJSU-CS-systems-group/canvas_sak/labels/good%20first%20issue)
  — may be empty right now; if it is, open an issue describing what you'd like to fix
  and we'll scope it with you.
- **documentation is the biggest gap.** there are 32 commands and only a handful have a
  how-to guide. writing up the one you actually use is genuinely the most valuable thing
  available, and it's the fastest way to learn the codebase.

## ai-assisted contributions

**llm-assisted contributions are welcome**, subject to the rules below. these exist
because ai-generated prs have a characteristic failure mode — enormous, confident, and
unreviewable — not because we object to the tools. much of this repo was written with
one.

1. **disclose it.** say so in the pr description. this is not a black mark; it just
   tells reviewers where to look. it is far better than us trying to deduce it from a
   diff that doesn't match your description.

2. **no blind refactors.** if an ai suggested a redesign, **you must be able to explain
   the rationale** and defend it in review. "the model suggested it" is not a rationale.
   if you can't explain it, don't submit it.

3. **keep the diff proportional.** llms tend to rewrite whole files from scratch in a
   different style, turning a three-line fix into a 400-line diff nobody can review.
   **disproportionately large diffs for small changes will be sent back** to be
   resubmitted scoped.

4. **verify it yourself.** run the tests. read the output. check that the code does
   what you think. you are the author and you are accountable for it.

5. **respect the primary author.** don't replace an existing design because a model
   proposed a different one. the current design usually reflects constraints that
   aren't visible in the file — **ask about the rationale first**, in an issue.

## how we'll treat you

- we'll say thank you. even if the report turns out to be wrong or the pr isn't
  mergeable — you spent your time on this and that counts.
- we'll explain our decisions rather than just declaring them. if we say no, you'll
  get a reason.
- we'll credit you: in [CONTRIBUTORS.md](CONTRIBUTORS.md), in the release notes for
  the version containing your work, and with `Co-authored-by:` if we build on it.
- if you contribute something substantial and it would help you, **ask us for a
  reference or a public recommendation.** we're glad to write one.

be kind, assume good faith, and we'll do the same.
