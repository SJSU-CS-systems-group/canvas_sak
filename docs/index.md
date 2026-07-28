# canvas-sak documentation

canvas-sak is a command-line tool for teachers who run their courses in canvas. it
exists because the canvas web ui makes you do the same thing thirty times in a row —
thirty due dates, thirty grade entries, thirty messages — and a terminal is much better
at "thirty times in a row" than a browser is.

## where to start

| you want to | read |
|---|---|
| set it up and run your first command | [getting started](tutorial/getting-started.md) |
| do one specific thing | the [how-to guides](#how-to-guides) below |
| understand why it behaves the way it does | [explanation](#explanation) |
| look up a command's options | [command reference](reference/commands.md) |

if you're new, read the tutorial first. it's short, and it ends with you having run a
real command against a real course without changing anything.

## how-to guides

task-oriented recipes for people who already know what they want.

- [set due dates in bulk](how-to/set-due-dates.md) — the list → edit → set round trip,
  including per-section dates
- [set up assignment groups and weights](how-to/assignment-groups.md)
- [reuse a course from a previous semester](how-to/reuse-a-course.md)
- [view and change quiz settings](how-to/update-quiz.md)
- [exclude files from processing](how-to/ignore-files.md)

## explanation

why things work the way they do. worth ten minutes before you use anything that writes
to a live course.

- [why almost everything is a dry run](explanation/dry-run.md) — and the commands that
  aren't
- [how courses are found](explanation/finding-courses.md) — why a course you're
  definitely teaching sometimes "doesn't exist"

## reference

- [every command and option](reference/commands.md) — generated from the tool itself,
  so it can't drift

## getting help

- questions: [discussions →
  q&a](https://github.com/SJSU-CS-systems-group/canvas_sak/discussions/categories/q-a)
- something's broken: [open an
  issue](https://github.com/SJSU-CS-systems-group/canvas_sak/issues/new/choose)
- something's missing from these docs: that's a bug too, please file it
