from collections import Counter
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from canvas_sak.core import *


def parse_iso_date(dt_str):
    """Convert ISO date string to datetime object."""
    if not dt_str:
        return None
    return datetime.datetime.fromisoformat(dt_str.replace('Z', '+00:00'))


def check_missing_due_dates(assignments):
    """Check for assignments missing a due date.

    Args:
        assignments: list of assignment-like objects with .name and .due_at

    Returns:
        list of assignment names missing due dates
    """
    missing = []
    for a in assignments:
        if a.due_at is None:
            missing.append(a.name)
    return missing


def check_until_date_consistency_for_group(assignments):
    """Check that submittable assignments in a single group have consistent lock_at offsets.

    Args:
        assignments: list of assignment-like objects with .name, .due_at,
                     .lock_at, and .submission_types

    Returns:
        (most_common_offset, total_counted, issues) where:
        - most_common_offset is a timedelta or None
        - total_counted is how many assignments had a valid offset
        - issues is a list of (name, message) tuples
    """
    non_submittable = {'none', 'not_graded'}
    offsets = []
    offset_assignments = []
    issues = []

    for a in assignments:
        sub_types = set(a.submission_types) if a.submission_types else set()
        if sub_types & non_submittable:
            if not a.due_at:
                issues.append((a.name, "non-submittable assignment missing due date"))
            continue

        due = parse_iso_date(a.due_at)
        lock = parse_iso_date(a.lock_at)

        if due and lock:
            offset = lock - due
            offsets.append(offset)
            offset_assignments.append((a.name, offset))
        elif due and not lock:
            issues.append((a.name, "has due date but no until/lock date"))
        elif lock and not due:
            issues.append((a.name, "has until/lock date but no due date"))

    if not offsets:
        return None, 0, issues

    counter = Counter(offsets)
    most_common_offset, most_common_count = counter.most_common(1)[0]

    for name, offset in offset_assignments:
        if offset != most_common_offset:
            issues.append((name, f"offset is {format_timedelta(offset)}, expected {format_timedelta(most_common_offset)}"))

    return most_common_offset, most_common_count, issues


def group_assignments_by_group(assignments, group_names):
    """Group assignments by their assignment group.

    Args:
        assignments: list of assignment-like objects with .assignment_group_id
        group_names: dict mapping group_id -> group_name

    Returns:
        dict mapping group_name -> list of assignments
    """
    groups = defaultdict(list)
    for a in assignments:
        group_id = getattr(a, 'assignment_group_id', None)
        group_name = group_names.get(group_id, f"Unknown Group ({group_id})")
        groups[group_name].append(a)
    return dict(groups)


def format_timedelta(td):
    """Format a timedelta into a human-readable string."""
    total_seconds = int(td.total_seconds())
    if total_seconds == 0:
        return "0 seconds"
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    parts = []
    if days:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    return ', '.join(parts) if parts else "0 seconds"


def extract_links(html):
    """Extract all links from HTML content.

    Returns:
        list of (tag, attr, url) tuples
    """
    if not html:
        return []
    soup = BeautifulSoup(html, 'lxml')
    links = []
    for a in soup.find_all('a', href=True):
        links.append(('a', 'href', a['href']))
    for img in soup.find_all('img', src=True):
        links.append(('img', 'src', img['src']))
    for iframe in soup.find_all('iframe', src=True):
        links.append(('iframe', 'src', iframe['src']))
    return links


def classify_link(url, canvas_domain, course_id):
    """Classify a link as internal, internal-other-course, external, or skip.

    Returns:
        (category, normalized_path) where category is one of:
        'internal', 'internal_other', 'external', 'skip'
    """
    if not url or url.startswith('#') or url.startswith('mailto:') or url.startswith('javascript:'):
        return 'skip', None

    parsed = urlparse(url)

    # Handle relative URLs (Canvas often uses /courses/... paths)
    if not parsed.scheme and not parsed.netloc:
        path = parsed.path
        if path.startswith(f'/courses/{course_id}'):
            return 'internal', path.split('?')[0].split('#')[0]
        elif path.startswith('/courses/'):
            return 'internal_other', path
        return 'skip', None

    # Handle absolute URLs
    canvas_parsed = urlparse(canvas_domain)
    if parsed.netloc == canvas_parsed.netloc:
        path = parsed.path
        if path.startswith(f'/courses/{course_id}'):
            return 'internal', path.split('?')[0].split('#')[0]
        elif path.startswith('/courses/'):
            return 'internal_other', path
        return 'skip', None

    return 'external', url


