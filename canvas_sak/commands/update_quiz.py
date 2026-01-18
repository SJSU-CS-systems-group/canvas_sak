from canvas_sak.core import *


def process_quiz(quiz, update_kwargs):
    """Update a single quiz and display its attributes."""
    # Update the quiz if there are changes
    if update_kwargs:
        info(f"updating quiz '{quiz.title}' with: {update_kwargs}")
        quiz = quiz.edit(quiz=update_kwargs)
        output("quiz updated successfully")
    else:
        info(f"no changes specified for '{quiz.title}', showing current settings")

    # Display quiz attributes
    output("")
    output(f"Quiz Settings: {quiz.title}")
    output(f"  Quiz Type: {getattr(quiz, 'quiz_type', 'N/A')}")
    output(f"  Points Possible: {getattr(quiz, 'points_possible', 'N/A')}")
    output(f"  Allowed Attempts: {getattr(quiz, 'allowed_attempts', 'N/A')}")
    output(f"  Time Limit: {getattr(quiz, 'time_limit', 'None')} minutes")
    output(f"  Shuffle Answers: {getattr(quiz, 'shuffle_answers', 'N/A')}")
    output(f"  Hide Results: {getattr(quiz, 'hide_results', 'None')}")
    output(f"  Show Correct Answers: {getattr(quiz, 'show_correct_answers', 'N/A')}")
    output(f"  One Time Results: {getattr(quiz, 'one_time_results', 'N/A')}")
    output(f"  Published: {getattr(quiz, 'published', 'N/A')}")
    output(f"  Question Count: {getattr(quiz, 'question_count', 'N/A')}")


@canvas_sak.command()
@click.argument('course_name', metavar='course')
@click.argument('quiz_name', metavar='quiz', default='')
@click.option('--active/--inactive', default=True, help="Search active or inactive courses")
@click.option('--all', 'process_all', is_flag=True, default=False,
              help="Process all matching quizzes instead of requiring a single match")
@click.option('--attempts', type=int, default=None,
              help="Number of attempts allowed (-1 for unlimited)")
@click.option('--view-responses', type=click.Choice(['always', 'once', 'until_after_last_attempt', 'never']),
              default=None, help="When students can view their responses")
@click.option('--show-correct-answers/--hide-correct-answers', default=None,
              help="Whether to show correct answers after submission")
@click.option('--quiz-type', type=click.Choice(['practice_quiz', 'assignment', 'graded_survey', 'survey']),
              default=None, help="The type of quiz")
def update_quiz(course_name, quiz_name, active, process_all, attempts, view_responses, show_correct_answers, quiz_type):
    """Update quiz settings and display the resulting attributes.

    Examples:

        canvas-sak update-quiz "My Course" "Midterm" --attempts 2

        canvas-sak update-quiz "My Course" "Final" --hide-correct-answers

        canvas-sak update-quiz "My Course" --inactive  # list all quizzes

        canvas-sak update-quiz "My Course" "Quiz" --all --attempts 2  # update all quizzes containing "Quiz"

        canvas-sak update-quiz "My Course" "Practice" --quiz-type practice_quiz --attempts -1
    """
    canvas = get_canvas_object()
    course = get_course(canvas, course_name, is_active=active)
    info(f"found {course.name}")

    # Get all quizzes
    all_quizzes = list(course.get_quizzes())

    # Find matching quizzes (substring match)
    if quiz_name:
        quizzes = [q for q in all_quizzes if quiz_name in q.title]
    elif process_all:
        # No quiz name but --all specified: process all quizzes
        quizzes = all_quizzes
    else:
        quizzes = []

    if len(quizzes) == 0:
        if quiz_name:
            error(f"no quizzes matched '{quiz_name}'")
        output(f"available quizzes in {course.name}:")
        for q in all_quizzes:
            output(f"    {q.title}")
        sys.exit(0 if not quiz_name else 2)

    if len(quizzes) > 1 and not process_all:
        error(f"multiple quizzes matched '{quiz_name}' (use --all to process all):")
        for q in quizzes:
            error(f"    {q.title}")
        sys.exit(2)

    # Build update kwargs
    update_kwargs = {}

    if attempts is not None:
        update_kwargs['allowed_attempts'] = attempts

    if view_responses is not None:
        # Map our option values to Canvas API values
        if view_responses == 'never':
            update_kwargs['hide_results'] = 'always'
        elif view_responses == 'once':
            update_kwargs['hide_results'] = None
            update_kwargs['one_time_results'] = True
        elif view_responses == 'until_after_last_attempt':
            update_kwargs['hide_results'] = 'until_after_last_attempt'
        else:  # always
            update_kwargs['hide_results'] = None
            update_kwargs['one_time_results'] = False

    if show_correct_answers is not None:
        update_kwargs['show_correct_answers'] = show_correct_answers

    if quiz_type is not None:
        update_kwargs['quiz_type'] = quiz_type

    # Process quizzes
    info(f"processing {len(quizzes)} quiz(es)")
    for quiz in quizzes:
        process_quiz(quiz, update_kwargs)
