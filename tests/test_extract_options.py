"""Tests for extract_options in upload_canvas_course."""

from canvas_sak.commands.upload_canvas_course import extract_options


class TestExtractOptions:
    def test_simple_key_value(self):
        assert extract_options("k=v") == {"k": "v"}

    def test_value_contains_equals_sign(self):
        """Bug repro: split('=', 2) used to drop the trailing 'b' from
        'url=https://x?a=b'. With split('=', 1) the full value is preserved."""
        result = extract_options("url=https://x?a=b")
        assert result == {"url": "https://x?a=b"}

    def test_key_only_becomes_empty_value(self):
        assert extract_options("flag") == {"flag": ""}

    def test_multiple_options_semicolon_separated(self):
        assert extract_options("a=1;b=2;c=3") == {"a": "1", "b": "2", "c": "3"}

    def test_lowercases_key_and_strips_whitespace(self):
        assert extract_options(" Foo = bar ") == {"foo": "bar"}
