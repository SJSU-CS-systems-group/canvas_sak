"""Tests for despace in core."""

from canvas_sak.core import despace


class TestDespace:
    def test_single_space_becomes_underscore(self):
        assert despace("Homework 1") == "Homework_1"

    def test_multiple_spaces_each_become_underscore(self):
        assert despace("a b c") == "a_b_c"

    def test_tab_becomes_underscore(self):
        assert despace("a\tb") == "a_b"

    def test_newline_becomes_underscore(self):
        assert despace("a\nb") == "a_b"

    def test_carriage_return_becomes_underscore(self):
        assert despace("a\rb") == "a_b"

    def test_mixed_whitespace(self):
        assert despace("a \t\nb") == "a___b"

    def test_no_whitespace_unchanged(self):
        assert despace("already-clean") == "already-clean"

    def test_empty_string(self):
        assert despace("") == ""

    def test_leading_and_trailing_whitespace(self):
        assert despace(" hi ") == "_hi_"
