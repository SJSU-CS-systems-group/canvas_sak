# manage rubrics

view, edit, create, and attach rubrics from the terminal. rubric editing in the canvas
web ui is one small text box per rating, saved one click at a time; a rubric with five
criteria is easier to write in a text file.

everything here uses the one `rubrics` command. what it does depends on whether you
name a rubric:

| command | does |
|---|---|
| `canvas-sak rubrics "CS 146"` | list every rubric and the assignments it's attached to |
| `canvas-sak rubrics "CS 146" "Project Rubric"` | print that rubric's criteria and ratings |
| `canvas-sak rubrics "CS 146" --update-with file` | attach rubrics to assignments |
| `canvas-sak rubrics "CS 146" "Project Rubric" --update-with file` | update (or create) that rubric's criteria |

the rubric name is a partial match, like course names: `"project"` finds
`Project Rubric` as long as nothing else matches too.

## edit a rubric's criteria

the same round trip as [due dates](set-due-dates.md): the command prints exactly the
format it reads back.

```bash
# 1. dump the rubric
canvas-sak rubrics "CS 146" "Project Rubric" > rubric.txt

# 2. edit rubric.txt in any text editor

# 3. see what would change — nothing is written
canvas-sak rubrics "CS 146" "Project Rubric" --update-with rubric.txt

# 4. apply it
canvas-sak rubrics "CS 146" "Project Rubric" --update-with rubric.txt --no-dryrun
```

the update replaces the rubric's criteria with what's in the file, so the file needs to
be the whole rubric, not just the rows you changed.

## the rubric definition format

```
Project Rubric (20 pts)
* Correctness (10 pts): does the program do what the assignment asks
  - Full marks (10 pts): everything works, including edge cases
  - Partial credit (5 pts): some tests fail
  - No marks (0 pts)
* Style (10 pts)
  - Good (10 pts)
  - Needs work (0 pts)
```

- the first line is the rubric's title. the points on it are informational — canvas
  recomputes the total from the criteria.
- `*` starts a criterion, `-` starts a rating under it. indentation is optional but
  makes the file easier to read.
- after the points, an optional `: long description`. descriptions are kept to one
  line so the file stays editable.

to rename a rubric, edit the title line: the name on the command line finds the
rubric in canvas, the title in the file is what it ends up called.

## create a rubric, or copy one to another course

if the named rubric doesn't exist in the course, `--update-with` creates it. that's
also how a rubric moves between semesters:

```bash
canvas-sak rubrics "CS 146" "Project Rubric" > rubric.txt
canvas-sak rubrics "CS 146 Spring" "Project Rubric" --update-with rubric.txt --inactive --no-dryrun
```

`--inactive` because the next semester's course hasn't started yet — see
[how courses are found](../explanation/finding-courses.md). writing the file from
scratch works too; there's nothing in it the round trip has to generate.

## attach rubrics to assignments

without a rubric name, the round trip works on rubric-to-assignment associations
instead:

```bash
# 1. dump every rubric and what it's attached to
canvas-sak rubrics "CS 146" > rubrics.txt

# 2. edit: add or move "- assignment name" lines under a rubric

# 3. preview, then apply
canvas-sak rubrics "CS 146" --update-with rubrics.txt
canvas-sak rubrics "CS 146" --update-with rubrics.txt --no-dryrun
```

the association format is the rubric title line with one assignment per `-` line:

```
Project Rubric (20 pts)
  - Homework 1
  - Homework 2
Essay Rubric (15 pts)
  - Final Essay
```

assignment names match exactly first, then partially; an ambiguous name is skipped
with a warning listing the candidates. attached rubrics are set to be used for
grading.

## which format does --update-with expect?

the rubric name on the command line decides: with a name, the file is a rubric
definition; without one, it's associations. if you forget the name and hand it a
definition file, the command errors out rather than misreading ratings as assignment
names.
