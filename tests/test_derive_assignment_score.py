"""Tests for helper functions in derive_assignment_score.py"""

from types import SimpleNamespace

import pytest

from canvas_sak.commands.derive_assignment_score import (
    build_change_score_comment,
    find_last_manual_score,
    normalize_name,
    parse_change_score_comment,
)


class TestNormalizeName:
    def test_spaces_become_underscores(self):
        assert normalize_name("Quiz 1") == "Quiz_1"

    def test_dash_becomes_underscore(self):
        assert normalize_name("Quiz-1") == "Quiz_1"

    def test_space_dash_space_collapses(self):
        assert normalize_name("Quiz - 1") == "Quiz_1"

    def test_trailing_operators_stripped(self):
        assert normalize_name("C++") == "C"

    def test_slash_becomes_underscore(self):
        assert normalize_name("Pass/Fail") == "Pass_Fail"

    def test_star_becomes_underscore(self):
        assert normalize_name("Bonus * 2") == "Bonus_2"

    def test_multiple_spaces_collapse(self):
        assert normalize_name("Quiz   1") == "Quiz_1"

    def test_no_operators_unchanged(self):
        assert normalize_name("Midterm") == "Midterm"

    def test_underscore_input_unchanged(self):
        assert normalize_name("Quiz_1") == "Quiz_1"

    def test_mixed_operators_collapse(self):
        assert normalize_name("A - B + C") == "A_B_C"


class TestBuildChangeScoreComment:
    def test_with_previous(self):
        result = build_change_score_comment(85.0, 90.0)
        assert result == "change-score previous: 85.0 new: 90.0"

    def test_without_previous(self):
        result = build_change_score_comment(None, 90.0)
        assert result == "change-score new: 90.0"

    def test_zero_previous(self):
        result = build_change_score_comment(0, 75.0)
        assert result == "change-score previous: 0 new: 75.0"

    def test_zero_new(self):
        result = build_change_score_comment(50.0, 0)
        assert result == "change-score previous: 50.0 new: 0"

    def test_both_zero(self):
        result = build_change_score_comment(0, 0)
        assert result == "change-score previous: 0 new: 0"


class TestParseChangeScoreComment:
    def test_with_previous(self):
        result = parse_change_score_comment("change-score previous: 85.0 new: 90.0")
        assert result == (85.0, 90.0)

    def test_without_previous(self):
        result = parse_change_score_comment("change-score new: 90.0")
        assert result == (None, 90.0)

    def test_integer_values(self):
        result = parse_change_score_comment("change-score previous: 85 new: 90")
        assert result == (85.0, 90.0)

    def test_non_matching_string(self):
        result = parse_change_score_comment("this is a regular comment")
        assert result is None

    def test_none_input(self):
        result = parse_change_score_comment(None)
        assert result is None

    def test_empty_string(self):
        result = parse_change_score_comment("")
        assert result is None

    def test_roundtrip_with_previous(self):
        comment = build_change_score_comment(85.0, 90.0)
        result = parse_change_score_comment(comment)
        assert result == (85.0, 90.0)

    def test_roundtrip_without_previous(self):
        comment = build_change_score_comment(None, 90.0)
        result = parse_change_score_comment(comment)
        assert result == (None, 90.0)

    def test_roundtrip_zero_values(self):
        comment = build_change_score_comment(0, 0)
        result = parse_change_score_comment(comment)
        assert result == (0.0, 0.0)


def _make_comment(text, author_name="Tool"):
    """Helper to create a comment-like object with the structure Canvas returns."""
    return {"comment": text, "author_name": author_name}


class TestFindLastManualScore:
    def test_no_comments(self):
        result = find_last_manual_score(80.0, [])
        assert result == 80.0

    def test_no_change_score_comments(self):
        comments = [
            _make_comment("Great work!"),
            _make_comment("Resubmit please"),
        ]
        result = find_last_manual_score(80.0, comments)
        assert result == 80.0

    def test_single_match(self):
        # current score is 90, last change-score says previous was 85
        comments = [
            _make_comment("change-score previous: 85.0 new: 90.0"),
        ]
        result = find_last_manual_score(90.0, comments)
        assert result == 85.0

    def test_chain_walkback(self):
        # current=95, chain: 85->90->95, should walk back to 85
        comments = [
            _make_comment("change-score previous: 85.0 new: 90.0"),
            _make_comment("change-score previous: 90.0 new: 95.0"),
        ]
        result = find_last_manual_score(95.0, comments)
        assert result == 85.0

    def test_chain_ending_in_no_previous(self):
        # current=95, chain: None->90->95, should return None
        comments = [
            _make_comment("change-score new: 90.0"),
            _make_comment("change-score previous: 90.0 new: 95.0"),
        ]
        result = find_last_manual_score(95.0, comments)
        assert result is None

    def test_manual_change_breaks_chain(self):
        # Tool set score to 90, then teacher manually changed to 88,
        # then tool set to 95. Current score is 95.
        # The latest change-score has previous=88, which doesn't match
        # any other change-score's "new", so 88 is the manual score.
        comments = [
            _make_comment("change-score previous: 85.0 new: 90.0"),
            _make_comment("change-score previous: 88.0 new: 95.0"),
        ]
        result = find_last_manual_score(95.0, comments)
        assert result == 88.0

    def test_mixed_regular_and_change_score_comments(self):
        comments = [
            _make_comment("Good submission"),
            _make_comment("change-score previous: 70.0 new: 80.0"),
            _make_comment("Graded by instructor"),
            _make_comment("change-score previous: 80.0 new: 90.0"),
        ]
        result = find_last_manual_score(90.0, comments)
        assert result == 70.0

    def test_current_score_doesnt_match_latest_new(self):
        # Teacher manually changed from 90 (set by tool) to 85
        # Current score is 85 which doesn't match the latest "new" (90)
        # So the current score IS the manual score
        comments = [
            _make_comment("change-score previous: 75.0 new: 90.0"),
        ]
        result = find_last_manual_score(85.0, comments)
        assert result == 85.0
