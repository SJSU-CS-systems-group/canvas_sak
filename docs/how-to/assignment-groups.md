# set up assignment groups and weights

assignment groups are how canvas turns individual scores into a course grade —
"homework is 10% of the grade, the final is 30%". `update-assignment-groups` builds them
from a plain text file.

## the file format

a group header is a line ending in `%`. every line after it, until the next header, is
an assignment that belongs to that group:

```
Assignments: 10%
Assignment1
Hard Assignment
Easy Assignment
LastAssignment

Test1: 30%
Test1

Test2: 30%

Test3: 30%
Test3
```

blank lines are ignored, so you can space it out for readability. a group with no
assignments listed under it — `Test2` above — is still created, just empty.

## applying it

```bash
# preview
canvas-sak update-assignment-groups "CS 146" groups.txt

# apply
canvas-sak update-assignment-groups "CS 146" groups.txt --no-dryrun
```

## what it checks and does

- **the weights must add up to 100%.** if they don't, it stops with an error rather than
  leaving your course half-configured.
- **a group that doesn't exist is created.**
- **an assignment that doesn't exist is reported as an error** — it won't invent one. this
  is usually a typo, or an assignment name that changed in canvas.

## seeing what you have now

running the command without a file prints your current groups in the same format, so you
can redirect it to a file, edit, and feed it back:

```bash
canvas-sak update-assignment-groups "CS 146" > groups.txt
```

check the exact arguments for your version with:

```bash
canvas-sak update-assignment-groups --help
```
