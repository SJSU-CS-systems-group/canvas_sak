"""Tests for list-grades helpers."""

from canvas_sak.commands.list_grades import (
    student_matches,
    format_rubric_scores,
)


class TestStudentMatches:
    def test_no_filters_matches_everyone(self):
        assert student_matches("alice", "Alice Smith", None, None) is True

    def test_name_substring_case_insensitive(self):
        assert student_matches("alice", "Alice Smith", "alice", None) is True
        assert student_matches("bob", "Bob Jones", "ALICE", None) is False
        assert student_matches("carol", "Carol Danvers", "DANVER", None) is True

    def test_name_substring_in_middle(self):
        assert student_matches("frank", "Frank von Helsing", "von", None) is True

    def test_id_exact_match(self):
        assert student_matches("alice123", "Alice", None, "alice123") is True
        assert student_matches("alice123", "Alice", None, "alice") is False

    def test_id_filter_with_no_login_id(self):
        assert student_matches(None, "Alice", None, "alice123") is False

    def test_both_filters_must_match(self):
        assert student_matches("bob42", "Bob Jones", "bob", "bob42") is True
        assert student_matches("bob42", "Bob Jones", "alice", "bob42") is False
        assert student_matches("bob42", "Bob Jones", "bob", "alice99") is False


class TestFormatRubricScores:
    def test_empty_assessment_returns_empty_string(self):
        assert format_rubric_scores({}, {"crit1": "Code quality"}) == ""
        assert format_rubric_scores(None, {"crit1": "Code quality"}) == ""

    def test_renders_descriptions_with_points(self):
        assessment = {
            "crit1": {"points": 8.0},
            "crit2": {"points": 5.0},
        }
        criteria = {"crit1": "Code quality", "crit2": "Tests"}
        result = format_rubric_scores(assessment, criteria)
        assert "Code quality=8.0" in result
        assert "Tests=5.0" in result

    def test_falls_back_to_id_when_description_missing(self):
        assessment = {"crit_unknown": {"points": 3.0}}
        result = format_rubric_scores(assessment, {})
        assert "crit_unknown=3.0" in result

    def test_handles_missing_points(self):
        assessment = {"crit1": {"comments": "ok"}}
        criteria = {"crit1": "Code quality"}
        result = format_rubric_scores(assessment, criteria)
        assert "Code quality=" in result

    def test_orders_by_criterion_list(self):
        """When the criteria dict is ordered, output should follow that order
        so columns line up across students."""
        assessment = {
            "c2": {"points": 2.0},
            "c1": {"points": 1.0},
        }
        criteria = {"c1": "First", "c2": "Second"}
        result = format_rubric_scores(assessment, criteria)
        assert result.index("First=1.0") < result.index("Second=2.0")
