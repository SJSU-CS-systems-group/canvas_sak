from canvas_sak.core import *

@canvas_sak.command()
@click.argument("course")
@click.argument("csv_output_file", type=click.File("w"))
def export_letter_grade(course, csv_output_file):
    ''' export course letter grade to CSV

    the "Reported Letter Grade" column must be setup in the gradebook.
    this command will pull down the letter grades from that column an print a CSV record
    with the student id and the corresponding letter grade.
    output will got to the indicated csv_output_file.
    an output file name of - will go to stdout.
    '''

    canvas = get_canvas_object()
    course = get_course(canvas, course)

    rlg_assignment = get_assignment(course, "Reported Letter Grade")

    user_id_to_sis, _ = build_sis_maps(course)

    count = 0
    csv_output_file.write("Student ID,Grade\n")
    for submission in rlg_assignment.get_submissions():
        sis = user_id_to_sis.get(submission.user_id)
        if sis:
            csv_output_file.write(f"{sis}, {submission.grade}\n")
            count += 1

    info(f"{count} records written to {csv_output_file.name}")

