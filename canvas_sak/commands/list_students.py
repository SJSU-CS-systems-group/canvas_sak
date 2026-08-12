from canvas_sak.core import *

def format_sections(enrollments, section_names):
    '''return a comma separated list of section names for a user's enrollments'''
    seen = []
    for enrollment in enrollments or []:
        section_id = enrollment.get('course_section_id')
        if section_id is None:
            continue
        name = section_names.get(section_id, str(section_id))
        if name not in seen:
            seen.append(name)
    return ", ".join(seen)

@canvas_sak.command()
@click.argument('course')
@click.option('--active/--inactive', default=True, help="show only active courses")
@click.option('--emails/--no-emails', help="list student emails")
@click.option('--id/--no-id', help="include the canvas id")
@click.option('--link', help="show value of a link field (* for everything)", default=None)
@click.option('--sections/--no-sections', help="list the sections the students are in")
def list_students(course, active, emails, link, id, sections):
    '''list the students in a course'''
    if link:
        link = link.lower()
    canvas = get_canvas_object()
    course = get_course(canvas, course, active)
    section_names = {s.id: s.name for s in course.get_sections()} if sections else {}
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
        if sections:
            additional_info += f"\t{format_sections(getattr(user, 'enrollments', None), section_names)}"
        output(f"{initial_info}{user.name}{additional_info}")

