"""Tests for rubric association filtering in rubrics.py"""

from types import SimpleNamespace

from canvas_sak.commands.rubrics import (
    filter_assignment_associations,
    find_rubrics_by_name,
    format_rubric_lines,
    parse_rubrics_file,
)


class TestFilterAssignmentAssociations:
    def test_includes_assignment_associations_when_use_for_grading_is_false(self):
        """Bug repro: Canvas returns Assignment associations with use_for_grading=False
        even though the rubric is attached to the assignments. They must still be listed."""
        associations = [
            {'association_type': 'Assignment', 'association_id': 1, 'use_for_grading': False},
            {'association_type': 'Assignment', 'association_id': 2, 'use_for_grading': False},
            {'association_type': 'Assignment', 'association_id': 3, 'use_for_grading': False},
        ]
        result = filter_assignment_associations(associations)
        assert [a['association_id'] for a in result] == [1, 2, 3]

    def test_includes_assignment_associations_when_use_for_grading_is_true(self):
        associations = [
            {'association_type': 'Assignment', 'association_id': 1, 'use_for_grading': True},
        ]
        result = filter_assignment_associations(associations)
        assert [a['association_id'] for a in result] == [1]

    def test_excludes_non_assignment_association_types(self):
        associations = [
            {'association_type': 'Course', 'association_id': 99, 'use_for_grading': False},
            {'association_type': 'Assignment', 'association_id': 1, 'use_for_grading': False},
        ]
        result = filter_assignment_associations(associations)
        assert [a['association_id'] for a in result] == [1]

    def test_handles_empty_list(self):
        assert filter_assignment_associations([]) == []


class TestFindRubricsByName:
    rubrics = [
        SimpleNamespace(title='Project Rubric'),
        SimpleNamespace(title='project rubric (old)'),
        SimpleNamespace(title='Essay Rubric'),
    ]

    def test_exact_match_wins_over_partial_matches(self):
        result = find_rubrics_by_name(self.rubrics, 'Project Rubric')
        assert [r.title for r in result] == ['Project Rubric']

    def test_partial_match_is_case_insensitive(self):
        result = find_rubrics_by_name(self.rubrics, 'essay')
        assert [r.title for r in result] == ['Essay Rubric']

    def test_ambiguous_partial_match_returns_all_matches(self):
        result = find_rubrics_by_name(self.rubrics, 'project')
        assert [r.title for r in result] == ['Project Rubric', 'project rubric (old)']

    def test_no_match_returns_empty_list(self):
        assert find_rubrics_by_name(self.rubrics, 'quiz') == []


class TestFormatRubricLines:
    def test_round_trips_through_parse_rubrics_file(self):
        """The displayed rubric must be usable as-is with --update-with."""
        lines = format_rubric_lines('Project Rubric', 20, ['hw1', 'hw2'])
        parsed = parse_rubrics_file(lines)
        assert parsed == [('Project Rubric', ['hw1', 'hw2'])]

    def test_round_trips_with_float_points(self):
        lines = format_rubric_lines('Project Rubric', 20.0, ['hw1'])
        parsed = parse_rubrics_file(lines)
        assert parsed == [('Project Rubric', ['hw1'])]

    def test_round_trips_without_points(self):
        lines = format_rubric_lines('Project Rubric', 'N/A', ['hw1'])
        parsed = parse_rubrics_file(lines)
        assert parsed == [('Project Rubric', ['hw1'])]

    def test_rubric_with_no_assignments_still_parses(self):
        lines = format_rubric_lines('Project Rubric', 20, [])
        parsed = parse_rubrics_file(lines)
        assert parsed == [('Project Rubric', [])]
