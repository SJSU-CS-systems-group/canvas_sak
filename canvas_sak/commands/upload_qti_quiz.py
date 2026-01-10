import time

import click

from canvas_sak.core import *


@canvas_sak.command()
@click.argument('course_name', metavar='course')
@click.argument('qti_file', type=click.Path(exists=True))
@click.option('--wait/--no-wait', default=True, show_default=True,
              help="wait for the import to complete")
@click.option('--poll-interval', default=2, show_default=True,
              help="seconds between status checks when waiting")
def upload_qti_quiz(course_name, qti_file, wait, poll_interval):
    """Upload a QTI quiz package to a Canvas course.

    QTI_FILE should be a zip file containing a QTI-formatted quiz.
    """
    canvas = get_canvas_object()
    course = get_course(canvas, course_name)
    output(f"uploading QTI quiz to {course.name}")

    # Create content migration for QTI import
    migration = course.create_content_migration(
        migration_type='qti_converter',
        pre_attachment={
            'name': os.path.basename(qti_file),
        }
    )

    # Upload the QTI file
    info(f"uploading {qti_file}...")
    upload_url = migration.pre_attachment['upload_url']
    upload_params = migration.pre_attachment['upload_params']

    with open(qti_file, 'rb') as f:
        files = {'file': (os.path.basename(qti_file), f)}
        response = requests.post(upload_url, data=upload_params, files=files)

    if response.status_code not in [200, 201, 301, 303]:
        error(f"failed to upload file: {response.status_code} {response.text}")
        sys.exit(1)

    info("file uploaded, processing migration...")

    if wait:
        # Poll for migration completion
        while True:
            migration = course.get_content_migration(migration.id)
            status = migration.workflow_state

            if status == 'completed':
                info("quiz import completed successfully")
                break
            elif status == 'failed':
                error(f"quiz import failed: {getattr(migration, 'migration_issues', 'unknown error')}")
                sys.exit(1)
            elif status in ['pre_processing', 'pre_processed', 'running', 'queued', 'exporting']:
                output(f"status: {status}...")
                time.sleep(poll_interval)
            else:
                warn(f"unexpected status: {status}")
                time.sleep(poll_interval)
    else:
        output(f"migration started with id {migration.id}")
        output("use Canvas to check migration status")
