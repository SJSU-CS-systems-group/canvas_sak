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
def todo(remove, dryrun):
    '''list my canvas todo items (assignments to grade or submit).'''
    canvas = get_canvas_object()
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
