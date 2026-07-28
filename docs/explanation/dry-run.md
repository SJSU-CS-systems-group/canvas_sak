# why almost everything is a dry run

most canvas-sak commands that change your course do nothing the first time you run
them. that's deliberate, and it's the most important thing to understand about the
tool.

## the problem it solves

canvas-sak operates in bulk. one command can move every due date in a course, overwrite
every page, or push a letter grade to every student. the web ui makes that kind of
mistake slowly and visibly — you'd notice around the fourth wrong due date. a command
line makes it instantly and silently.

there is also no undo. canvas has no "revert my last bulk change" button. if you set 40
due dates to the wrong semester, fixing it means setting 40 due dates again, and any
student who saw the wrong one in between has already emailed you.

so the default is inverted from what you might expect: **the command shows you what it
would do, and stops.**

```bash
# shows what would change — nothing is written
canvas-sak set-due-dates "CS 146" dates.txt

# actually writes it
canvas-sak set-due-dates "CS 146" dates.txt --no-dryrun
```

the intended workflow is to run it, *read the output*, and only then re-run with
`--no-dryrun`. the dry run isn't a safety net you're meant to skip — it's the part
where you check your data file was right.

## which commands do this

16 of the 32 commands take `--dryrun/--no-dryrun`, and for those the default is always
`--dryrun`:

`archive-inbox` · `code-similarity` · `derive-assignment-score` ·
`download-course-content` · `download-submissions` · `grade-discussion` ·
`grade-submission` · `rubrics` · `set-due-dates` · `set-fudge-points` ·
`set-letter-grade` · `settings-navigation` · `todo` · `update-assignment-groups` ·
`upload-assignment-grades` · `upload-course-content`

## ⚠️ which commands do *not*

these commands write to canvas **immediately**, with no dry run and no confirmation
prompt. there is no preview step — when you press enter, it has happened:

| command | what it does the moment you run it |
|---|---|
| `message-students` | sends the message |
| `announcement create` | posts the announcement |
| `update-assignment` | edits assignment settings |
| `update-quiz` | edits quiz settings |
| `set-course-image` | changes the course image |
| `upload-qti-quiz` | starts a content migration that imports the quiz |

this is an inconsistency in the tool, not a considered exception — the project's own
convention says anything that modifies canvas should default to a dry run. until that's
fixed, treat these six as live-fire and check the arguments before pressing enter.
`message-students` in particular cannot be taken back.

if you're contributing a new command that writes to canvas, add the `--dryrun` flag —
see [CONTRIBUTING.md](../../CONTRIBUTING.md).

## a related habit

several commands accept a partial course name and refuse to run if it matches more than
one course. that's the same instinct: it would rather stop and ask than guess which
course you meant. see [how courses are found](finding-courses.md).
