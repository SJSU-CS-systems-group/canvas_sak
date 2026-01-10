from canvas_sak.core import *


def format_date(dt_str):
    """Convert ISO date string to YYYY-MM-DD-hh:mm format"""
    if not dt_str:
        return None
    dt = datetime.datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    return dt.strftime('%Y-%m-%d-%H:%M')


def build_date_entries(unlock_at, due_at, lock_at):
    """Build comma-separated date entries string"""
    entries = []
    if unlock_at:
        formatted = format_date(unlock_at)
        if formatted:
            entries.append(f"available={formatted}")
    if due_at:
        formatted = format_date(due_at)
        if formatted:
            entries.append(f"due={formatted}")
    if lock_at:
        formatted = format_date(lock_at)
        if formatted:
            entries.append(f"until={formatted}")
    return ','.join(entries)


@canvas_sak.command()
@click.argument('course_name', metavar='course')
@click.option('--active/--inactive', default=True, help="show only active courses")
def list_due_dates(course_name, active):
    """List due dates for all assignments in dates file format"""
    canvas = get_canvas_object()
    course = get_course(canvas, course_name, active)

    for assignment in course.get_assignments():
        date_entries = build_date_entries(
            assignment.unlock_at,
            assignment.due_at,
            assignment.lock_at
        )
        output(f"{assignment.name}\t{date_entries}")
