# view and change quiz settings

`update-quiz` reads and writes the settings on one or many quizzes — attempts allowed,
whether students see correct answers, quiz type.

> ⚠️ **`update-quiz` has no dry run.** unlike most commands that modify canvas, this one
> applies changes the moment you run it. check the arguments before pressing enter. see
> [why almost everything is a dry run](../explanation/dry-run.md).

## look before you change

with no options, it shows the current settings rather than changing anything:

```bash
# list all quizzes in a course
canvas-sak update-quiz "My Course" --inactive

# show the settings for one quiz
canvas-sak update-quiz "My Course" "Midterm"
```

the quiz name is a partial match, like the course name.

## changing settings

```bash
# allow two attempts
canvas-sak update-quiz "My Course" "Midterm" --attempts 2

# stop showing correct answers after submission
canvas-sak update-quiz "My Course" "Final" --hide-correct-answers

# make it a practice quiz with unlimited attempts
canvas-sak update-quiz "My Course" "Practice" --quiz-type practice_quiz --attempts -1
```

## changing many quizzes at once

by default the quiz name must match exactly one quiz. `--all` applies the change to
every quiz that matches instead:

```bash
# every quiz with "Quiz" in the title gets two attempts
canvas-sak update-quiz "My Course" "Quiz" --all --attempts 2
```

with no dry run available, `--all` is the sharpest edge in this command. run it once
without any setting options first to see exactly which quizzes match.

## options

| option | effect |
|---|---|
| `--active` / `--inactive` | search active (default) or inactive courses |
| `--all` | apply to every matching quiz instead of requiring a single match |
| `--attempts N` | attempts allowed; `-1` for unlimited |
| `--view-responses [always\|once\|until_after_last_attempt\|never]` | when students can see their responses |
| `--show-correct-answers` / `--hide-correct-answers` | whether correct answers appear after submission |
| `--quiz-type [practice_quiz\|assignment\|graded_survey\|survey]` | the quiz type |

the [command reference](../reference/commands.md#update-quiz) always has the current
list, generated from the tool itself.

## related

- `update-assignment` — the equivalent for assignments, also with no dry run
- `set-fudge-points` — adjust a quiz score after the fact (this one *does* have a dry run)
- `upload-qti-quiz` — import a quiz from a qti package
