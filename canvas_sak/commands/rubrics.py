import re
from canvasapi.util import combine_kwargs
from canvas_sak.core import *


def filter_assignment_associations(associations):
    """Return rubric associations that link to an assignment.

    Canvas returns a rubric's associations with use_for_grading sometimes
    False even when the rubric is attached to the assignment for grading,
    so we list every Assignment-typed association rather than filter on
    use_for_grading.
    """
    return [assoc for assoc in associations
            if assoc.get('association_type') == 'Assignment']


def find_rubrics_by_name(rubrics_list, name):
    """Find rubrics by title: exact match first, then case-insensitive partial."""
    exact = [r for r in rubrics_list if getattr(r, 'title', '') == name]
    if exact:
        return exact
    name_lower = name.lower()
    return [r for r in rubrics_list
            if name_lower in getattr(r, 'title', '').lower()]


def _fmt_pts(points):
    """Render 10.0 as 10 but leave non-integral points alone."""
    if isinstance(points, float) and points.is_integer():
        return int(points)
    return points


def _one_line(text):
    """Collapse a long description to a single line for the text format."""
    return ' '.join(text.split())


def format_rubric_definition(title, points, criteria):
    """Format a rubric's criteria and ratings in the format
    parse_rubric_definitions accepts:

        Title (20 pts)
        * Criterion (10 pts): optional long description
          - Rating (10 pts): optional long description
    """
    if points is None or points == 'N/A':
        lines = [f"{title} (N/A)"]
    else:
        lines = [f"{title} ({_fmt_pts(points)} pts)"]
    for criterion in criteria:
        line = f"* {criterion.get('description', '')} ({_fmt_pts(criterion.get('points', 0))} pts)"
        if criterion.get('long_description'):
            line += f": {_one_line(criterion['long_description'])}"
        lines.append(line)
        for rating in criterion.get('ratings') or []:
            rating_line = f"  - {rating.get('description', '')} ({_fmt_pts(rating.get('points', 0))} pts)"
            if rating.get('long_description'):
                rating_line += f": {_one_line(rating['long_description'])}"
            lines.append(rating_line)
    return lines


# criterion/rating lines: name, then "(N pts)", then an optional long description
CRITERION_RE = re.compile(r'^\*\s*(.+?)\s*\(([\d.]+)\s*pts?\)\s*(?::\s*(.*))?$')
RATING_RE = re.compile(r'^-\s*(.+?)\s*\(([\d.]+)\s*pts?\)\s*(?::\s*(.*))?$')


def is_rubric_definition_file(lines):
    """A file with criterion lines ("* name (N pts)") holds rubric definitions,
    as opposed to rubric-to-assignment associations."""
    return any(CRITERION_RE.match(line.strip()) for line in lines)


def parse_rubric_definitions(lines):
    """Parse rubric definition lines into
    [{title, criteria: [{description, points, long_description?, ratings: [...]}]}]"""
    rubrics = []
    current_rubric = None
    current_criterion = None

    for line in lines:
        stripped = line.rstrip('\n\r').strip()
        if not stripped:
            continue

        match = CRITERION_RE.match(stripped)
        if match and current_rubric is not None:
            current_criterion = {
                'description': match.group(1),
                'points': float(match.group(2)),
                'ratings': [],
            }
            if match.group(3):
                current_criterion['long_description'] = match.group(3)
            current_rubric['criteria'].append(current_criterion)
            continue

        match = RATING_RE.match(stripped)
        if match and current_criterion is not None:
            rating = {'description': match.group(1), 'points': float(match.group(2))}
            if match.group(3):
                rating['long_description'] = match.group(3)
            current_criterion['ratings'].append(rating)
            continue

        match = re.match(r'^(.+?)\s*\(\s*(?:[\d.]+\s*pts?|N/A)\s*\)\s*$', stripped, re.IGNORECASE)
        if match and not stripped.startswith(('-', '*')):
            current_rubric = {'title': match.group(1), 'criteria': []}
            current_criterion = None
            rubrics.append(current_rubric)

    return rubrics


