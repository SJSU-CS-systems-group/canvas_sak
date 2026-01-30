import re
from canvas_sak.core import *


def parse_rubrics_file(file):
    """Parse a rubrics file and return a list of (rubric_name, [assignment_name, ...])"""
    rubrics = []
    current_rubric = None
    current_assignments = []

    # Patterns to skip (info/status messages)
    skip_patterns = [
        r'^accessing canvas',
        r'^Rubrics for .+:$',
        r'^\(no assignments\)$',
        r'^No rubrics found',
    ]

    for line in file:
        line = line.rstrip('\n\r')

        # Skip empty lines
        if not line.strip():
            continue

        stripped = line.strip()

        # Skip known info/status lines
        if any(re.match(pat, stripped, re.IGNORECASE) for pat in skip_patterns):
            continue

        # Skip lines ending with colon (headers)
        if stripped.endswith(':'):
            continue

        # Match assignment line: starts with "-" with optional whitespace around it
        assignment_match = re.match(r'^\s*-\s*(.+)$', line)
        if assignment_match and current_rubric:
            assignment_name = assignment_match.group(1).strip()
            if assignment_name:
                current_assignments.append(assignment_name)
            continue

        # Match rubric line: must have "(XX pts)" or "(N/A)" or similar at end
        rubric_match = re.match(r'^(.+?)\s*\([\d.]+\s*(?:pts?)?\s*\)\s*$', stripped)
        if not rubric_match:
            rubric_match = re.match(r'^(.+?)\s*\(N/A\)\s*$', stripped, re.IGNORECASE)

        if rubric_match and not stripped.startswith('-'):
            # Save previous rubric if exists
            if current_rubric:
                rubrics.append((current_rubric, current_assignments))

            current_rubric = rubric_match.group(1).strip()
            current_assignments = []

    # Save last rubric
    if current_rubric:
        rubrics.append((current_rubric, current_assignments))

    return rubrics


@canvas_sak.command()
@click.argument("course")
@click.option("--active/--inactive", default=True, help="match only active courses")
@click.option("--update-with", "update_file", type=click.File('r'), default=None,
              help="File with rubric assignments to apply (same format as output)")
@click.option("--dryrun/--no-dryrun", default=True, help="Only show what would be changed")
def rubrics(course, active, update_file, dryrun):
    '''List rubrics and their associated assignments for a course.

    COURSE is a partial course name to match.

    Examples:

        canvas-sak rubrics "CS101"

        canvas-sak rubrics "CS101" --update-with rubrics.txt --no-dryrun
    '''

    canvas = get_canvas_object()
    course = get_course(canvas, course, is_active=active)

    # Build maps for lookups
    rubrics_list = list(course.get_rubrics())
    rubric_by_name = {getattr(r, 'title', ''): r for r in rubrics_list}

    assignment_data = list(course.get_course_level_assignment_data())
    assignment_by_id = {a['assignment_id']: a['title'] for a in assignment_data}

    def find_assignment(name):
        """Find assignment by exact match first, then partial match."""
        # Exact match
        for a in assignment_data:
            if a['title'] == name:
                return a['assignment_id'], a['title']
        # Partial match (case-insensitive)
        name_lower = name.lower()
        matches = [(a['assignment_id'], a['title']) for a in assignment_data
                   if name_lower in a['title'].lower()]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            warn(f'  Multiple matches for "{name}": {[m[1] for m in matches[:5]]}')
            return None, None
        # Try to find similar names for helpful error message
        similar = [(a['assignment_id'], a['title']) for a in assignment_data
                   if any(word in a['title'].lower() for word in name_lower.split('-') if len(word) > 2)
                   or any(word in a['title'].lower() for word in name_lower.split('_') if len(word) > 2)]
        if similar:
            warn(f'  Did you mean: {[m[1] for m in similar[:3]]}?')
        return None, None

    if update_file:
        # Update mode: apply rubric associations from file
        parsed = parse_rubrics_file(update_file)

        if not parsed:
            error("No rubrics found in file")
            sys.exit(2)

        for rubric_name, assignments in parsed:
            if rubric_name not in rubric_by_name:
                error(f'Rubric "{rubric_name}" not found in course')
                continue

            rubric = rubric_by_name[rubric_name]
            info(f"Rubric: {rubric_name}")

            for assignment_name in assignments:
                assignment_id, actual_name = find_assignment(assignment_name)
                if not assignment_id:
                    warn(f'  Assignment "{assignment_name}" not found')
                    continue

                display_name = actual_name if actual_name != assignment_name else assignment_name

                if dryrun:
                    info(f"  Would associate: {display_name}")
                else:
                    try:
                        course.create_rubric_association(
                            rubric_association={
                                'rubric_id': rubric.id,
                                'association_id': assignment_id,
                                'association_type': 'Assignment',
                                'use_for_grading': True,
                                'purpose': 'grading'
                            }
                        )
                        info(f"  Associated: {display_name}")
                    except Exception as e:
                        warn(f"  Failed to associate {display_name}: {e}")

        if dryrun:
            warn("This was a dryrun. Nothing has been updated.")
        return

    # List mode: show rubrics and associations
    info(f"Rubrics for {course.name}:")

    if not rubrics_list:
        output("  No rubrics found")
        return

    for rubric in rubrics_list:
        title = getattr(rubric, 'title', 'Untitled')
        points = getattr(rubric, 'points_possible', 'N/A')
        rubric_id = rubric.id

        output(f"\n  {title} ({points} pts)")

        # Get rubric with associations to find linked assignments
        try:
            detailed_rubric = course.get_rubric(rubric_id, include=['assignment_associations'])
            associations = getattr(detailed_rubric, 'associations', [])

            grading_assocs = [assoc for assoc in associations
                              if assoc.get('association_type') == 'Assignment'
                              and assoc.get('use_for_grading', False)]
            if grading_assocs:
                for assoc in grading_assocs:
                    assoc_id = assoc.get('association_id')
                    if assoc_id in assignment_by_id:
                        output(f"    - {assignment_by_id[assoc_id]}")
                    else:
                        output(f"    - Assignment ID {assoc_id}")
            else:
                output("    (no assignments)")
        except Exception as e:
            warn(f"    Could not fetch associations: {e}")
