# canvas_sak - canvas Swiss-Army-Knife
a command-line python based tool for teachers who use canvas. 

you can download from Pypi.
just `pip install canvas-sak`.

you will need to grab a "token" from your canvas account. go to the canvas webpage -> click on Account in the upper left -> click Settings -> scroll down and click the New Access Token button. you will need to put the token in a configuration file. `canvas-sak help-me-setup` will tell you how and where to create that configuration file.

some of the major functions:

* code-similarity: download program submissions and run them through stanford MOSS.
* collect-reference-info: collect high level information about student for when they later ask for letters of recommendation.
* download-submissions: the the submissions of an assignment.
* download/upload-course-content: download and upload course content as markdown files for easily reusing past courses in a way that is easy to change.
* message-students: send a canvas messages to students from the commandline
* list/set-due-dates: list and set due dates for assignments all at once
* update-quiz: view and update quiz settings (attempts, view responses, show correct answers, quiz type)

# update-quiz

View and update quiz settings for one or more quizzes in a course.

## Options

* `--active/--inactive`: search active (default) or inactive courses
* `--all`: process all matching quizzes instead of requiring a single match
* `--attempts INTEGER`: number of attempts allowed (-1 for unlimited)
* `--view-responses [always|once|until_after_last_attempt|never]`: when students can view their responses
* `--show-correct-answers/--hide-correct-answers`: whether to show correct answers after submission
* `--quiz-type [practice_quiz|assignment|graded_survey|survey]`: the type of quiz

## Examples

```bash
# List all quizzes in a course
canvas-sak update-quiz "My Course" --inactive

# View settings for a specific quiz
canvas-sak update-quiz "My Course" "Midterm"

# Set attempts to 2 for a quiz
canvas-sak update-quiz "My Course" "Midterm" --attempts 2

# Hide correct answers
canvas-sak update-quiz "My Course" "Final" --hide-correct-answers

# Update all quizzes containing "Quiz" in the title
canvas-sak update-quiz "My Course" "Quiz" --all --attempts 2

# Make a quiz a practice quiz with unlimited attempts
canvas-sak update-quiz "My Course" "Practice" --quiz-type practice_quiz --attempts -1
```

# Ignore files pattern

* canvas_sak will search for ignore patterns from the canvas_sak configuration file in the [IGNORE] section.
* if there is a `canvas-sak-ignore.lst` file in the current directory, it will use patterns in that file as well.
* canvas_sak will avoid processing files that match the ignore patterns.
* the patterns are the same format at gitignore patterns.

# Assignment Group files

    ASSIGNMENT_GROUP_NAME: WEIGHT_PERCENTAGE
    ASSIGNMENT_NAME
    ASSIGNMENT_NAME

## Example Group File

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

## Validations

- Make sure the the weights add up to 100%. Halt with an error if it does not
- If the Assignment group does not exist, create the group
- If the Assignment doesn't exist, print an error
- Print what would happen, but don't actually do it if the --no-dryrun is not used