def build_resource_map(course, course_id):
    """Build a map of internal course URLs to resource info.

    Returns:
        dict mapping url_path -> {'type': str, 'name': str, 'published': bool}
    """
    resource_map = {}

    info("  fetching pages...")
    for page in course.get_pages():
        published = getattr(page, 'published', True)
        path = f"/courses/{course_id}/pages/{page.url}"
        resource_map[path] = {'type': 'Page', 'name': page.title, 'published': published}

    info("  fetching assignments...")
    for a in course.get_assignments():
        published = getattr(a, 'published', True)
        path = f"/courses/{course_id}/assignments/{a.id}"
        resource_map[path] = {'type': 'Assignment', 'name': a.name, 'published': published}

    info("  fetching discussions...")
    for d in course.get_discussion_topics():
        published = getattr(d, 'published', True)
        path = f"/courses/{course_id}/discussion_topics/{d.id}"
        resource_map[path] = {'type': 'Discussion', 'name': d.title, 'published': published}

    info("  fetching quizzes...")
    for q in course.get_quizzes():
        published = getattr(q, 'published', True)
        path = f"/courses/{course_id}/quizzes/{q.id}"
        resource_map[path] = {'type': 'Quiz', 'name': q.title, 'published': published}

    info("  fetching files...")
    for f in course.get_files():
        path = f"/courses/{course_id}/files/{f.id}"
        # Files don't have a published attribute in the same way; treat as published
        resource_map[path] = {'type': 'File', 'name': getattr(f, 'display_name', str(f.id)), 'published': True}

    return resource_map


def collect_content_with_html(course):
    """Collect all published content items that have HTML bodies.

    Returns:
        list of (source_type, name, html) tuples
    """
    items = []

    info("  scanning pages...")
    for page in course.get_pages(include=['body']):
        if getattr(page, 'published', True):
            body = getattr(page, 'body', None)
            if body:
                items.append(('Page', page.title, body))

    info("  scanning assignments...")
    for a in course.get_assignments():
        if getattr(a, 'published', True):
            desc = getattr(a, 'description', None)
            if desc:
                items.append(('Assignment', a.name, desc))

    info("  scanning discussions...")
    for d in course.get_discussion_topics():
        if getattr(d, 'published', True):
            msg = getattr(d, 'message', None)
            if msg:
                items.append(('Discussion', d.title, msg))

    info("  scanning quizzes...")
    for q in course.get_quizzes():
        if getattr(q, 'published', True):
            desc = getattr(q, 'description', None)
            if desc:
                items.append(('Quiz', q.title, desc))

    return items


def check_external_link(url, timeout, cache):
    """Check if an external URL is reachable.

    Returns:
        (ok, message) tuple
    """
    if url in cache:
        return cache[url]

    try:
        resp = requests.head(url, timeout=timeout, allow_redirects=True)
        if resp.status_code == 405:
            resp = requests.get(url, timeout=timeout, allow_redirects=True, stream=True)
        ok = resp.status_code < 400
        msg = None if ok else f"HTTP {resp.status_code}"
    except requests.ConnectionError:
        ok, msg = False, "connection failed"
    except requests.Timeout:
        ok, msg = False, "timeout"
    except requests.RequestException as e:
        ok, msg = False, str(e)

    cache[url] = (ok, msg)
    return ok, msg


def check_module_items(course, course_id, resource_map):
    """Check that module items reference published resources.

    Returns:
        list of (module_name, item_name, message) tuples
    """
    issues = []
    for module in course.get_modules():
        if not getattr(module, 'published', True):
            continue
        for item in module.get_module_items():
            item_type = getattr(item, 'type', None)
            content_id = getattr(item, 'content_id', None)
            item_name = getattr(item, 'title', 'Unknown')

            if item_type == 'Page':
                page_url = getattr(item, 'page_url', None)
                if page_url:
                    path = f"/courses/{course_id}/pages/{page_url}"
                else:
                    continue
            elif item_type == 'Assignment' and content_id:
                path = f"/courses/{course_id}/assignments/{content_id}"
            elif item_type == 'Discussion' and content_id:
                path = f"/courses/{course_id}/discussion_topics/{content_id}"
            elif item_type == 'Quiz' and content_id:
                path = f"/courses/{course_id}/quizzes/{content_id}"
            elif item_type == 'File' and content_id:
                path = f"/courses/{course_id}/files/{content_id}"
            else:
                continue

            resource = resource_map.get(path)
            if resource is None:
                issues.append((module.name, item_name, "references missing resource"))
            elif not resource['published']:
                issues.append((module.name, item_name, f"references unpublished {resource['type']}: \"{resource['name']}\""))

    return issues


