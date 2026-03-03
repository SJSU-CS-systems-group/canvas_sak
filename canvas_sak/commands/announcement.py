import re
import sys

import click

from canvas_sak.core import *
from canvas_sak.md2fhtml import html2mdstr, md2htmlstr


def parse_since(s):
    """Parse a duration string like '1d', '2w', '3m' into a timedelta."""
    m = re.fullmatch(r'(\d+)([dwm])', s)
    if not m:
        raise click.BadParameter(f"invalid duration '{s}', use e.g. 1d, 2w, 3m")
    n = int(m.group(1))
    unit = m.group(2)
    if unit == 'd':
        return datetime.timedelta(days=n)
    elif unit == 'w':
        return datetime.timedelta(weeks=n)
    elif unit == 'm':
        return datetime.timedelta(days=n * 30)


def linkify_urls(text):
    """Convert bare URLs to markdown autolinks (<url>).

    Skips URLs already inside [text](url) or <url> syntax.
    """
    return re.sub(
        r'(?<!\()(?<![<\[])https?://\S+',
        lambda m: f'<{m.group(0)}>',
        text
    )


@canvas_sak.group()
def announcement():
    '''manage course announcements'''


@announcement.command(name='list')
@click.argument('course_name', metavar='COURSE')
@click.option('--comments', is_flag=True, default=False,
              help='show replies/comments on each announcement')
@click.option('--contents', is_flag=True, default=False,
              help='display the contents of each announcement')
@click.option('--since', default='1w', show_default=True,
              help='how far back to list (e.g. 1d, 2w, 3m)')
@click.option('--date', 'on_date', default=None,
              help='show announcements from a specific date (YYYY-MM-DD)')
def list_announcements(course_name, comments, contents, since, on_date):
    '''list recent announcements'''
    canvas = get_canvas_object()
    course = get_course(canvas, course_name)
    now = datetime.datetime.now(datetime.timezone.utc)

    if on_date:
        try:
            d = datetime.date.fromisoformat(on_date)
        except ValueError:
            error(f"invalid date '{on_date}', use YYYY-MM-DD")
            sys.exit(2)
        start_date = datetime.datetime.combine(d, datetime.time.min, tzinfo=datetime.timezone.utc)
        end_date = datetime.datetime.combine(d, datetime.time.max, tzinfo=datetime.timezone.utc)
    else:
        delta = parse_since(since)
        start_date = now - delta
        end_date = now

    topics = canvas.get_announcements(
        context_codes=[f'course_{course.id}'],
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
    )

    found = False
    for topic in topics:
        found = True
        posted = topic.posted_at or ''
        if posted:
            posted = posted[:10]
        output(f"{posted}\t{topic.title}")
        if contents:
            body = getattr(topic, 'message', '') or ''
            if body:
                output(html2mdstr(body).strip())
                output('')
        if comments:
            try:
                for entry in topic.get_topic_entries():
                    author = getattr(entry, 'user_name', 'unknown')
                    message = getattr(entry, 'message', '')
                    output(f"  {author}: {message}")
            except Exception:
                pass

    if not found:
        output("no announcements found")


@announcement.command()
@click.argument('course_name', metavar='COURSE')
@click.option('--subject', required=True, help='announcement title')
@click.option('--message', default=None,
              help='announcement body in markdown (reads stdin if omitted)')
def post(course_name, subject, message):
    '''post an announcement'''
    canvas = get_canvas_object()
    course = get_course(canvas, course_name)

    if message is None:
        message = sys.stdin.read()

    message = linkify_urls(message)
    html = md2htmlstr(message)

    course.create_discussion_topic(
        title=subject,
        message=html,
        is_announcement=True,
    )
    info(f"posted announcement: {subject}")
