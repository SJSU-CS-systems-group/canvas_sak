# how courses are found

nearly every command takes a course as its first argument, and the rules for what that
argument means catch people out. this page explains them, because the failure mode —
"canvas-sak says i don't teach a course i am definitely teaching" — looks like a bug and
isn't.

## it's a partial match, and it must be unique

the course argument is a **substring** of the course name, not the full name and not the
course id:

```bash
canvas-sak list-students "146"        # matches "CS 146 Section 1 Fall 2026"
```

canvas-sak then insists on exactly one match:

- **no matches** → it prints every course it *can* see and exits. that list is the
  useful part — it tells you what canvas actually returned for you.
- **more than one match** → it prints the ones that matched and exits, so you can make
  the argument more specific. it will not pick one for you.

if you teach two sections named similarly, include enough to disambiguate:

```bash
canvas-sak list-students "146 Section 1"
```

matching is case-sensitive and matches anywhere in the name.

## only courses that are running *right now*

this is the part that surprises people. by default canvas-sak only considers a course
if, at this moment:

```
start date <= now <= end date
```

so a course is invisible to the default view when:

- **the term hasn't started yet** — you're setting up next semester in advance
- **the term has ended** — you're pulling grades or reference info from a past course

both are extremely common times to reach for this tool, which is why this comes up so
often. the fix is `--inactive`:

```bash
# next semester's course, before the term begins
canvas-sak set-due-dates "CS 146 Spring" dates.txt --inactive

# last semester's course, after it ended
canvas-sak collect-reference-info "CS 146 Fall 2025" --inactive
```

`--active` (the default) and `--inactive` are available on most commands — check
[the reference](../reference/commands.md) for a specific one.

> this exact problem was a real bug: `upload-qti-quiz` had no `--inactive` flag at all,
> so you could not upload a quiz to a course whose term hadn't started — which is
> precisely when you'd want to. it was fixed in 1.1.0.

## a course with no dates set is always visible

if canvas has no start or end date for a course, canvas-sak substitutes "now" for the
missing value, so the comparison passes and the course shows up under `--active`. sandbox
and manually-created courses often have no dates and therefore always appear.

## when the list looks wrong entirely

canvas-sak only ever asks canvas for courses where you are enrolled as a **teacher**. if
a course is missing from even the `--inactive` listing, check your enrollment type in
canvas — a TA or designer enrollment won't show up.

to see what canvas-sak can see:

```bash
canvas-sak list-courses
canvas-sak list-courses --inactive
```
