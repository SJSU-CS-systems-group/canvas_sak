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


CHANGE_SCORE_WITH_PREV = re.compile(
    r'^change-score\s+previous:\s*([\d.]+)\s+new:\s*([\d.]+)$'
)
CHANGE_SCORE_NO_PREV = re.compile(
    r'^change-score\s+new:\s*([\d.]+)$'
)


def build_change_score_comment(previous_score, new_score):
    """Build a change-score comment string.

    Returns 'change-score previous: X new: Y' or 'change-score new: Y'
    if previous_score is None.
    """
    if previous_score is None:
        return f"change-score new: {new_score}"
    return f"change-score previous: {previous_score} new: {new_score}"


def parse_change_score_comment(comment_text):
    """Parse a change-score comment string.

    Returns (previous, new) tuple where previous may be None,
    or None if the comment doesn't match the change-score format.
    """
    if not comment_text:
        return None
    m = CHANGE_SCORE_WITH_PREV.match(comment_text.strip())
    if m:
        return (float(m.group(1)), float(m.group(2)))
    m = CHANGE_SCORE_NO_PREV.match(comment_text.strip())
    if m:
        return (None, float(m.group(1)))
    return None


def find_last_manual_score(current_score, comments):
    """Walk backwards through change-score comments to find the original manual score.

    If current_score matches the latest change-score "new" value, follows the chain
    of "previous" values back to find the score that was set before any tool runs.
    Returns None if the chain ends with a change-score that has no previous value.
    """
    # Extract all change-score comments in order
    parsed = []
    for c in comments:
        text = c.get("comment", "") if isinstance(c, dict) else getattr(c, "comment", "")
        result = parse_change_score_comment(text)
        if result is not None:
            parsed.append(result)

    if not parsed:
        return current_score

    # Check if the current score matches the latest change-score "new"
    latest_prev, latest_new = parsed[-1]
    if current_score != latest_new:
        # Score was manually changed after last tool run
        return current_score

    # Walk the chain backwards
    score_to_find = latest_prev
    if score_to_find is None:
        return None

    # Look through earlier change-score comments (in reverse) for a chain
    for prev, new in reversed(parsed[:-1]):
        if new == score_to_find:
            score_to_find = prev
            if score_to_find is None:
                return None

    return score_to_find


@canvas_sak.command()
@click.argument("course")
@click.argument("target_assignment")
@click.option("--formula", required=True, help="Formula using assignment names with _ for spaces")
@click.option("--dryrun/--no-dryrun", default=True)
@click.option("--use-last-assigned/--no-use-last-assigned", default=False,
              help="Use the last manually-assigned score as the previous score instead of the current score")
def derive_assignment_score(course, target_assignment, formula, dryrun, use_last_assigned):
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

    include = ['submission_comments'] if use_last_assigned else []
    for submission in target.get_submissions(include=include):
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
            if use_last_assigned:
                comments = getattr(submission, 'submission_comments', [])
                previous_score = find_last_manual_score(submission.score, comments)
            else:
                previous_score = submission.score
            computed_scores[submission] = (user_name, result, previous_score)
        except ZeroDivisionError:
            warn(f"Skipping {user_name}: division by zero")
            skipped_count += 1
        except Exception as e:
            warn(f"Skipping {user_name}: formula error - {e}")
            skipped_count += 1

    info(f"Computed {len(computed_scores)} scores, skipped {skipped_count}")

    if dryrun:
        for submission, (user_name, score, previous_score) in computed_scores.items():
            comment = build_change_score_comment(previous_score, score)
            info(f"  {user_name}: {score:.2f} ({comment})")
        warn("This was a dryrun. Nothing has been updated")
    else:
        with click.progressbar(length=len(computed_scores), label="updating grades", show_pos=True) as bar:
            for submission, (user_name, score, previous_score) in computed_scores.items():
                comment = build_change_score_comment(previous_score, score)
                submission.edit(
                    submission={'posted_grade': score},
                    comment={'text_comment': comment},
                )
                bar.update(1)
        info(f"Updated {len(computed_scores)} grades")
