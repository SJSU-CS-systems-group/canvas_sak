# canvas-sak — the canvas swiss army knife

[![CI](https://github.com/SJSU-CS-systems-group/canvas_sak/actions/workflows/ci.yml/badge.svg)](https://github.com/SJSU-CS-systems-group/canvas_sak/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/canvas-sak)](https://pypi.org/project/canvas-sak/)
[![License](https://img.shields.io/github/license/SJSU-CS-systems-group/canvas_sak)](LICENSE)

**do the repetitive parts of teaching in canvas from your terminal — 32 commands for the
things the web ui makes you click thirty times.** every command that changes your course
shows you what it would do first, and stops.

```bash
# reschedule an entire course for the new semester
canvas-sak list-due-dates "CS 146" > dates.txt   # dump every date
$EDITOR dates.txt                                # fix the year, shift a week
canvas-sak set-due-dates "CS 146" dates.txt      # preview — nothing is written yet
canvas-sak set-due-dates "CS 146" dates.txt --no-dryrun
```

also: pull a whole course down as markdown and push it into next semester's shell,
run submissions through stanford moss, message every student, bulk-set letter grades,
and collect the information you'll want when someone asks for a recommendation letter
two years from now.

▶️ **[see what every command does, without installing anything](docs/reference/commands.md)** —
generated from the tool itself

---

## install

```bash
pip install canvas-sak
```

or, to keep it out of your main python environment:

```bash
pipx install canvas-sak      # or: uv tool install canvas-sak
```

needs python 3.10+. then run `canvas-sak help-me-setup`, which walks you through
creating a canvas access token and tells you exactly where to put it.

to upgrade later: `pip install --upgrade canvas-sak`.

every version ships to [pypi](https://pypi.org/project/canvas-sak/) — that's the place
to get it, not this repo's releases tab, which is historical. what changed in each
version is in [CHANGELOG.md](CHANGELOG.md).

## documentation

- **[getting started](docs/tutorial/getting-started.md)** — install to first real command,
  about ten minutes
- **[how-to guides](docs/index.md#how-to-guides)** — due dates, assignment groups, reusing
  a course, quiz settings, ignore patterns
- **[explanation](docs/index.md#explanation)** — [why almost everything is a dry
  run](docs/explanation/dry-run.md), and [how courses are
  found](docs/explanation/finding-courses.md) (read this one when a course you're
  definitely teaching "doesn't exist")
- **[command reference](docs/reference/commands.md)** — all 32 commands and their options

## contributing

contributions are welcome — see **[CONTRIBUTING.md](CONTRIBUTING.md)**.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/SJSU-CS-systems-group/canvas_sak)

that gives you a working dev environment with nothing to install. the test suite mocks
the canvas api, so you can develop without a canvas account or a token.

documentation is the biggest gap right now and is a genuinely valuable place to start —
see the [good first
issues](https://github.com/SJSU-CS-systems-group/canvas_sak/labels/good%20first%20issue).

## community

- **[discussions](https://github.com/SJSU-CS-systems-group/canvas_sak/discussions)** —
  questions, ideas, and show-and-tell
- **[using this to run a real course?](https://github.com/SJSU-CS-systems-group/canvas_sak/issues/new?template=production_experience.yml)**
  please tell us. the issue tracker only ever hears from people something broke for, so
  without this we have no idea whether anyone is out there.
- **[report a bug](https://github.com/SJSU-CS-systems-group/canvas_sak/issues/new/choose)**
  — please redact student names and ids

## license

released into the public domain under the [Unlicense](LICENSE).
