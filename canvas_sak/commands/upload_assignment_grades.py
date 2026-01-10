import csv
from importlib.metadata import requires

from canvas_sak.core import *

@canvas_sak.command()
@click.argument("course")
@click.argument("assignment")
@click.option("--file", type=click.File('r'), required=True)
@click.option("--id", required=True, help="field number (0-based) in the file that contains the ID")
@click.option("--grade", required=True, help="field number (0-based) in the file that contains the grade")
@click.option("--free-points", default=0.0, help="points to add to the score.")
@click.option("--dryrun/--no-dryrun", default=True)
def upload_assignment_grades(course, assignment, file, id, grade, free_points, dryrun):
    ''' upload grades for an assignment from a CSV file.
    '''

    canvas = get_canvas_object()
    course = get_course(canvas, course)

    assignment = get_assignment(course, assignment)
    if not assignment:
        error(f'{assignment} hasn\'t been set up')
        exit(2)

    grades = {}
    csv_reader = csv.reader(file)
    next(csv_reader)  # skip header
    for row in csv_reader:
        student_id = row[int(id)].strip()
        student_grade = row[int(grade)].strip()
        if not student_id or not student_grade:
            print(f"skipping empty id or grade: '{student_id}' '{student_grade}' in {row}")
        student_grade = student_grade.rstrip("%")
        student_grade = min(100.00, float(student_grade) + free_points)
        grades[student_id] = student_grade

    user_id_2_sis = {}
    for enrollment in course.get_enrollments(include = ["user", "sis_user_id"]):
        user_id_2_sis[enrollment.user['id']] = enrollment.sis_user_id

    if dryrun:
        for submission in assignment.get_submissions():
            sis = user_id_2_sis[submission.user_id] if submission.user_id in user_id_2_sis else None
            if sis in grades:
                score = grades[sis]
                info(f"{score} {sis}")
            else:
                warn(f"no grade found for {sis}")
        warn("This was a dryrun. Nothing has been updated")
    else:
        with click.progressbar(length=len(grades), label="updating grades", show_pos=True) as bar:
            for submission in assignment.get_submissions():
                sis = user_id_2_sis[submission.user_id] if submission.user_id in user_id_2_sis else None
                if sis in grades:
                    score = grades[sis]
                    submission.edit(submission={'posted_grade': score})
                    bar.update(1)
                else:
                    warn(f"no grade found for {sis}")
