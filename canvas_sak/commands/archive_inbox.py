import datetime
from datetime import timezone

import click

from canvas_sak.core import *

namedtuple("ConversationMeta", ["id", ])

@canvas_sak.command()
@click.argument('course_substring')
@click.option('--dryrun/--no-dryrun', default=True, help="show what would be done, but don't do it")
def archive_inbox(course_substring, dryrun):
    '''
    move inbox conversations for a course to the archive.
    the course can be a partial name or * for all courses.
    '''
    recent_past = datetime.datetime.now() - datetime.timedelta(minutes=60)
    canvas_recent_past = recent_past.strftime('%Y-%m-%dT%H:%M:%SZ')
    canvas = get_canvas_object()
    to_archive = []
    archive_count = 0
    skipped_count = 0
    course_substring = course_substring.lower()
    archive_contexts = set()
    for c in canvas.get_conversations():
        if c.last_message_at > canvas_recent_past:
            continue

        if c.context_name and (course_substring == '*' or course_substring in c.context_name.lower()):
            archive_count += 1
            to_archive = to_archive + [c.id]
            archive_contexts.add(c.context_name)
        else:
            skipped_count += 1
        click.echo(f"\rto archive {archive_count} skipped {skipped_count}   ", nl=False)
    click.echo()
    sorted_contexts = list(archive_contexts)
    sorted_contexts.sort()
    if sorted_contexts:
        click.echo("archiving conversations for these contexts:")
    for context in sorted_contexts:
        click.echo(context)
    if dryrun:
        click.echo("this was a dry run, so no conversations were archived")
    else:
        if to_archive:
            click.echo(f"archiving {len(to_archive)} conversations")
            chunk_size = 100
            for r in range(0, len(to_archive), chunk_size):
                chunk = to_archive[r:r+chunk_size]
                click.echo (f"archiving {len(chunk)} conversations")
                canvas.conversations_batch_update(conversation_ids=chunk, event='archive')
        else:
            click.echo("no conversations to archive")