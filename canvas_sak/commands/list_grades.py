from canvas_sak.core import *


def student_matches(login_id, name, name_filter, id_filter):
    """Return True if the student passes the --name and --id filters.

    name_filter is a case-insensitive substring match against the user's name.
    id_filter is an exact match against the user's login_id.
    Either may be None to skip that filter.
    """
    if name_filter is not None:
        if not name or name_filter.lower() not in name.lower():
            return False
    if id_filter is not None:
        if login_id != id_filter:
            return False
    return True


def format_rubric_scores(rubric_assessment, criterion_id_to_desc):
    """Render a rubric_assessment dict as 'desc1=points1 desc2=points2 ...'.

    criterion_id_to_desc should preserve the rubric's criterion order so the
    output is consistent across students. Criteria with no entry in the
    assessment are skipped; criteria present in the assessment but missing
    from criterion_id_to_desc fall back to the criterion id.
    """
    if not rubric_assessment:
        return ""

    parts = []
    seen = set()
    for cid, desc in criterion_id_to_desc.items():
        if cid in rubric_assessment:
            points = rubric_assessment[cid].get("points", "")
            parts.append(f"{desc}={points}")
            seen.add(cid)

    for cid, entry in rubric_assessment.items():
        if cid in seen:
            continue
        points = entry.get("points", "") if isinstance(entry, dict) else ""
        parts.append(f"{cid}={points}")

    return " ".join(parts)


@canvas_sak.command("list-grades")
@click.argument("course")
@click.argument("assignment")
@click.option("--name", default=None,
              help="filter to students whose name contains this substring (case-insensitive)")
@click.option("--id", "id_filter", default=None,
              help="filter to the student with this login id")
@click.option("--rubric", is_flag=True, default=False,
              help="include rubric criterion scores alongside the grade")
@click.option("--active/--inactive", default=True, help="match only active courses")
def list_grades(course, assignment, name, id_filter, rubric, active):
    """list student ids, names, and grades for an assignment.

    course - any part of an active course name.

    assignment - any part of an assignment's name.
    """
    canvas = get_canvas_object()
    course = get_course(canvas, course, is_active=active)
    assignment_obj = get_assignment(course, assignment)

    user_id_to_login = {}
    user_id_to_name = {}
    for user in course.get_users(include=["enrollments"]):
        user_id_to_login[user.id] = getattr(user, "login_id", None)
        user_id_to_name[user.id] = getattr(user, "name", str(user.id))

    criterion_id_to_desc = {}
    if rubric:
        rubric_data = getattr(assignment_obj, "rubric", None) or []
        for criterion in rubric_data:
            criterion_id_to_desc[criterion.get("id")] = criterion.get("description", criterion.get("id"))

    include = ["rubric_assessment"] if rubric else []
    for submission in assignment_obj.get_submissions(include=include):
        login_id = user_id_to_login.get(submission.user_id)
        student_name = user_id_to_name.get(submission.user_id, str(submission.user_id))

        if not student_matches(login_id, student_name, name, id_filter):
            continue

        grade = submission.grade if submission.grade is not None else ""
        login_display = login_id if login_id is not None else ""

        line = f"{login_display}\t{student_name}\t{grade}"
        if rubric:
            assessment = getattr(submission, "rubric_assessment", None)
            rubric_str = format_rubric_scores(assessment, criterion_id_to_desc)
            if rubric_str:
                line += f"\t{rubric_str}"
        output(line)
