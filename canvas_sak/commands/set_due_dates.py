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


def parse_assignment_name(name):
    """Parse assignment name and optional section override.

    Returns (assignment_name, section_name) where section_name is None
    if no override specified.

    Example: "Quiz 1 [Section A]" -> ("Quiz 1", "Section A")
    Example: "Quiz 1" -> ("Quiz 1", None)
    """
    if name.endswith(']') and '[' in name:
        bracket_start = name.rfind('[')
        assignment_name = name[:bracket_start].strip()
        section_name = name[bracket_start + 1:-1].strip()
        return assignment_name, section_name
    return name, None


@canvas_sak.command()
@click.argument('course_name', metavar='course')
@click.argument('dates_file', type=click.File('r'))
@click.option('--active/--inactive', default=True, help="show only active courses")
@click.option('--dryrun/--no-dryrun', default=True, show_default=True, help="show what would happen, but don't do it")
def set_due_dates(course_name, dates_file, active, dryrun):
    """Set due dates for assignments from a dates file.

    Input format: assignment name TAB comma-separated dates

    Each date is type=YYYY-MM-DD-hh:mm where type is available, due, or until.

    For section-specific dates, append the section name in brackets:

        Quiz 1\tdue=2024-01-20-23:59
        Quiz 1 [Section A]\tdue=2024-01-22-23:59

    Examples:

        Homework 1\tavailable=2024-01-15-09:00,due=2024-01-22-23:59

        Quiz 1 [Evening Section]\tdue=2024-01-25-23:59
    """
    canvas = get_canvas_object()
    course = get_course(canvas, course_name, active)

    # Build assignment lookup by name (with overrides for later)
    assignments = {a.name: a for a in course.get_assignments(include=['overrides'])}

    # Build section lookup by name
    sections = {s.name: s for s in course.get_sections()}
    info(f"found {len(sections)} sections: {', '.join(sections.keys())}")

    for line in dates_file:
        line = line.strip()
        if not line:
            continue
        parts = line.split('\t')
        if len(parts) < 2:
            warn(f"skipping malformed line: {line}")
            continue

        raw_name = parts[0]
        date_entries = parse_date_entries(parts[1])

        # Parse assignment name and optional section
        assignment_name, section_name = parse_assignment_name(raw_name)

        if assignment_name not in assignments:
            error(f"assignment not found: {assignment_name}")
            continue

        if not date_entries:
            info(f"no dates to set for: {raw_name}")
            continue

        assignment = assignments[assignment_name]

        if section_name:
            # This is a section override
            if section_name not in sections:
                error(f"section not found: {section_name}")
                continue

            section_id = sections[section_name].id

            # Check if override already exists for this section
            existing_overrides = getattr(assignment, 'overrides', None) or []
            existing_override = None
            for ov in existing_overrides:
                # Handle both dict and object access patterns
                ov_section_id = ov.get('course_section_id') if isinstance(ov, dict) else getattr(ov, 'course_section_id', None)
                if ov_section_id == section_id:
                    existing_override = ov
                    break

            if dryrun:
                if existing_override:
                    info(f"would update override for {raw_name} with {date_entries}")
                else:
                    info(f"would create override for {raw_name} with {date_entries}")
            else:
                if existing_override:
                    info(f"updating override for {raw_name}")
                    # Update existing override
                    override_id = existing_override.get('id') if isinstance(existing_override, dict) else getattr(existing_override, 'id')
                    assignment.edit_override(override_id, assignment_override=date_entries)
                else:
                    info(f"creating override for {raw_name}")
                    # Create new override
                    override_data = {'course_section_id': section_id, **date_entries}
                    assignment.create_override(assignment_override=override_data)
        else:
            # Base assignment dates
            if dryrun:
                info(f"would update {assignment_name} with {date_entries}")
            else:
                info(f"updating {assignment_name}")
                assignment.edit(assignment=date_entries)
