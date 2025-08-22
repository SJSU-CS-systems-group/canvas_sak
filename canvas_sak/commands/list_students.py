from canvas_sak.core import *

@canvas_sak.command()
@click.argument('course')
@click.option('--active/--inactive', default=True, help="show only active courses")
@click.option('--emails/--no-emails', help="list student emails")
@click.option('--id/--no-id', help="include the canvas id")
@click.option('--link', help="show value of a link field (* for everything)", default=None)
def list_students(course, active, emails, link, id):
    '''list the students in a course'''
    if link:
        link = link.lower()
    canvas = get_canvas_object()
    course = get_course(canvas, course, active)
    users = course.get_users(include=["enrollments"])
    for user in users:
        initial_info = ""
        additional_info = ""
        if id:
            initial_info += f"{user.login_id}\t"
        if emails or link:
            profile = user.get_profile(include=["links"])
            additional_info += f"\t{profile['primary_email'] if emails else ''}"
            if link:
                link_info = "\t" + " ".join([f"{m['title']}={m['url']}" for m in profile['links'] if m['title'].lower() == link or link == '*'])
                additional_info += link_info
        output(f"{initial_info}{user.name}{additional_info}")

