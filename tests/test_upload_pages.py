"""Tests for the upload_pages force-update path in upload_canvas_course.py"""

import os
from unittest.mock import MagicMock, patch

from canvas_sak import core
from canvas_sak.commands.upload_canvas_course import upload_pages


def make_pages_dir(tmp_path):
    pages = tmp_path / "pages"
    pages.mkdir()
    (pages / "p.md").write_text("title: My Page\nsome *body* text")
    return pages


class TestUploadPagesForce:
    """Canvas silently ignores unwrapped params on PUT /pages; the update
    must send the attributes wrapped in wiki_page."""

    def test_force_update_wraps_attributes_in_wiki_page(self, tmp_path):
        pages = make_pages_dir(tmp_path)
        mock_page = MagicMock()
        course = MagicMock()
        course.get_page.return_value = mock_page
        record = core.ResourceRecord(1, "my-page", "Page", "My Page", False)

        with patch.dict(core.rr4name, {"PageMy Page": record}, clear=True):
            upload_pages(course, str(pages), dryrun=False, force=True)

        course.get_page.assert_called_once_with("my-page")
        assert mock_page.edit.call_count == 1
        kwargs = mock_page.edit.call_args.kwargs
        assert set(kwargs) == {"wiki_page"}
        assert kwargs["wiki_page"]["title"] == "My Page"
        assert "<em>body</em>" in kwargs["wiki_page"]["body"]

    def test_force_dryrun_does_not_edit(self, tmp_path):
        pages = make_pages_dir(tmp_path)
        mock_page = MagicMock()
        course = MagicMock()
        course.get_page.return_value = mock_page
        record = core.ResourceRecord(1, "my-page", "Page", "My Page", False)

        with patch.dict(core.rr4name, {"PageMy Page": record}, clear=True):
            upload_pages(course, str(pages), dryrun=True, force=True)

        assert course.get_page.call_count == 0
        assert mock_page.edit.call_count == 0


def make_image_pages_dir(tmp_path, image_ref="shot.png"):
    pages = tmp_path / "pages"
    pages.mkdir()
    (pages / "p.md").write_text(f"title: My Page\nlook at ![a screenshot]({image_ref})")
    (pages / "shot.png").write_bytes(b"\x89PNG\r\n\x1a\nnot really a png")
    return pages


class TestUploadPagesImages:
    """Pages reference image files relative to the page's .md file; the upload
    resolves those references to canvas file links, uploading the image to the
    course files when it isn't already there."""

    def test_relative_image_uploaded_and_src_rewritten(self, tmp_path):
        pages = make_image_pages_dir(tmp_path)
        course = MagicMock()
        course.id = 99
        course.upload.return_value = (True, {"id": 42, "url": "https://canvas.test/files/42/download?verifier=v"})

        with patch.dict(core.rr4name, {}, clear=True):
            upload_pages(course, str(pages), dryrun=False, force=False)

        # the image file itself must not be treated as a page
        assert course.create_page.call_count == 1
        course.upload.assert_called_once_with(
            os.path.join(str(pages), "shot.png"), parent_folder_path="", name="shot.png")
        body = course.create_page.call_args.args[0]["body"]
        assert 'src="/courses/99/files/42/preview"' in body

    def test_image_already_in_course_files_is_reused(self, tmp_path):
        pages = make_image_pages_dir(tmp_path)
        course = MagicMock()
        course.id = 99
        record = core.ResourceRecord(42, "https://canvas.test/files/42/download", "File",
                                     "course files/shot.png", False)

        with patch.dict(core.rr4name, {"Filecourse files/shot.png": record}, clear=True):
            upload_pages(course, str(pages), dryrun=False, force=False)

        assert course.upload.call_count == 0
        body = course.create_page.call_args.args[0]["body"]
        assert 'src="/courses/99/files/42/preview"' in body

    def test_external_and_absolute_srcs_left_alone(self, tmp_path):
        pages = tmp_path / "pages"
        pages.mkdir()
        (pages / "p.md").write_text("title: My Page\n"
                                    "![a](https://elsewhere.test/pic.png) "
                                    "![b](/courses/1/files/2/preview)")
        course = MagicMock()
        course.id = 99

        with patch.dict(core.rr4name, {}, clear=True):
            upload_pages(course, str(pages), dryrun=False, force=False)

        assert course.upload.call_count == 0
        body = course.create_page.call_args.args[0]["body"]
        assert 'src="https://elsewhere.test/pic.png"' in body
        assert 'src="/courses/1/files/2/preview"' in body

    def test_missing_image_left_alone(self, tmp_path):
        pages = make_image_pages_dir(tmp_path, image_ref="gone.png")
        course = MagicMock()
        course.id = 99

        with patch.dict(core.rr4name, {}, clear=True):
            upload_pages(course, str(pages), dryrun=False, force=False)

        assert course.upload.call_count == 0
        body = course.create_page.call_args.args[0]["body"]
        assert 'src="gone.png"' in body

    def test_dryrun_does_not_upload_image(self, tmp_path):
        pages = make_image_pages_dir(tmp_path)
        course = MagicMock()
        course.id = 99

        with patch.dict(core.rr4name, {}, clear=True):
            upload_pages(course, str(pages), dryrun=True, force=False)

        assert course.upload.call_count == 0
        assert course.create_page.call_count == 0
