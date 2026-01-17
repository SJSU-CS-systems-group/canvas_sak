from canvas_sak.core import *


@canvas_sak.command()
@click.argument('course_name', metavar='course')
@click.argument('image', metavar='image', required=False)
@click.option('--remove', is_flag=True, default=False, help="remove the course image instead of setting it")
def set_course_image(course_name, image, remove):
    """Set or remove the course image.

    IMAGE can be a local file path or a URL. If it's a local file, it will be
    uploaded to Canvas first. If it's a URL, it will be set directly.

    Examples:

        canvas-sak set-course-image "My Course" ./banner.jpg

        canvas-sak set-course-image "My Course" https://example.com/image.jpg

        canvas-sak set-course-image "My Course" --remove
    """
    if not remove and not image:
        error("IMAGE is required when not using --remove")
        sys.exit(1)

    canvas = get_canvas_object()
    course = get_course(canvas, course_name, is_active=False)
    info(f"found {course.name}")

    if remove:
        info("removing course image")
        course.update(course={"remove_image": True})
        output("course image removed")
        return

    # Check if image is a URL or a file path
    if image.startswith("http://") or image.startswith("https://"):
        # It's a URL, set it directly
        info(f"setting course image to URL: {image}")
        course.update(course={"image_url": image})
        output("course image set from URL")
    else:
        # It's a file path, upload it first
        if not os.path.exists(image):
            error(f"file not found: {image}")
            sys.exit(1)

        info(f"uploading {image}")
        success, response = course.upload(image)
        if not success:
            error("failed to upload image")
            sys.exit(1)

        # Get the file ID from the response
        if isinstance(response, dict):
            file_id = response['id']
        else:
            file_id = response.id

        info(f"setting course image to uploaded file (id={file_id})")
        course.update(course={"image_id": file_id})
        output("course image set from uploaded file")
