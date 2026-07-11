import click

from canvas_sak.core import *

# Navigation tabs that Canvas does not allow to be hidden or moved.
UNHIDEABLE_TAB_IDS = {"home", "settings"}


def _get_tabs(course):
    """Return the course navigation tabs sorted by their current position."""
    tabs = list(course.get_tabs())
    tabs.sort(key=lambda t: getattr(t, "position", 0))
    return tabs


def _is_hidden(tab):
    """Canvas only sets ``hidden`` on tabs that are hidden from students."""
    return bool(getattr(tab, "hidden", False))


def _match_tab(tabs, item):
    """Find the single tab matching ``item`` by label (case-insensitive).

    Prefers an exact label match, then falls back to a unique substring match.
    Returns the tab, or None if there is no match or the match is ambiguous.
    """
    item_l = item.strip().lower()
    exact = [t for t in tabs if t.label.lower() == item_l]
    if len(exact) == 1:
        return exact[0]
    if exact:
        error(f"'{item}' matches multiple navigation items: "
              f"{', '.join(t.label for t in exact)}")
        return None
    partial = [t for t in tabs if item_l in t.label.lower()]
    if len(partial) == 1:
        return partial[0]
    if not partial:
        error(f"no navigation item matches '{item}'")
    else:
        error(f"'{item}' matches multiple navigation items: "
              f"{', '.join(t.label for t in partial)}")
    return None


@canvas_sak.group("settings-navigation")
def settings_navigation():
    """List and update a course's navigation menu (Settings > Navigation)."""


@settings_navigation.command("list")
@click.argument("course_name", metavar="course")
@click.option("--active/--inactive", default=True, help="search active or inactive courses")
def list_navigation(course_name, active):
    """List the visible and hidden navigation items for a course."""
    canvas = get_canvas_object()
    course = get_course(canvas, course_name, is_active=active)

    tabs = _get_tabs(course)
    visible = [t for t in tabs if not _is_hidden(t)]
    hidden = [t for t in tabs if _is_hidden(t)]

    output(f"navigation for {course.name}")
    output("visible:")
    for t in visible:
        output(f"    {t.label}")
    output("hidden:")
    for t in hidden:
        output(f"    {t.label}")


@settings_navigation.command("update")
@click.argument("course_name", metavar="course")
@click.argument("visible_items", metavar="item", nargs=-1)
@click.option("--active/--inactive", default=True, help="search active or inactive courses")
@click.option("--dryrun/--no-dryrun", default=True, show_default=True,
              help="show what would happen, but don't do it")
def update_navigation(course_name, visible_items, active, dryrun):
    """Make the given navigation ITEMs visible and hide the rest.

    Each ITEM is matched against a navigation item's label. Items not listed
    are hidden. Canvas does not allow the Home and Settings items to be
    hidden, so those are left visible.

    Items may be given as arguments and/or piped on stdin, one per line, for
    example:

        canvas-sak settings-navigation update "My Course" < items.lst
    """
    items = list(visible_items)

    # Also accept items on stdin (one per line) when input is piped in.
    stdin = click.get_text_stream("stdin")
    if not stdin.isatty():
        items.extend(line.strip() for line in stdin if line.strip())

    if not items:
        error("no navigation items specified; pass items as arguments or on stdin")
        sys.exit(2)

    canvas = get_canvas_object()
    course = get_course(canvas, course_name, is_active=active)

    tabs = _get_tabs(course)

    # Resolve the requested items to tabs, keeping track of which to show.
    keep_visible_ids = set()
    for item in items:
        tab = _match_tab(tabs, item)
        if tab is None:
            sys.exit(2)
        keep_visible_ids.add(tab.id)

    for tab in tabs:
        should_hide = tab.id not in keep_visible_ids
        currently_hidden = _is_hidden(tab)

        if should_hide and tab.id in UNHIDEABLE_TAB_IDS:
            if not currently_hidden:
                warn(f"cannot hide '{tab.label}'; leaving it visible")
            continue

        if should_hide == currently_hidden:
            # already in the desired state
            continue

        action = "hide" if should_hide else "show"
        output(f"{action} {tab.label}")
        if not dryrun:
            tab.update(hidden=should_hide)

    if dryrun:
        dryrun_warn()
