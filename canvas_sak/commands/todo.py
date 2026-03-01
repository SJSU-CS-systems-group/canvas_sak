from canvas_sak import core
from canvas_sak.core import *


def todo_key(course_name, todo_type, assignment_name):
    return (course_name, todo_type, assignment_name)


def parse_remove_file(f):
    """Parse a remove file and return a set of (course, type, assignment) keys."""
    keys = set()
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) >= 3:
            keys.add(todo_key(parts[0], parts[1], parts[2]))
    return keys


def parse_datetime(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))


def assignments_in_window(assignments, start, end):
    """Return list of (name, reason, dt) for assignments due or locking between start and end."""
    results = []
    for a in assignments:
        for field, reason in [("due_at", "due"), ("lock_at", "locks")]:
            val = getattr(a, field, None)
            if not val:
                continue
            dt = parse_datetime(val)
            if start <= dt <= end:
                results.append((a.name, reason, dt))
    results.sort(key=lambda r: r[2])
    return results


def upcoming_assignments(assignments, now, days):
    """Return list of (name, reason, dt) for assignments due or locking within days."""
    return assignments_in_window(assignments, now, now + datetime.timedelta(days=days))


def format_todo_item(item):
    course_name = format_course_name(item.context_name)
    assignment_name = item.assignment["name"]
    todo_type = item.type

    parts = [course_name, todo_type, assignment_name]

    if todo_type == "grading" and hasattr(item, "needs_grading_count"):
        parts.append(f"({item.needs_grading_count} to grade)")

    due_at = item.assignment.get("due_at")
    if due_at:
        parts.append(f"due: {due_at}")

    return parts


@canvas_sak.command()
@click.option("--remove", type=click.File("r"), default=None,
              help="file with todo items to permanently ignore (same tab-separated format as output)")
@click.option("--dryrun/--no-dryrun", default=True, show_default=True,
              help="dryrun mode for --remove")
@click.option("--upcoming", is_flag=True, default=False,
              help="show assignments due or locking within the next 10 days")
@click.option("--recent-past", is_flag=True, default=False,
              help="show assignments that were due or locked in the last 10 days")
def todo(remove, dryrun, upcoming, recent_past):
    '''list my canvas todo items (assignments to grade or submit).'''
    canvas = get_canvas_object()

    if upcoming or recent_past:
        now = datetime.datetime.now(datetime.timezone.utc)
        courses = get_courses(canvas, "", is_active=True)
        found = False
        for course in courses:
            course_name = format_course_name(course.name)
            assignments = list(course.get_assignments())
            if upcoming:
                for name, reason, dt in upcoming_assignments(assignments, now, 10):
                    output("\t".join([course_name, reason, name, dt.strftime("%Y-%m-%d %H:%M")]))
                    found = True
            if recent_past:
                start = now - datetime.timedelta(days=10)
                for name, reason, dt in assignments_in_window(assignments, start, now):
                    output("\t".join([course_name, reason, name, dt.strftime("%Y-%m-%d %H:%M")]))
                    found = True
        if not found:
            label = "upcoming or recent" if upcoming and recent_past else "upcoming" if upcoming else "recent"
            output(f"no {label} assignments")
        return

    items = list(canvas.get_todo_items())

    if remove:
        remove_keys = parse_remove_file(remove)
        removed = 0
        for item in items:
            parts = format_todo_item(item)
            key = todo_key(parts[0], parts[1], parts[2])
            if key in remove_keys:
                if dryrun:
                    info(f"would remove: {'\t'.join(parts)}")
                else:
                    requests.delete(item.ignore_permanently,
                                    headers={"Authorization": f"Bearer {core.access_token}"})
                    info(f"removed: {'\t'.join(parts)}")
                removed += 1
        info(f"{removed} item(s) {'would be ' if dryrun else ''}removed")
        if dryrun and removed > 0:
            warn("this was a dryrun. use --no-dryrun to apply")
        return

    if not items:
        output("no todo items")
        return

    for item in items:
        parts = format_todo_item(item)
        output("\t".join(parts))
