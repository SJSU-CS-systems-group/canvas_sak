from canvas_sak.core import *


def parse_date(date_str):
    """Convert YYYY-MM-DD-hh:mm format (local time) to ISO format for Canvas API"""
    if not date_str:
        return None
    dt = datetime.datetime.strptime(date_str, '%Y-%m-%d-%H:%M')
    local_dt = dt.astimezone()
    return local_dt.isoformat()


def parse_date_entries(entries_str):
    """Parse comma-separated date entries into a dict"""
    result = {}
    if not entries_str.strip():
        return result
    for entry in entries_str.split(','):
        if '=' not in entry:
            continue
        key, value = entry.split('=', 1)
        key = key.strip()
        value = value.strip()
        if key == 'available':
            result['unlock_at'] = parse_date(value)
        elif key == 'due':
            result['due_at'] = parse_date(value)
        elif key == 'until':
            result['lock_at'] = parse_date(value)
    return result


@canvas_sak.command()
@click.argument('course_name', metavar='course')
@click.argument('dates_file', type=click.File('r'))
@click.option('--active/--inactive', default=True, help="show only active courses")
@click.option('--dryrun/--no-dryrun', default=True, show_default=True, help="show what would happen, but don't do it")
def set_due_dates(course_name, dates_file, active, dryrun):
    """Set due dates for assignments from a dates file.

    Input format: assignment name TAB comma-separated dates

    Each date is type=YYYY-MM-DD-hh:mm where type is available, due, or until.

    Example: Homework 1\tavailable=2024-01-15-09:00,due=2024-01-22-23:59
    """
    canvas = get_canvas_object()
    course = get_course(canvas, course_name, active)

    # Build assignment lookup by name
    assignments = {a.name: a for a in course.get_assignments()}

    for line in dates_file:
        line = line.strip()
        if not line:
            continue
        parts = line.split('\t')
        if len(parts) < 2:
            warn(f"skipping malformed line: {line}")
            continue

        name = parts[0]
        date_entries = parse_date_entries(parts[1])

        if name not in assignments:
            error(f"assignment not found: {name}")
            continue

        if not date_entries:
            info(f"no dates to set for: {name}")
            continue

        if dryrun:
            info(f"would update {name} with {date_entries}")
        else:
            info(f"updating {name}")
            assignments[name].edit(assignment=date_entries)
