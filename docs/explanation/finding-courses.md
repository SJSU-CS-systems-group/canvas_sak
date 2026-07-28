# how courses are found

nearly every command takes a course as its first argument. canvas course names are long
— term, department, course number, and section all run together, like
`FA26:CMPE-30 Section 01` — and typing that out every time, exactly right, to list your
students would be miserable.

so you don't have to. give canvas-sak **any fragment of the name that identifies one
course**, and it works out which one you meant:

```bash
canvas-sak list-students "CMPE-30"      # matches FA26:CMPE-30 Section 01
```

the rest of this page is what "identifies one course" means in practice, and why a
course you are definitely teaching sometimes appears not to exist.

## it's a partial match, and it must be unique

the argument is a **substring** of the course name — not the full name, and not the
course id.

canvas-sak then insists on exactly one match:

- **no matches** → it prints every course it *can* see and exits. that list is the
  useful part — it tells you what canvas actually returned for you.
- **more than one match** → it prints the ones that matched and exits, so you can make
  the argument more specific. it will not pick one for you.

when two of your courses share a fragment — two sections of the same class, typically —
include enough to tell them apart:

```bash
canvas-sak list-students "CMPE-30 Section 01"
```

matching is case-sensitive and matches anywhere in the name.

## only courses that are running *right now*

a name fragment only searches the courses canvas-sak is currently looking at, and by
default that is the courses running right now:

```
start date <= now <= end date
```

teaching a course is mostly a present-tense activity, so that default keeps a decade of
old sections out of every listing. but two of the most useful times to reach for this
tool fall outside it:

- **the term hasn't started yet** — you're setting up next semester in advance
- **the term has ended** — you're pulling grades or reference info from a past course

for those, ask for the inactive ones with `--inactive`:

```bash
# next semester's course, before the term begins
canvas-sak set-due-dates "CMPE-30" dates.txt --inactive

# last semester's course, after it ended
canvas-sak collect-reference-info "CMPE-172" --inactive
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
