from canvas_sak.core import *


def process_assignment(assignment, update_kwargs):
    """Update a single assignment and display its attributes."""
    if update_kwargs:
        info(f"updating assignment '{assignment.name}' with: {update_kwargs}")
        assignment.edit(assignment=update_kwargs)
        output("assignment updated successfully")
    else:
        info(f"no changes specified for '{assignment.name}', showing current settings")

    # Display assignment attributes
    output("")
    output(f"Assignment Settings: {assignment.name}")
    output(f"  Points Possible: {getattr(assignment, 'points_possible', 'N/A')}")
    output(f"  Submission Types: {getattr(assignment, 'submission_types', 'N/A')}")
    output(f"  Grading Type: {getattr(assignment, 'grading_type', 'N/A')}")
    output(f"  Published: {getattr(assignment, 'published', 'N/A')}")
    output(f"  Allowed Attempts: {getattr(assignment, 'allowed_attempts', 'N/A')}")
    output(f"  Allowed Extensions: {getattr(assignment, 'allowed_extensions', 'N/A')}")
    output(f"  Omit From Final Grade: {getattr(assignment, 'omit_from_final_grade', 'N/A')}")
    output(f"  Peer Reviews: {getattr(assignment, 'peer_reviews', 'N/A')}")
    output(f"  Due At: {getattr(assignment, 'due_at', 'N/A')}")
    output(f"  Unlock At: {getattr(assignment, 'unlock_at', 'N/A')}")
    output(f"  Lock At: {getattr(assignment, 'lock_at', 'N/A')}")
    output(f"  Assignment Group: {getattr(assignment, 'assignment_group_id', 'N/A')}")


@canvas_sak.command()
@click.argument('course_name', metavar='course')
@click.argument('assignment_name', metavar='assignment', default='')
@click.option('--active/--inactive', default=True, help="Search active or inactive courses")
@click.option('--all', 'process_all', is_flag=True, default=False,
              help="Process all matching assignments instead of requiring a single match")
@click.option('--points', type=float, default=None,
              help="Points possible")
@click.option('--published/--unpublished', default=None,
              help="Publish or unpublish the assignment")
@click.option('--submission-types', default=None,
              help="Comma-separated submission types: online_upload,online_text_entry,online_url,media_recording,none,on_paper,external_tool,online_quiz")
@click.option('--grading-type', type=click.Choice(['points', 'percent', 'letter_grade', 'gpa_scale', 'pass_fail', 'not_graded']),
              default=None, help="Grading type")
@click.option('--attempts', type=int, default=None,
              help="Number of attempts allowed (-1 for unlimited)")
@click.option('--allowed-extensions', default=None,
              help="Comma-separated file extensions (e.g., pdf,docx)")
@click.option('--omit-from-final-grade/--include-in-final-grade', default=None,
              help="Omit or include assignment in final grade")
@click.option('--peer-reviews/--no-peer-reviews', default=None,
              help="Enable or disable peer reviews")
def update_assignment(course_name, assignment_name, active, process_all, points,
                      published, submission_types, grading_type, attempts,
                      allowed_extensions, omit_from_final_grade, peer_reviews):
    """Update assignment settings and display the resulting attributes.

    Examples:

        canvas-sak update-assignment "My Course" "Homework 1" --points 100

        canvas-sak update-assignment "My Course" "Essay" --submission-types online_upload,online_text_entry

        canvas-sak update-assignment "My Course" --inactive  # list all assignments

        canvas-sak update-assignment "My Course" "Lab" --all --published  # publish all assignments containing "Lab"

        canvas-sak update-assignment "My Course" "Final" --grading-type letter_grade --omit-from-final-grade
    """
    canvas = get_canvas_object()
    course = get_course(canvas, course_name, is_active=active)
    info(f"found {course.name}")

    # Get all assignments
    all_assignments = list(course.get_assignments())

    # Find matching assignments (substring match)
    if assignment_name:
        assignments = [a for a in all_assignments if assignment_name in a.name]
    elif process_all:
        # No assignment name but --all specified: process all assignments
        assignments = all_assignments
    else:
        assignments = []

    if len(assignments) == 0:
        if assignment_name:
            error(f"no assignments matched '{assignment_name}'")
        output(f"available assignments in {course.name}:")
        for a in all_assignments:
            output(f"    {a.name}")
        sys.exit(0 if not assignment_name else 2)

    if len(assignments) > 1 and not process_all:
        error(f"multiple assignments matched '{assignment_name}' (use --all to process all):")
        for a in assignments:
            error(f"    {a.name}")
        sys.exit(2)

    # Build update kwargs
    update_kwargs = {}

    if points is not None:
        update_kwargs['points_possible'] = points

    if published is not None:
        update_kwargs['published'] = published

    if submission_types is not None:
        update_kwargs['submission_types'] = [s.strip() for s in submission_types.split(',')]

    if grading_type is not None:
        update_kwargs['grading_type'] = grading_type

    if attempts is not None:
        update_kwargs['allowed_attempts'] = attempts

    if allowed_extensions is not None:
        update_kwargs['allowed_extensions'] = [e.strip() for e in allowed_extensions.split(',')]

    if omit_from_final_grade is not None:
        update_kwargs['omit_from_final_grade'] = omit_from_final_grade

    if peer_reviews is not None:
        update_kwargs['peer_reviews'] = peer_reviews

    # Process assignments
    info(f"processing {len(assignments)} assignment(s)")
    for assignment in assignments:
        process_assignment(assignment, update_kwargs)
