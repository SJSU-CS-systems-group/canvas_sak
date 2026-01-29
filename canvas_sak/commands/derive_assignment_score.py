import re
import builtins
from canvas_sak.core import *

# Safe functions allowed in formulas - explicitly from builtins
SAFE_FUNCTIONS = {
    'min': builtins.min,
    'max': builtins.max,
    'sum': builtins.sum,
    'abs': builtins.abs,
    'round': builtins.round,
}

SAFE_FUNCTION_NAMES = set(SAFE_FUNCTIONS.keys())


def extract_variable_names(formula):
    """Extract variable names from formula (identifiers that aren't functions)."""
    # Match word characters (including underscores) that form identifiers
    identifiers = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', formula)
    # Filter out function names
    variables = [name for name in identifiers if name not in SAFE_FUNCTION_NAMES]
    return list(set(variables))


def variable_to_assignment_name(var_name):
    """Convert variable name (with underscores) to assignment name (with spaces)."""
    return var_name.replace('_', ' ')


def validate_formula(formula, var_names):
    """Validate formula syntax and return error message if invalid."""
    # First try to compile the formula
    try:
        compile(formula, '<formula>', 'eval')
    except SyntaxError as e:
        return f"Syntax error: {e.msg} at position {e.offset}"

    # Try evaluating with dummy values to catch runtime errors
    namespace = dict(SAFE_FUNCTIONS)
    namespace.update({var: 50.0 for var in var_names})  # Use 50 as dummy value

    try:
        result = eval(formula, {"__builtins__": {}}, namespace)
    except NameError as e:
        # Extract the undefined name from the error
        match = re.search(r"'(\w+)'", str(e))
        if match:
            name = match.group(1)
            if name in SAFE_FUNCTION_NAMES:
                return f"Function '{name}' failed unexpectedly - please report this bug"
            else:
                available = ', '.join(sorted(SAFE_FUNCTION_NAMES))
                return f"Unknown name '{name}'. Assignment variables use _ for spaces. Available functions: {available}"
        return f"Name error: {e}"
    except TypeError as e:
        error_str = str(e)
        if 'argument' in error_str:
            return f"Function call error: {e}"
        return f"Type error: {e}"
    except ZeroDivisionError:
        # This is okay at validation time - might not happen with real data
        pass
    except Exception as e:
        return f"Formula error: {e}"

    # Check result is a number
    if not isinstance(result, (int, float)):
        return f"Formula must produce a number, got {type(result).__name__}"

    return None  # No error


@canvas_sak.command()
@click.argument("course")
@click.argument("target_assignment")
@click.option("--formula", required=True, help="Formula using assignment names with _ for spaces")
@click.option("--dryrun/--no-dryrun", default=True)
def derive_assignment_score(course, target_assignment, formula, dryrun):
    '''Compute assignment scores from a formula using other assignments.

    Assignment names in the formula use underscores for spaces.
    Scores are converted to percentages (0-100) before applying the formula.

    Available functions: min, max, sum, abs, round

    Examples:

        canvas-sak derive-assignment-score "CS101" "Average" --formula "(Quiz_1 + Quiz_2) / 2"

        canvas-sak derive-assignment-score "CS101" "Best_Score" --formula "max(Midterm, Final)"

        canvas-sak derive-assignment-score "CS101" "Weighted" --formula "0.3 * Homework + 0.7 * Exam"
    '''

    canvas = get_canvas_object()
    course = get_course(canvas, course)

    # Get the target assignment (convert underscores to spaces)
    target_assignment_name = variable_to_assignment_name(target_assignment)
    target = get_assignment(course, target_assignment_name)
    if not target:
        error(f'Target assignment "{target_assignment_name}" not found')
        sys.exit(2)

    # Extract variable names from formula
    var_names = extract_variable_names(formula)
    if not var_names:
        error("No assignment variables found in formula")
        sys.exit(2)

    # Validate formula syntax before fetching data
    formula_error = validate_formula(formula, var_names)
    if formula_error:
        error(f"Invalid formula: {formula_error}")
        sys.exit(2)

    info(f"Formula: {formula}")
    info(f"Variables: {', '.join(var_names)}")

    # Map variable names to assignments
    assignments = {}
    for var_name in var_names:
        assignment_name = variable_to_assignment_name(var_name)
        assignment = get_assignment(course, assignment_name)
        if not assignment:
            error(f'Assignment "{assignment_name}" (from variable {var_name}) not found')
            sys.exit(2)
        assignments[var_name] = assignment
        info(f"  {var_name} -> {assignment.name} ({assignment.points_possible} pts)")

    # Build a mapping: user_id -> {var_name: percentage}
    user_scores = defaultdict(dict)

    for var_name, assignment in assignments.items():
        points_possible = assignment.points_possible
        if not points_possible or points_possible == 0:
            error(f'Assignment "{assignment.name}" has no points possible')
            sys.exit(2)
        for submission in assignment.get_submissions():
            if submission.score is not None:
                percentage = (submission.score / points_possible) * 100
                user_scores[submission.user_id][var_name] = percentage

    # Get user info for display
    user_info = {}
    for enrollment in course.get_enrollments():
        if hasattr(enrollment, 'user'):
            user_info[enrollment.user['id']] = enrollment.user.get('name', str(enrollment.user['id']))

    # Compute scores for each student
    computed_scores = {}
    skipped_count = 0

    for submission in target.get_submissions():
        user_id = submission.user_id
        user_name = user_info.get(user_id, str(user_id))

        # Check if we have all required scores
        if user_id not in user_scores:
            skipped_count += 1
            continue

        scores = user_scores[user_id]
        missing = [var for var in var_names if var not in scores]
        if missing:
            warn(f"Skipping {user_name}: missing {', '.join(missing)}")
            skipped_count += 1
            continue

        # Build namespace for eval
        namespace = dict(SAFE_FUNCTIONS)
        namespace.update(scores)

        try:
            result = eval(formula, {"__builtins__": {}}, namespace)
            computed_scores[submission] = (user_name, result)
        except ZeroDivisionError:
            warn(f"Skipping {user_name}: division by zero")
            skipped_count += 1
        except Exception as e:
            warn(f"Skipping {user_name}: formula error - {e}")
            skipped_count += 1

    info(f"Computed {len(computed_scores)} scores, skipped {skipped_count}")

    if dryrun:
        for submission, (user_name, score) in computed_scores.items():
            info(f"  {user_name}: {score:.2f}")
        warn("This was a dryrun. Nothing has been updated")
    else:
        with click.progressbar(length=len(computed_scores), label="updating grades", show_pos=True) as bar:
            for submission, (user_name, score) in computed_scores.items():
                submission.edit(submission={'posted_grade': score})
                bar.update(1)
        info(f"Updated {len(computed_scores)} grades")
