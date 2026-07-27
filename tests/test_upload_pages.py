"""Tests for the upload_pages force-update path in upload_canvas_course.py"""

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
