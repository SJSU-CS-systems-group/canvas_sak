<!-- GENERATED FILE — do not edit by hand.
     Regenerate with: python scripts/gen_command_reference.py
     The text below comes from each command's own --help output. -->

# command reference

every canvas-sak command, straight from its `--help`. this page is generated, so it
cannot drift from the code.

this is the *reference* quadrant — it tells you what the options are, not which command
you want. if you don't know where to start, read the
[getting started tutorial](../tutorial/getting-started.md) or browse the
[how-to guides](../how-to/).

**two things that apply to almost every command:**

- commands that write to canvas default to `--dryrun`. add `--no-dryrun` to actually
  apply the change — see [why everything is a dry run](../explanation/dry-run.md).
- commands take a *partial* course name and require it to match exactly one course.
  see [how courses are found](../explanation/finding-courses.md).


## all commands

- [`announcement`](#announcement) — manage course announcements
- [`archive-inbox`](#archive-inbox) — move inbox conversations for a course to the...
- [`code-similarity`](#code-similarity) — check submissions for code similarity using...
- [`collect-reference-info`](#collect-reference-info) — collect high level information about students...
- [`derive-assignment-score`](#derive-assignment-score) — Compute assignment scores from a formula...
- [`download-course-content`](#download-course-content) — download course content from local files
- [`download-submissions`](#download-submissions) — download submissions for an assignment.
- [`export-letter-grade`](#export-letter-grade) — export course letter grade to CSV
- [`grade-discussion`](#grade-discussion) — grade a discussion assignment based on...
- [`grade-submission`](#grade-submission) — grade a student's submission for an assignment.
- [`help-me-setup`](#help-me-setup) — provide guidance through the setup process
- [`list-courses`](#list-courses) — list courses i am teaching.
- [`list-due-dates`](#list-due-dates) — List due dates for all assignments in dates...
- [`list-grades`](#list-grades) — list student ids, names, and grades for an...
- [`list-students`](#list-students) — list the students in a course
- [`message-students`](#message-students) — message students in a course
- [`min-grade-analyzer`](#min-grade-analyzer) — see what the scores would look like with...
- [`quiz`](#quiz) — get quiz logs for a student
- [`rubrics`](#rubrics) — List rubrics and their associated assignments...
- [`set-course-image`](#set-course-image) — Set or remove the course image.
- [`set-due-dates`](#set-due-dates) — Set due dates for assignments from a dates file.
- [`set-fudge-points`](#set-fudge-points) — set the fudge points for a quiz.
- [`set-letter-grade`](#set-letter-grade) — calculate the letter grade based on the final...
- [`settings-navigation`](#settings-navigation) — List and update a course's navigation menu...
- [`todo`](#todo) — list my canvas todo items (assignments to...
- [`update-assignment`](#update-assignment) — Update assignment settings and display the...
- [`update-assignment-groups`](#update-assignment-groups) — Update assignment groups and their weights...
- [`update-quiz`](#update-quiz) — Update quiz settings and display the...
- [`upload-assignment-grades`](#upload-assignment-grades) — upload grades for an assignment from a CSV file.
- [`upload-course-content`](#upload-course-content) — upload course content from local files
- [`upload-qti-quiz`](#upload-qti-quiz) — Upload a QTI quiz package to a Canvas course.
- [`validate-course-setup`](#validate-course-setup) — Validate course setup: due dates, until-date...

## announcement

```
Usage: python -m canvas_sak announcement [OPTIONS] COMMAND [ARGS]...

  manage course announcements

Options:
  --help  Show this message and exit.

Commands:
  list  list recent announcements
  post  post an announcement
```

## archive-inbox

```
Usage: python -m canvas_sak archive-inbox [OPTIONS] COURSE_SUBSTRING

  move inbox conversations for a course to the archive. the course can be a
  partial name or * for all courses.

Options:
  --dryrun / --no-dryrun  show what would be done, but don't do it
  --help                  Show this message and exit.
```

## code-similarity

```
Usage: python -m canvas_sak code-similarity [OPTIONS] course assignment
                                            language

  check submissions for code similarity using stanford MOSS.

Options:
  --dryrun / --no-dryrun      only show the grade, don't actually set it
                              [default: dryrun]
  --pause / --no-pause        pause before uploading  [default: no-pause]
  --multiple / --no-multiple  collect submissions from multiple classes
                              [default: no-multiple]
  --help                      Show this message and exit.
```

## collect-reference-info

```
Usage: python -m canvas_sak collect-reference-info [OPTIONS] COURSE

  collect high level information about students of previous classes to help
  writing reference letters

Options:
  -t threshold        assignment groups with grades about the lowest threshold
                      will have a +, the next lowest gets ++, and so on.
                      assignment groups below the lowest threshold will not be
                      printed.  [default: 84, 90, 95]
  -s skip_assignment  assignment groups with the listed keywords will not be
                      collected.  [default: iclickr, ungraded, imported]
  --help              Show this message and exit.
```

## derive-assignment-score

```
Usage: python -m canvas_sak derive-assignment-score [OPTIONS] COURSE
                                                    TARGET_ASSIGNMENT

  Compute assignment scores from a formula using other assignments.

  Assignment names in the formula use underscores for spaces and math
  operators (+ - * /). For example, an assignment named "Quiz - 1" becomes
  Quiz_1 in the formula. Consecutive spaces/operators collapse into one _.

  Scores are converted to percentages (0-100) before applying the formula.

  Available functions: min, max, sum, abs, round

  Examples:

      canvas-sak derive-assignment-score "CS101" "Average" --formula "(Quiz_1
      + Quiz_2) / 2"

      canvas-sak derive-assignment-score "CS101" "Best_Score" --formula
      "max(Midterm, Final)"

      canvas-sak derive-assignment-score "CS101" "Weighted" --formula "0.3 *
      Homework + 0.7 * Exam"

Options:
  --formula TEXT                  Formula using assignment names with _ for
                                  spaces and math operators  [required]
  --dryrun / --no-dryrun
  --use-last-assigned / --no-use-last-assigned
                                  Use the last manually-assigned score as the
                                  previous score instead of the current score
  --help                          Show this message and exit.
```

## download-course-content

```
Usage: python -m canvas_sak download-course-content [OPTIONS] course

  download course content from local files

Options:
  --dryrun / --no-dryrun          show what would happen, but don't do it.
                                  [default: dryrun]
  --modules / --no-modules        download modules to the modules file.
                                  [default: no-modules]
  --discussions / --no-discussions
                                  download discussions to the discussions
                                  subdirectory.  [default: no-discussions]
  --assignments BOOLEAN           download assignments to the assignments
                                  subdirectory.  [default: False]
  --pages / --no-pages            download pages to the pages subdirectory.
                                  [default: no-pages]
  --files BOOLEAN                 download files to the files subdirectory.
                                  [default: False]
  --announcements BOOLEAN         download announcements to the announcements
                                  subdirectory.  [default: False]
  --all / --no-all                download all content to corresponding
                                  directories  [default: no-all]
  --target TEXT                   download content parent directory.
                                  [default: .]
  --help                          Show this message and exit.
```

## download-submissions

```
Usage: python -m canvas_sak download-submissions [OPTIONS] course assignment

  download submissions for an assignment.

Options:
  --dryrun / --no-dryrun  only show the grade, don't actually set it
                          [default: dryrun]
  --help                  Show this message and exit.
```

## export-letter-grade

```
Usage: python -m canvas_sak export-letter-grade [OPTIONS] COURSE
                                                CSV_OUTPUT_FILE

  export course letter grade to CSV

  the "Reported Letter Grade" column must be setup in the gradebook. this
  command will pull down the letter grades from that column an print a CSV
  record with the student id and the corresponding letter grade. output will
  got to the indicated csv_output_file. an output file name of - will go to
  stdout.

Options:
  --help  Show this message and exit.
```

## grade-discussion

```
Usage: python -m canvas_sak grade-discussion [OPTIONS] course assignment

  grade a discussion assignment based on participation.

  one point is added for a post and another for a reply for a total of 2. this
  tool assumes that the student must post first to reply.

  course_name - any part of an active course name. for example, 249 will match
  CS249. the course must active (it has not passed the end date) to be
  eligible for matching. only the first match will be used.

  assignment_name - any part of an assigment's name will be matched. only the
  first match will be used.

Options:
  --dryrun / --no-dryrun    only show the grade, don't actually set it
                            [default: dryrun]
  --min-words INTEGER       the minimum number of valid words to get credit
                            [default: 5]
  --points-comment INTEGER  number of points for posting a comment  [default:
                            1]
  --max-points INTEGER      maximum number of points to give  [default: 2]
  --help                    Show this message and exit.
```

## grade-submission

```
Usage: python -m canvas_sak grade-submission [OPTIONS] course assignment

  grade a student's submission for an assignment.

  assigns the specified grade and posts a submission comment. optionally
  attaches a file to the comment.

  use --grade -1 to clear an existing grade.

  use --delete-previous to remove your prior comments and attachments before
  posting the new grade and comment.

  course - any part of an active course name. for example, 249 will match
  CS249.

  assignment - any part of an assignment's name will be matched. only one
  match is allowed.

Options:
  --canvasid INTEGER      the canvas user id of the student
  --sisid TEXT            the SIS user id of the student
  --grade TEXT            the grade to assign (-1 to unset)  [required]
  --message TEXT          submission comment to post  [required]
  --attachment PATH       file to attach to the submission comment
  --delete-previous       delete previous comments and attachments from you
                          before grading
  --only-changes          skip the update if the new grade matches the current
                          grade
  --dryrun / --no-dryrun  show what would happen, but don't do it  [default:
                          dryrun]
  --help                  Show this message and exit.
```

## help-me-setup

```
Usage: python -m canvas_sak help-me-setup [OPTIONS]

  provide guidance through the setup process

Options:
  --help  Show this message and exit.
```

## list-courses

```
Usage: python -m canvas_sak list-courses [OPTIONS]

  list courses i am teaching. --inactive will include past and future courses.

Options:
  --active / --inactive           show only active courses
  --matcher match_re_expression   course name regular expressions matcher
                                  [default: ((\S*): (\S+)\s.*)]
  --formatter format_re_expression
                                  course name regular expressions formatter
                                  based on the matcher pattern. a format
                                  pattern of - will turn off formatting.
                                  [default: \2:\3]
  --help                          Show this message and exit.
```

## list-due-dates

```
Usage: python -m canvas_sak list-due-dates [OPTIONS] course

  List due dates for all assignments in dates file format.

  Output format: assignment name TAB comma-separated dates

  Each date is type=YYYY-MM-DD-hh:mm where type is available, due, or until.

  Assignments with section overrides show the base dates first, then each
  override on a separate line with the section name in brackets.

  Example:     Homework 1      available=2024-01-15-09:00,due=2024-01-22-23:59
  Quiz 1  due=2024-01-20-23:59     Quiz 1 [Section A]
  due=2024-01-22-23:59

Options:
  --active / --inactive  show only active courses
  --help                 Show this message and exit.
```

## list-grades

```
Usage: python -m canvas_sak list-grades [OPTIONS] COURSE ASSIGNMENT

  list student ids, names, and grades for an assignment.

  course - any part of an active course name.

  assignment - any part of an assignment's name.

Options:
  --name TEXT            filter to students whose name contains this substring
                         (case-insensitive)
  --id TEXT              filter to the student with this login id
  --rubric               include rubric criterion scores alongside the grade
  --active / --inactive  match only active courses
  --help                 Show this message and exit.
```

## list-students

```
Usage: python -m canvas_sak list-students [OPTIONS] COURSE

  list the students in a course

Options:
  --active / --inactive   show only active courses
  --emails / --no-emails  list student emails
  --id / --no-id          include the canvas id
  --link TEXT             show value of a link field (* for everything)
  --help                  Show this message and exit.
```

## message-students

```
Usage: python -m canvas_sak message-students [OPTIONS] COURSE SUBJECT
                                             STUDENTS...

  message students in a course

Options:
  --course-in-subject / --no-course-in-subject
                                  include the course name in []s in the
                                  subject line  [default: course-in-subject]
  --message TEXT                  message to send
  --from-file FILENAME            file containing message to send (- for
                                  stdin)
  --help                          Show this message and exit.
```

## min-grade-analyzer

```
Usage: python -m canvas_sak min-grade-analyzer [OPTIONS] COURSE

  see what the scores would look like with minimum grade

Options:
  -m FLOAT  the minimum assignment grade. any score below this grade will be
            set to this minimum score.  [default: 50.0]
  --help    Show this message and exit.
```

## quiz

```
Usage: python -m canvas_sak quiz [OPTIONS] course quiz

  get quiz logs for a student

Options:
  --show-question / --no-show-question
                                  [default: no-show-question]
  --for-student students          students to get quiz logs for
  --summarize / --no-summarize    show only completed answers. skip answers
                                  that are a prefix of subsequent answers
                                  [default: summarize]
  --final-answer / --no-final-answer
                                  show the final answer, if --no-final-answer,
                                  the final answers will be skipped  [default:
                                  final-answer]
  --help                          Show this message and exit.
```

## rubrics

```
Usage: python -m canvas_sak rubrics [OPTIONS] COURSE

  List rubrics and their associated assignments for a course.

  COURSE is a partial course name to match.

  Examples:

      canvas-sak rubrics "CS101"

      canvas-sak rubrics "CS101" --update-with rubrics.txt --no-dryrun

Options:
  --active / --inactive   match only active courses
  --update-with FILENAME  File with rubric assignments to apply (same format
                          as output)
  --dryrun / --no-dryrun  Only show what would be changed
  --help                  Show this message and exit.
```

## set-course-image

```
Usage: python -m canvas_sak set-course-image [OPTIONS] course image

  Set or remove the course image.

  IMAGE can be a local file path or a URL. If it's a local file, it will be
  uploaded to Canvas first. If it's a URL, it will be set directly.

  Examples:

      canvas-sak set-course-image "My Course" ./banner.jpg

      canvas-sak set-course-image "My Course" https://example.com/image.jpg

      canvas-sak set-course-image "My Course" --remove

Options:
  --remove  remove the course image instead of setting it
  --help    Show this message and exit.
```

## set-due-dates

```
Usage: python -m canvas_sak set-due-dates [OPTIONS] course DATES_FILE

  Set due dates for assignments from a dates file.

  Input format: assignment name TAB comma-separated dates

  Each date is type=YYYY-MM-DD-hh:mm where type is available, due, or until.

  For section-specific dates, append the section name in brackets:

      Quiz 1  due=2024-01-20-23:59     Quiz 1 [Section A]
      due=2024-01-22-23:59

  Examples:

      Homework 1      available=2024-01-15-09:00,due=2024-01-22-23:59

      Quiz 1 [Evening Section]        due=2024-01-25-23:59

Options:
  --active / --inactive   show only active courses
  --dryrun / --no-dryrun  show what would happen, but don't do it  [default:
                          dryrun]
  --help                  Show this message and exit.
```

## set-fudge-points

```
Usage: python -m canvas_sak set-fudge-points [OPTIONS] COURSE_NAME [QUIZ_NAME]
                                             [POINTS]

  set the fudge points for a quiz.

  course_name - any part of an active course name. for example, 249 will match
  CS249. the course must active (it has not passed the end date) to be
  eligible for matching. only the first match will be used.

  quiz_name - any part of an quiz's name will be matched. if multiple quizes
  match, the points will not be set.

Options:
  --dryrun / --no-dryrun      only show the grade, don't actually set it
                              [default: dryrun]
  --decrease / --no-decrease  If not true, the fudge points will not be
                              updated if new points < old points.  [default:
                              no-decrease]
  --help                      Show this message and exit.
```

## set-letter-grade

```
Usage: python -m canvas_sak set-letter-grade [OPTIONS] COURSE

  calculate the letter grade based on the final score in the class.

  the "Reported Letter Grade" assignment must be created in the gradebook as a
  letter grade assignment before this command is run. the command will loop
  through all the students in the class and set the letter grade in that
  assignment based on the final score in the class.

Options:
  --round FLOAT                   points to add to the final score before
                                  calculating the letter grade.
  --dryrun / --no-dryrun
  --skip-mismatch / --no-skip-mismatch
                                  do not set letter grade for current grades
                                  that don't match total
  --help                          Show this message and exit.
```

## settings-navigation

```
Usage: python -m canvas_sak settings-navigation [OPTIONS] COMMAND [ARGS]...

  List and update a course's navigation menu (Settings > Navigation).

Options:
  --help  Show this message and exit.

Commands:
  list    List the visible and hidden navigation items for a course.
  update  Make the given navigation ITEMs visible and hide the rest.
```

## todo

```
Usage: python -m canvas_sak todo [OPTIONS]

  list my canvas todo items (assignments to grade or submit).

Options:
  --remove FILENAME       file with todo items to permanently ignore (same
                          tab-separated format as output)
  --dryrun / --no-dryrun  dryrun mode for --remove  [default: dryrun]
  --upcoming              show assignments due or locking within the next 10
                          days
  --recent-past           show assignments that were due or locked in the last
                          10 days
  --help                  Show this message and exit.
```

## update-assignment

```
Usage: python -m canvas_sak update-assignment [OPTIONS] course assignment

  Update assignment settings and display the resulting attributes.

  Examples:

      canvas-sak update-assignment "My Course" "Homework 1" --points 100

      canvas-sak update-assignment "My Course" "Essay" --submission-types
      online_upload,online_text_entry

      canvas-sak update-assignment "My Course" --inactive  # list all
      assignments

      canvas-sak update-assignment "My Course" "Lab" --all --published  #
      publish all assignments containing "Lab"

      canvas-sak update-assignment "My Course" "Final" --grading-type
      letter_grade --omit-from-final-grade

      canvas-sak update-assignment "My Course" "New Assignment" --create
      --points 50  # create if not exists

      canvas-sak update-assignment "My Course" "Lab" --assignment-group "Labs"
      --all --published  # publish all "Lab" assignments in groups matching
      "Labs"

Options:
  --active / --inactive           Search active or inactive courses
  --all                           Process all matching assignments instead of
                                  requiring a single match
  --create                        Create the assignment if it does not exist
                                  (requires exact assignment name)
  --points FLOAT                  Points possible
  --published / --unpublished     Publish or unpublish the assignment
  --submission-types TEXT         Comma-separated submission types: online_upl
                                  oad,online_text_entry,online_url,media_recor
                                  ding,none,on_paper,external_tool,online_quiz
  --grading-type [points|percent|letter_grade|gpa_scale|pass_fail|not_graded]
                                  Grading type
  --attempts INTEGER              Number of attempts allowed (-1 for
                                  unlimited)
  --allowed-extensions TEXT       Comma-separated file extensions (e.g.,
                                  pdf,docx)
  --omit-from-final-grade / --include-in-final-grade
                                  Omit or include assignment in final grade
  --peer-reviews / --no-peer-reviews
                                  Enable or disable peer reviews
  --assignment-group TEXT         Only process assignments whose assignment
                                  group name contains this substring
  --description TEXT              Assignment description (HTML supported)
  --help                          Show this message and exit.
```

## update-assignment-groups

```
Usage: python -m canvas_sak update-assignment-groups [OPTIONS] course
                                                     [GROUPS_FILE]

  Update assignment groups and their weights from a file.

  If no file is specified, prints the current assignment groups in the file
  format.

  The file format is:

      GROUP_NAME: WEIGHT%     assignment1     assignment2

      ANOTHER_GROUP: WEIGHT%     assignment3

  Examples:

      canvas-sak update-assignment-groups "My Course"  # print current groups

      canvas-sak update-assignment-groups "My Course" groups.txt

      canvas-sak update-assignment-groups "My Course" groups.txt --no-dryrun

Options:
  --active / --inactive   search active or inactive courses
  --dryrun / --no-dryrun  show what would happen, but don't do it  [default:
                          dryrun]
  --help                  Show this message and exit.
```

## update-quiz

```
Usage: python -m canvas_sak update-quiz [OPTIONS] course quiz

  Update quiz settings and display the resulting attributes.

  Examples:

      canvas-sak update-quiz "My Course" "Midterm" --attempts 2

      canvas-sak update-quiz "My Course" "Final" --hide-correct-answers

      canvas-sak update-quiz "My Course" --inactive  # list all quizzes

      canvas-sak update-quiz "My Course" "Quiz" --all --attempts 2  # update
      all quizzes containing "Quiz"

      canvas-sak update-quiz "My Course" "Practice" --quiz-type practice_quiz
      --attempts -1

Options:
  --active / --inactive           Search active or inactive courses
  --all                           Process all matching quizzes instead of
                                  requiring a single match
  --attempts INTEGER              Number of attempts allowed (-1 for
                                  unlimited)
  --view-responses [always|once|until_after_last_attempt|never]
                                  When students can view their responses
  --show-correct-answers / --hide-correct-answers
                                  Whether to show correct answers after
                                  submission
  --quiz-type [practice_quiz|assignment|graded_survey|survey]
                                  The type of quiz
  --help                          Show this message and exit.
```

## upload-assignment-grades

```
Usage: python -m canvas_sak upload-assignment-grades [OPTIONS] COURSE
                                                     ASSIGNMENT

  upload grades for an assignment from a CSV file.

Options:
  --file FILENAME         [required]
  --id TEXT               field number (0-based) in the file that contains the
                          ID  [required]
  --grade TEXT            field number (0-based) in the file that contains the
                          grade  [required]
  --free-points FLOAT     points to add to the score.
  --dryrun / --no-dryrun
  --help                  Show this message and exit.
```

## upload-course-content

```
Usage: python -m canvas_sak upload-course-content [OPTIONS] course

  upload course content from local files

Options:
  --dryrun / --no-dryrun          show what would happen, but don't do it.
                                  [default: dryrun]
  --modules / --no-modules        upload modules to the modules subdirectory.
                                  [default: no-modules]
  --discussions / --no-discussions
                                  upload discussions to the discussions
                                  subdirectory.  [default: no-discussions]
  --assignments BOOLEAN           upload assignments to the assignments
                                  subdirectory.  [default: False]
  --pages / --no-pages            upload pages to the pages subdirectory.
                                  [default: no-pages]
  --files / --no-files            upload files to the files subdirectory.
                                  [default: no-files]
  --announcements BOOLEAN         upload announcements to the announcements
                                  subdirectory.  [default: False]
  --all / --no-all                upload all content to corresponding
                                  directories  [default: no-all]
  --source TEXT                   upload content parent directory.  [default:
                                  .]
  --force / --no-force            overwrite existing content  [default: no-
                                  force]
  --help                          Show this message and exit.
```

## upload-qti-quiz

```
Usage: python -m canvas_sak upload-qti-quiz [OPTIONS] course QTI_FILE

  Upload a QTI quiz package to a Canvas course.

  QTI_FILE should be a zip file containing a QTI-formatted quiz.

Options:
  --active / --inactive    Search active or inactive courses
  --wait / --no-wait       wait for the import to complete  [default: wait]
  --poll-interval INTEGER  seconds between status checks when waiting
                           [default: 2]
  --help                   Show this message and exit.
```

## validate-course-setup

```
Usage: python -m canvas_sak validate-course-setup [OPTIONS] course

  Validate course setup: due dates, until-date consistency, and links.

  Checks all courses matching COURSE for common setup issues.

  Examples:

      canvas-sak validate-course-setup "CS 146"

      canvas-sak validate-course-setup "CS 146" --no-check-links

      canvas-sak validate-course-setup "CS 146" --no-external-links

Options:
  --active / --inactive           show only active courses
  --check-links / --no-check-links
                                  check for broken/unpublished links
                                  [default: check-links]
  --check-dates / --no-check-dates
                                  check for missing due dates  [default:
                                  check-dates]
  --check-until / --no-check-until
                                  check until-date consistency  [default:
                                  check-until]
  --external-links / --no-external-links
                                  check external links (HTTP requests)
                                  [default: external-links]
  --timeout INTEGER               timeout in seconds for external link checks
                                  [default: 10]
  --help                          Show this message and exit.
```
