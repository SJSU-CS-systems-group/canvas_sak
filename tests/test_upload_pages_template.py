"""Tests for page templates (styling support) in upload_canvas_course.py"""

import pytest
from canvas_sak.commands.upload_canvas_course import prepare_page


class TestPreparePage:
    """Test cases for the prepare_page function."""

    def test_page_without_template_renders_markdown(self):
        """A page with no template header renders markdown to html as before."""
        content = "title: My Page\npublished: true\n# Heading\n\nsome *text*"
        page = prepare_page(content, "/nonexistent")

        assert page['title'] == 'My Page'
        assert page['published'] == 'true'
        assert '<h1>Heading</h1>' in page['body']
        assert '<em>text</em>' in page['body']

    def test_template_wraps_body(self, tmp_path):
        """The rendered markdown replaces $body in the template."""
        (tmp_path / "templates").mkdir()
        (tmp_path / "templates" / "plain.html").write_text(
            '<div class="fancy">$body</div>')
        content = "title: My Page\ntemplate: templates/plain.html\nhello *world*"
        page = prepare_page(content, str(tmp_path))

        assert page['body'].startswith('<div class="fancy">')
        assert page['body'].endswith('</div>')
        assert '<em>world</em>' in page['body']

    def test_template_variables_from_headers(self, tmp_path):
        """Placeholders in the template become recognized page header keys."""
        (tmp_path / "banner.html").write_text(
            '<p>$kicker</p><h1>$heading</h1><em>${tagline}</em>$body')
        content = ("title: Intro Study Guide\n"
                   "template: banner.html\n"
                   "kicker: Study Guide - Module 1\n"
                   "heading: Introduction\n"
                   "tagline: First steps.\n"
                   "the body")
        page = prepare_page(content, str(tmp_path))

        assert '<p>Study Guide - Module 1</p>' in page['body']
        assert '<h1>Introduction</h1>' in page['body']
        assert '<em>First steps.</em>' in page['body']
        assert 'the body' in page['body']
        # variable lines are headers, not body content
        assert 'kicker:' not in page['body']

    def test_missing_template_variable_defaults_to_empty(self, tmp_path):
        """A placeholder with no matching header substitutes an empty string."""
        (tmp_path / "t.html").write_text('<h1>$heading</h1>$body')
        content = "title: My Page\ntemplate: t.html\nbody text"
        page = prepare_page(content, str(tmp_path))

        assert '<h1></h1>' in page['body']
        assert '$heading' not in page['body']

    def test_template_can_use_title(self, tmp_path):
        """$title in a template substitutes the page title."""
        (tmp_path / "t.html").write_text('<h1>$title</h1>$body')
        content = "title: My Page\ntemplate: t.html\nbody text"
        page = prepare_page(content, str(tmp_path))

        assert '<h1>My Page</h1>' in page['body']

    def test_template_keys_not_sent_to_canvas(self, tmp_path):
        """template and custom variable keys must not appear in the page dict."""
        (tmp_path / "t.html").write_text('<p>$kicker</p>$body')
        content = ("title: My Page\ntemplate: t.html\nkicker: hi\nbody text")
        page = prepare_page(content, str(tmp_path))

        assert 'template' not in page
        assert 'kicker' not in page
        assert set(page) == {'title', 'body'}

    def test_literal_dollars_preserved(self, tmp_path):
        """$$ escapes a dollar sign; a lone $ that isn't a placeholder survives."""
        (tmp_path / "t.html").write_text('cost: $$5 or $ 5\n$body')
        content = "title: My Page\ntemplate: t.html\nbody text"
        page = prepare_page(content, str(tmp_path))

        assert 'cost: $5 or $ 5' in page['body']

    def test_variable_line_without_template_stays_in_body(self):
        """Without a template declaring it, an unknown key line is body content."""
        content = "title: My Page\nkicker: hi\nbody text"
        page = prepare_page(content, "/nonexistent")

        assert 'kicker: hi' in page['body']

    def test_variable_not_in_template_stops_header_parsing(self, tmp_path):
        """A key line the template does not declare is body, not a header."""
        (tmp_path / "t.html").write_text('<p>$kicker</p>$body')
        content = "title: My Page\ntemplate: t.html\nother: hi\nbody text"
        page = prepare_page(content, str(tmp_path))

        assert 'other: hi' in page['body']

    def test_missing_template_file_raises(self, tmp_path):
        """A template header naming a missing file should raise."""
        content = "title: My Page\ntemplate: nope.html\nbody text"
        with pytest.raises(FileNotFoundError):
            prepare_page(content, str(tmp_path))