def build_criteria_param(criteria):
    """Convert parsed criteria into the indexed-hash form the Canvas API expects."""
    return {
        str(i): {
            'description': criterion['description'],
            'long_description': criterion.get('long_description', ''),
            'points': criterion['points'],
            'ratings': {
                str(j): {
                    'description': rating['description'],
                    'long_description': rating.get('long_description', ''),
                    'points': rating['points'],
                }
                for j, rating in enumerate(criterion.get('ratings', []))
            },
        }
        for i, criterion in enumerate(criteria)
    }


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
@click.argument("rubric", required=False)
@click.option("--active/--inactive", default=True, help="match only active courses")
@click.option("--update-with", "update_file", type=click.File('r'), default=None,
              help="File with rubric assignments to apply (same format as output)")
@click.option("--dryrun/--no-dryrun", default=True, help="Only show what would be changed")
def rubrics(course, rubric, active, update_file, dryrun):
    '''List rubrics and their associated assignments for a course.

    COURSE is a partial course name to match.

    RUBRIC is an optional rubric name (partial match); if given, that rubric's
    criteria and ratings are displayed in a format that can be saved to a
    file, edited, and applied with --update-with to update the rubric (or
    create it in another course).

    --update-with accepts two formats: rubric definitions (criteria lines
    starting with "*") to create or update rubrics, or rubric-to-assignment
    associations (the no-argument listing) to attach rubrics to assignments.

    Examples:

        canvas-sak rubrics "CS101"

        canvas-sak rubrics "CS101" "Project Rubric" > rubric.txt

        canvas-sak rubrics "CS101" --update-with rubric.txt --no-dryrun
    '''

    if rubric and update_file:
        error("Specify either a rubric name or --update-with, not both")
        sys.exit(2)

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
        update_lines = update_file.read().splitlines()

        if is_rubric_definition_file(update_lines):
            # Definition mode: create or update rubric criteria/ratings
            for spec in parse_rubric_definitions(update_lines):
                title = spec['title']
                existing = rubric_by_name.get(title)
                total = _fmt_pts(sum(c['points'] for c in spec['criteria']))
                action = 'update' if existing else 'create'
                if dryrun:
                    info(f"Would {action} rubric: {title} "
                         f"({len(spec['criteria'])} criteria, {total} pts)")
                    continue
                rubric_body = {'title': title,
                               'criteria': build_criteria_param(spec['criteria'])}
                try:
                    if existing:
                        course._requester.request(
                            'PUT', f'courses/{course.id}/rubrics/{existing.id}',
                            _kwargs=combine_kwargs(rubric=rubric_body))
                    else:
                        course.create_rubric(rubric=rubric_body)
                    info(f"{action.capitalize()}d rubric: {title} "
                         f"({len(spec['criteria'])} criteria, {total} pts)")
                except Exception as e:
                    warn(f"Failed to {action} rubric {title}: {e}")

            if dryrun:
                dryrun_warn()
            return

        # Association mode: apply rubric-to-assignment associations from file
        parsed = parse_rubrics_file(update_lines)

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
            dryrun_warn()
        return

    if rubric:
        # Single-rubric mode: display the rubric's definition in --update-with format
        matches = find_rubrics_by_name(rubrics_list, rubric)
        if not matches:
            error(f'Rubric "{rubric}" not found in course')
            sys.exit(2)
        if len(matches) > 1:
            error(f'Multiple rubrics match "{rubric}": '
                  f'{[getattr(r, "title", "") for r in matches]}')
            sys.exit(2)

        matched = matches[0]
        title = getattr(matched, 'title', 'Untitled')
        points = getattr(matched, 'points_possible', 'N/A')

        criteria = getattr(matched, 'data', None)
        if criteria is None:
            detailed_rubric = course.get_rubric(matched.id)
            criteria = getattr(detailed_rubric, 'data', []) or []

        for line in format_rubric_definition(title, points, criteria):
            output(line)
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

            grading_assocs = filter_assignment_associations(associations)
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