@canvas_sak.command()
@click.argument('course_name', metavar='course')
@click.option('--active/--inactive', default=True, help="show only active courses")
@click.option('--check-links/--no-check-links', default=True, show_default=True, help="check for broken/unpublished links")
@click.option('--check-dates/--no-check-dates', default=True, show_default=True, help="check for missing due dates")
@click.option('--check-until/--no-check-until', default=True, show_default=True, help="check until-date consistency")
@click.option('--external-links/--no-external-links', default=True, show_default=True, help="check external links (HTTP requests)")
@click.option('--timeout', default=10, show_default=True, help="timeout in seconds for external link checks")
def validate_course_setup(course_name, active, check_links, check_dates,
                          check_until, external_links, timeout):
    """Validate course setup: due dates, until-date consistency, and links.

    Checks all courses matching COURSE for common setup issues.

    Examples:

        canvas-sak validate-course-setup "CS 146"

        canvas-sak validate-course-setup "CS 146" --no-check-links

        canvas-sak validate-course-setup "CS 146" --no-external-links
    """
    canvas = get_canvas_object()
    courses = get_courses(canvas, course_name, is_active=active)

    if not courses:
        error(f"no courses found matching '{course_name}'")
        sys.exit(2)

    info(f"found {len(courses)} course(s) matching '{course_name}'")

    total_issues = 0

    for course in courses:
        course_id = course.id
        output(f"\n{'=' * 60}")
        output(f"Validating: {course.name}")
        output('=' * 60)

        # Fetch assignments once if needed by either date check
        assignments = None
        if check_dates or check_until:
            assignments = list(course.get_assignments(include=['overrides']))

        # --- Due Date Check ---
        if check_dates:
            output(f"\n--- Due Date Check ---")
            missing = check_missing_due_dates(assignments)
            if missing:
                for name in missing:
                    warn(f'  WARNING: "{name}" - missing due date')
                output(f"  {len(missing)} issue(s) found")
            else:
                output(f"  [x] all assignments have due dates")
            total_issues += len(missing)

        # --- Until Date Consistency ---
        if check_until:
            output(f"\n--- Until Date Consistency ---")
            group_names = {g.id: g.name for g in course.get_assignment_groups()}
            grouped = group_assignments_by_group(assignments, group_names)
            until_issues = 0
            for group_name in sorted(grouped):
                group_assignments = grouped[group_name]
                most_common_offset, total_counted, issues = check_until_date_consistency_for_group(group_assignments)
                if most_common_offset is not None and not issues:
                    output(f"  [x] {group_name}: offset {format_timedelta(most_common_offset)} ({total_counted} assignment(s))")
                elif most_common_offset is not None:
                    output(f"  {group_name}: most common offset {format_timedelta(most_common_offset)} ({total_counted} assignment(s))")
                    for name, msg in issues:
                        warn(f'    WARNING: "{name}" - {msg}')
                    until_issues += len(issues)
                elif issues:
                    output(f"  {group_name}:")
                    for name, msg in issues:
                        warn(f'    WARNING: "{name}" - {msg}')
                    until_issues += len(issues)
            if until_issues:
                output(f"  {until_issues} issue(s) found")
            else:
                output(f"  [x] all groups consistent")
            total_issues += until_issues

        # --- Link Check ---
        if check_links:
            output(f"\n--- Link Check ---")
            info("building resource map...")
            resource_map = build_resource_map(course, course_id)
            info("collecting content...")
            content_items = collect_content_with_html(course)

            link_issues = 0
            ext_cache = {}

            for source_type, source_name, html in content_items:
                links = extract_links(html)
                for tag, attr, url in links:
                    category, normalized = classify_link(url, canvas_url, course_id)

                    if category == 'skip':
                        continue
                    elif category == 'internal':
                        resource = resource_map.get(normalized)
                        if resource is None:
                            warn(f'  WARNING: {source_type}: "{source_name}" -> {normalized} - not found')
                            link_issues += 1
                        elif not resource['published']:
                            warn(f'  WARNING: {source_type}: "{source_name}" -> {normalized} - unpublished')
                            link_issues += 1
                    elif category == 'internal_other':
                        warn(f'  WARNING: {source_type}: "{source_name}" -> {url} - cross-course link (cannot verify)')
                        link_issues += 1
                    elif category == 'external' and external_links:
                        ok, msg = check_external_link(url, timeout, ext_cache)
                        if not ok:
                            warn(f'  WARNING: {source_type}: "{source_name}" -> {url} - {msg}')
                            link_issues += 1

            # Check module items
            info("checking module items...")
            module_issues = check_module_items(course, course_id, resource_map)
            for module_name, item_name, msg in module_issues:
                warn(f'  WARNING: Module "{module_name}": "{item_name}" - {msg}')
            link_issues += len(module_issues)

            if link_issues:
                output(f"  {link_issues} issue(s) found")
            else:
                output(f"  [x] all links valid")
            total_issues += link_issues

    if total_issues:
        output(f"\nSummary: {total_issues} issue(s) found across {len(courses)} course(s)")
    else:
        output(f"\nSummary: [x] no issues found across {len(courses)} course(s)")
