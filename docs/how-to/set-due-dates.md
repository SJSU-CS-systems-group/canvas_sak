# set due dates in bulk

move every date in a course at once — the usual reason being that you're reusing last
semester's course and everything is a year out.

## the round trip

`list-due-dates` prints exactly the format `set-due-dates` reads. that's the whole
workflow:

```bash
# 1. dump what's there now
canvas-sak list-due-dates "CS 146" > dates.txt

# 2. edit dates.txt in any text editor

# 3. see what would change — nothing is written
canvas-sak set-due-dates "CS 146" dates.txt

# 4. read that output, then apply it
canvas-sak set-due-dates "CS 146" dates.txt --no-dryrun
```

step 3 is not optional politeness. a wrong year in a date file is easy to miss and
silently reschedules the whole course.

## the file format

one assignment per line: **the assignment name, a tab, then comma-separated dates.**

```
Homework 1	available=2026-01-15-09:00,due=2026-01-22-23:59
Quiz 1	due=2026-01-25-23:59,until=2026-01-25-23:59
Homework 2	due=2026-02-05-23:59
```

that separator is a real tab character, not spaces. if your editor converts tabs to
spaces, turn that off for this file.

### date types

| in the file | canvas calls it | meaning |
|---|---|---|
| `available=` | unlock at | students can see and start it from this moment |
| `due=` | due at | submissions after this are marked late |
| `until=` | lock at | no submissions accepted at all after this |

all three are optional — include only the ones you want to set.

### date format

`YYYY-MM-DD-hh:mm`, on a 24-hour clock, **in your computer's local time zone**:

```
2026-01-22-23:59      # 22 january 2026, 11:59pm local
```

canvas-sak converts to what canvas expects. if you're travelling, or your laptop is set
to a different zone from your campus, that conversion follows your laptop.

## different dates for different sections

append the section name in square brackets to give one section its own dates:

```
Quiz 1	due=2026-01-20-23:59
Quiz 1 [Evening Section]	due=2026-01-22-23:59
```

the first line sets the assignment's dates for everyone; the second creates an override
for `Evening Section` only. the section name must match the section name in canvas
exactly.

`list-due-dates` emits these override lines too, so an existing set of per-section dates
survives the round trip.

## a course that hasn't started yet

setting up next semester before the term begins is the most common time to do this, and
by default canvas-sak won't find the course:

```bash
canvas-sak set-due-dates "CS 146 Spring" dates.txt --inactive
```

see [how courses are found](../explanation/finding-courses.md).

## checking your work

`validate-course-setup` looks for assignments with no due date at all, and for
until-dates that don't line up with their due dates:

```bash
canvas-sak validate-course-setup "CS 146"
```

it also checks the links in your course content for broken or unpublished targets,
which involves real http requests and can be slow. to check only the dates:

```bash
canvas-sak validate-course-setup "CS 146" --no-check-links
```
