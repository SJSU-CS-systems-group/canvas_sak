from canvasapi.exceptions import ResourceDoesNotExist

from canvas_sak.core import *

@canvas_sak.command()
@click.argument('course_name', metavar='course')
@click.argument('assignment_name', metavar='assignment')
@click.option('--canvasid', default=None, type=int, help="the canvas user id of the student")
@click.option('--sisid', default=None, help="the SIS user id of the student")
@click.option('--grade', required=True, help="the grade to assign (-1 to unset)")
@click.option('--message', required=True, help="submission comment to post")
@click.option('--attachment', default=None, type=click.Path(exists=True),
              help="file to attach to the submission comment")
@click.option('--delete-previous', is_flag=True, default=False,
              help="delete previous comments and attachments from you before grading")
@click.option('--only-changes', is_flag=True, default=False,
              help="skip the update if the new grade matches the current grade")
@click.option('--dryrun/--no-dryrun', default=True, show_default=True,
              help="show what would happen, but don't do it")
def grade_submission(course_name, assignment_name, canvasid, sisid, grade, message,
                     attachment, delete_previous, only_changes, dryrun):
    '''
    grade a student's submission for an assignment.

    assigns the specified grade and posts a submission comment. optionally
    attaches a file to the comment.

    use --grade -1 to clear an existing grade.

    use --delete-previous to remove your prior comments and attachments
    before posting the new grade and comment.

    course - any part of an active course name. for example, 249 will match CS249.

    assignment - any part of an assignment's name will be matched. only one
    match is allowed.
    '''

    if canvasid and sisid:
        error("specify either --canvasid or --sisid, not both")
        sys.exit(2)
    if not canvasid and not sisid:
        error("specify either --canvasid or --sisid")
        sys.exit(2)

    canvas = get_canvas_object()
    course = get_course(canvas, course_name)
    assignment = get_assignment(course, assignment_name)

    if sisid:
        _, sis_to_user_id = build_sis_maps(course)
        if sisid not in sis_to_user_id:
            error(f"no student found with SIS ID {sisid}")
            sys.exit(2)
        student_id = sis_to_user_id[sisid]
    else:
        student_id = canvasid

    include = ['submission_comments'] if delete_previous else []
    try:
        submission = assignment.get_submission(student_id, include=include)
    except ResourceDoesNotExist:
        error(f"no submission found for student {student_id} on {assignment.name}")
        sys.exit(2)

    if submission.grade is not None:
        delta_str = ''
        if grade != '-1':
            try:
                delta = float(grade) - float(submission.grade)
                delta_str = f' ({delta:+g})'
            except ValueError:
                pass
        info(f"current grade: {submission.grade}{delta_str}")

    if only_changes and submission.grade is not None and grade != '-1':
        try:
            if float(submission.grade) == float(grade):
                info(f"skipping {assignment.name} for student {student_id}, grade unchanged")
                return
        except ValueError:
            if submission.grade == grade:
                info(f"skipping {assignment.name} for student {student_id}, grade unchanged")
                return

    posted_grade = '' if grade == '-1' else grade

    if delete_previous:
        my_comments = [c for c in submission.submission_comments
                       if c['author_id'] == canvas.user_id]
        if dryrun:
            for c in my_comments:
                info(f"  would delete comment {c['id']}: {c['comment']}")
                for a in c.get('attachments', []):
                    info(f"    would delete attachment: {a['display_name']}")
        else:
            for c in my_comments:
                submission._requester.request(
                    "DELETE",
                    "courses/{}/assignments/{}/submissions/{}/comments/{}".format(
                        submission.course_id, submission.assignment_id,
                        submission.user_id, c['id']
                    )
                )
                info(f"deleted comment {c['id']}: {c['comment']}")

    if dryrun:
        info(f"would grade {assignment.name} for student {student_id}:")
        if grade == '-1':
            info("  grade: (unset)")
        else:
            info(f"  grade: {grade}")
        info(f"  comment: {message}")
        if attachment:
            info(f"  attachment: {attachment}")
    else:
        submission.edit(submission={'posted_grade': posted_grade},
                        comment={'text_comment': message})
        if grade == '-1':
            info(f"unset grade for {assignment.name} for student {student_id}")
        else:
            info(f"graded {assignment.name} for student {student_id}: {grade}")
        info(f"posted comment: {message}")

        if attachment:
            submission.upload_comment(attachment)
            info(f"uploaded attachment: {attachment}")
