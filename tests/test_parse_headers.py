"""Tests for header parsing in upload_canvas_course.py"""

import pytest
from canvas_sak.commands.upload_canvas_course import (
    parse_headers,
    PAGE_KEYWORDS,
    DISCUSSION_KEYWORDS,
)


class TestParseHeaders:
    """Test cases for the parse_headers function."""

    def test_valid_keywords_parsed_correctly(self):
        """Valid keywords should be extracted into the headers dict."""
        content = "published: true\ntitle: My Page\nThis is the body content."
        headers, body = parse_headers(content, PAGE_KEYWORDS)

        assert headers['published'] == 'true'
        assert headers['title'] == 'My Page'
        assert body == 'This is the body content.\n'

    def test_title_does_not_stop_header_parsing(self):
        """Parsing should continue after title keyword to capture other keywords."""
        content = "title: Test Title\npublished: true\nBody text here."
        headers, body = parse_headers(content, PAGE_KEYWORDS)

        assert headers['title'] == 'Test Title'
        assert headers['published'] == 'true'  # Should be parsed, not in body
        assert body == 'Body text here.\n'

    def test_unknown_keyword_treated_as_content(self):
        """Unknown keywords should be treated as normal content, not discarded."""
        content = "unknown_key: some value\ntitle: My Title\nBody content."
        headers, body = parse_headers(content, PAGE_KEYWORDS)

        # Unknown keyword line should be preserved in body
        assert 'unknown_key' not in headers
        assert body == 'unknown_key: some value\ntitle: My Title\nBody content.'

    def test_unknown_keyword_preserves_entire_line(self):
        """The entire line with unknown keyword should be preserved in body."""
        content = "invalid: this should be in body\nMore body text."
        headers, body = parse_headers(content, PAGE_KEYWORDS)

        assert headers == {}
        assert body == 'invalid: this should be in body\nMore body text.'

    def test_all_page_keywords_recognized(self):
        """All PAGE_KEYWORDS should be recognized and parsed."""
        content = "published: true\npublish_at: 2024-01-01\nfront_page: true\ntitle: Full Page\nBody."
        headers, body = parse_headers(content, PAGE_KEYWORDS)

        assert headers['published'] == 'true'
        assert headers['publish_at'] == '2024-01-01'
        assert headers['front_page'] == 'true'
        assert headers['title'] == 'Full Page'
        assert body == 'Body.\n'

    def test_all_discussion_keywords_recognized(self):
        """All DISCUSSION_KEYWORDS should be recognized and parsed."""
        content = "published: false\npublish_at: 2024-06-15\ntitle: Discussion Topic\nMessage body."
        headers, body = parse_headers(content, DISCUSSION_KEYWORDS)

        assert headers['published'] == 'false'
        assert headers['publish_at'] == '2024-06-15'
        assert headers['title'] == 'Discussion Topic'
        assert body == 'Message body.\n'

    def test_discussion_does_not_recognize_page_only_keywords(self):
        """DISCUSSION_KEYWORDS should not include page-only keywords like front_page."""
        content = "front_page: true\ntitle: My Discussion\nBody."
        headers, body = parse_headers(content, DISCUSSION_KEYWORDS)

        # front_page is not in DISCUSSION_KEYWORDS, so it should be treated as content
        assert 'front_page' not in headers
        assert body == 'front_page: true\ntitle: My Discussion\nBody.'

    def test_colon_in_value_preserved(self):
        """Colons within the value portion should be preserved."""
        content = "title: Time: 10:30 AM\nBody content."
        headers, body = parse_headers(content, PAGE_KEYWORDS)

        assert headers['title'] == 'Time: 10:30 AM'
        assert body == 'Body content.\n'

    def test_whitespace_stripped_from_values(self):
        """Whitespace should be stripped from header values."""
        content = "title:   Lots of spaces   \nBody."
        headers, body = parse_headers(content, PAGE_KEYWORDS)

        assert headers['title'] == 'Lots of spaces'

    def test_empty_body_after_keywords(self):
        """Should handle case where there's no body content after keywords."""
        content = "title: Just a Title"
        headers, body = parse_headers(content, PAGE_KEYWORDS)

        assert headers['title'] == 'Just a Title'
        assert body == '\n'  # Empty line after headers becomes body

    def test_multiline_body_preserved(self):
        """Multiline body content should be fully preserved."""
        content = "title: My Page\nLine 1\nLine 2\nLine 3"
        headers, body = parse_headers(content, PAGE_KEYWORDS)

        assert headers['title'] == 'My Page'
        assert body == 'Line 1\nLine 2\nLine 3'

    def test_line_without_colon_treated_as_content(self):
        """Lines without colons should be treated as content."""
        content = "This line has no colon\ntitle: My Title\nBody."
        headers, body = parse_headers(content, PAGE_KEYWORDS)

        # Line without colon should start the body
        assert 'title' not in headers
        assert body == 'This line has no colon\ntitle: My Title\nBody.'

    def test_empty_content(self):
        """Should handle empty content gracefully."""
        content = ""
        headers, body = parse_headers(content, PAGE_KEYWORDS)

        assert headers == {}
        assert body == '\n'  # partition on empty string gives ('', '', '')

    def test_only_title_keyword(self):
        """Should work with only the title keyword and body."""
        content = "title: Simple\nJust body text here."
        headers, body = parse_headers(content, PAGE_KEYWORDS)

        assert headers == {'title': 'Simple'}
        assert body == 'Just body text here.\n'

    def test_case_sensitive_keywords(self):
        """Keywords should be case-sensitive."""
        content = "Title: Uppercase T\ntitle: Lowercase t\nBody."
        headers, body = parse_headers(content, PAGE_KEYWORDS)

        # 'Title' (capital T) is not in PAGE_KEYWORDS, so treated as content
        assert 'Title' not in headers
        assert body == 'Title: Uppercase T\ntitle: Lowercase t\nBody.'

    def test_custom_keywords_set(self):
        """Should work with custom keyword sets."""
        custom_keywords = {'foo', 'bar', 'title'}
        content = "foo: value1\nbar: value2\ntitle: Custom\nBody."
        headers, body = parse_headers(content, custom_keywords)

        assert headers['foo'] == 'value1'
        assert headers['bar'] == 'value2'
        assert headers['title'] == 'Custom'
        assert body == 'Body.\n'

    def test_unknown_keyword_after_valid_keywords(self):
        """Unknown keyword after valid ones should stop parsing and preserve remaining content."""
        content = "published: true\nunknown: value\ntitle: Never Reached\nBody."
        headers, body = parse_headers(content, PAGE_KEYWORDS)

        assert headers['published'] == 'true'
        assert 'unknown' not in headers
        assert 'title' not in headers
        assert body == 'unknown: value\ntitle: Never Reached\nBody.'
