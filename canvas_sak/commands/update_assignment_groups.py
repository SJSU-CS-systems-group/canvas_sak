from canvas_sak.core import *


def parse_groups_file(f):
    """Parse assignment groups file.

    Format:
        GROUP_NAME: WEIGHT%
        assignment1
        assignment2

        ANOTHER_GROUP: WEIGHT%
        assignment3

    Returns list of (group_name, weight, [assignment_names])
    """
    groups = []
    current_group = None
    current_weight = None
    current_assignments = []

    for line in f:
        line = line.rstrip('\n\r')

        # Check if this is a group header (contains : and ends with %)
        if ':' in line and line.rstrip().endswith('%'):
            # Save previous group if any
            if current_group is not None:
                groups.append((current_group, current_weight, current_assignments))

            # Parse new group
            parts = line.rsplit(':', 1)
            current_group = parts[0].strip()
            weight_str = parts[1].strip().rstrip('%')
            try:
                current_weight = float(weight_str)
            except ValueError:
                error(f"invalid weight '{parts[1].strip()}' for group '{current_group}'")
                current_weight = 0
            current_assignments = []
        elif line.strip():
            # Non-empty line is an assignment name
            if current_group is not None:
                current_assignments.append(line.strip())

    # Don't forget the last group
    if current_group is not None:
        groups.append((current_group, current_weight, current_assignments))

    return groups


def print_current_groups(course):
    """Print current assignment groups in the file format."""
    # Get assignment groups with assignments
    groups = list(course.get_assignment_groups())
    assignments = list(course.get_assignments())

    # Build a map of group_id to assignments
    group_assignments = {}
    for a in assignments:
        gid = getattr(a, 'assignment_group_id', None)
        if gid not in group_assignments:
            group_assignments[gid] = []
        group_assignments[gid].append(a.name)

    # Print each group
    for group in groups:
        weight = getattr(group, 'group_weight', 0) or 0
        output(f"{group.name}: {weight:.0f}%")
        for assignment_name in group_assignments.get(group.id, []):
            output(assignment_name)
        output("")


@canvas_sak.command()
@click.argument('course_name', metavar='course')
@click.argument('groups_file', type=click.File('r'), required=False)
@click.option('--active/--inactive', default=True, help="search active or inactive courses")
@click.option('--dryrun/--no-dryrun', default=True, show_default=True,
              help="show what would happen, but don't do it")
def update_assignment_groups(course_name, groups_file, active, dryrun):
    """Update assignment groups and their weights from a file.

    If no file is specified, prints the current assignment groups in the file format.

    The file format is:

        GROUP_NAME: WEIGHT%
        assignment1
        assignment2

        ANOTHER_GROUP: WEIGHT%
        assignment3

    Examples:

        canvas-sak update-assignment-groups "My Course"  # print current groups

        canvas-sak update-assignment-groups "My Course" groups.txt

        canvas-sak update-assignment-groups "My Course" groups.txt --no-dryrun
    """
    canvas = get_canvas_object()
    course = get_course(canvas, course_name, is_active=active)
    info(f"found {course.name}")

    # If no file specified, print current groups
    if groups_file is None:
        print_current_groups(course)
        return

    # Parse the groups file
    groups = parse_groups_file(groups_file)

    if not groups:
        error("no assignment groups found in file")
        sys.exit(1)

    # Validate weights sum to 100%
    total_weight = sum(g[1] for g in groups)
    if abs(total_weight - 100) > 0.01:
        error(f"weights sum to {total_weight}%, must equal 100%")
        sys.exit(1)

    info(f"parsed {len(groups)} assignment groups, weights sum to {total_weight}%")

    # Get existing assignment groups
    existing_groups = {g.name: g for g in course.get_assignment_groups()}
    info(f"found {len(existing_groups)} existing assignment groups")

    # Get all assignments
    assignments = {a.name: a for a in course.get_assignments()}
    info(f"found {len(assignments)} assignments")

    # Process each group
    for group_name, weight, assignment_names in groups:
        output("")
        output(f"Assignment Group: {group_name} ({weight}%)")

        # Create or update the group
        if group_name in existing_groups:
            group = existing_groups[group_name]
            current_weight = getattr(group, 'group_weight', None)
            if current_weight != weight:
                if dryrun:
                    info(f"  would update weight from {current_weight}% to {weight}%")
                else:
                    info(f"  updating weight from {current_weight}% to {weight}%")
                    group.edit(group_weight=weight)
            else:
                info(f"  weight already set to {weight}%")
        else:
            if dryrun:
                info(f"  would create group with weight {weight}%")
            else:
                info(f"  creating group with weight {weight}%")
                group = course.create_assignment_group(name=group_name, group_weight=weight)
                existing_groups[group_name] = group

        # Process assignments in this group
        for assignment_name in assignment_names:
            if assignment_name not in assignments:
                error(f"  assignment not found: {assignment_name}")
                continue

            assignment = assignments[assignment_name]
            current_group_id = getattr(assignment, 'assignment_group_id', None)
            target_group_id = existing_groups[group_name].id if group_name in existing_groups else None

            if current_group_id == target_group_id:
                info(f"  {assignment_name}: already in this group")
            else:
                if dryrun:
                    info(f"  {assignment_name}: would move to this group")
                else:
                    info(f"  {assignment_name}: moving to this group")
                    assignment.edit(assignment={'assignment_group_id': target_group_id})

    if dryrun:
        output("")
        output("(dry run - use --no-dryrun to apply changes)")
