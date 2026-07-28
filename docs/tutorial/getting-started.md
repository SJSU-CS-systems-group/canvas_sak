# getting started

by the end of this page you'll have canvas-sak installed, talking to your canvas
account, and you'll have run a real command against one of your real courses — without
changing anything in it.

it takes about ten minutes, most of which is canvas's settings page.

## 1. install it

```bash
pip install canvas-sak
```

if you'd rather keep it out of your main python environment — a good idea for a tool
you'll run for years — use [pipx](https://pipx.pypa.io) or
[uv](https://docs.astral.sh/uv/) instead:

```bash
pipx install canvas-sak
# or
uv tool install canvas-sak
```

check it landed:

```bash
canvas-sak --version
```

## 2. get a canvas token

canvas-sak talks to canvas as *you*, using an access token you generate.

1. open canvas in a browser
2. click **account** in the top left
3. click **settings**
4. scroll to **approved integrations** and click **+ new access token**
5. give it a purpose (`canvas-sak`) and leave the expiry blank, or set one you'll
   remember to renew
6. click **generate token**

**copy the token now.** canvas shows it exactly once and you cannot retrieve it later —
if you lose it, delete the token and make another.

> treat this token like your password. it can do anything to your courses that you can,
> including things with no undo. don't paste it into a chat, a bug report, or a git
> repository. if you ever do, go back to that settings page and delete it immediately.

## 3. tell canvas-sak about it

canvas-sak reads a config file. ask it where that file should live:

```bash
canvas-sak help-me-setup
```

it will tell you the exact path for your machine — typically
`~/.config/canvas_sak.ini` on linux, `~/Library/Application Support/canvas_sak.ini` on
macos — and print the format it expects.

create that file with this content:

```ini
[SERVER]
url=https://YOURSCHOOL.instructure.com
token=YOUR_TOKEN_HERE
```

`YOURSCHOOL` is your institution's canvas hostname — the one already in your browser's
address bar when you're in canvas.

if you plan to use `code-similarity` later, you'll also want a
[moss](https://theory.stanford.edu/~aiken/moss/) user id in the same file:

```ini
[MOSS]
userid=YOUR_MOSS_ID
```

now run the check again:

```bash
canvas-sak help-me-setup
```

it should confirm the file exists, that your canvas server is reachable, that the token
works, and greet you by name. if any step fails it tells you which one — work through
them in order.

## 4. see your courses

```bash
canvas-sak list-courses
```

you should see the courses you're currently teaching.

**if the list is empty or missing a course**, that's expected rather than broken:
canvas-sak only shows courses that are running *right now*. for a course that hasn't
started or has already ended:

```bash
canvas-sak list-courses --inactive
```

[how courses are found](../explanation/finding-courses.md) covers the full rule, and how
to name a course without typing all of it.

## 5. run a read-only command

pick a course from that list. you don't need its full name — any distinctive piece will
do, as long as it matches only one course:

```bash
canvas-sak list-students "146"
```

that's a substring match. if it matches several courses canvas-sak will list them and
stop rather than guess; add more of the name until it's unique.

want emails too?

```bash
canvas-sak list-students "146" --emails
```

## 6. run a command that *would* change something

here's the part worth internalising. list the due dates in your course:

```bash
canvas-sak list-due-dates "146"
```

you'll get one assignment per line, a tab, then its dates:

```
Homework 1	available=2026-01-15-09:00,due=2026-01-22-23:59
Quiz 1	due=2026-01-25-23:59
```

save that to a file, and feed it straight back:

```bash
canvas-sak list-due-dates "146" > dates.txt
canvas-sak set-due-dates "146" dates.txt
```

**nothing happened to your course.** `set-due-dates` printed what it *would* do and
stopped, because commands that modify canvas default to a dry run. to actually apply a
change you add `--no-dryrun`:

```bash
canvas-sak set-due-dates "146" dates.txt --no-dryrun    # don't run this yet
```

since `dates.txt` is exactly what canvas already has, that would be a no-op — but the
habit is the point. run it, read the output, *then* add `--no-dryrun`.

be aware that six commands don't work this way and write immediately. [why almost
everything is a dry run](../explanation/dry-run.md) lists them.

## where to go next

- [set due dates in bulk](../how-to/set-due-dates.md) — the workflow you just previewed,
  including per-section dates
- [reuse a course from a previous semester](../how-to/reuse-a-course.md)
- [every command and option](../reference/commands.md)

or just run `canvas-sak --help` and read the list. most of the commands do what their
name suggests.
