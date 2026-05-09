"""Tests for rubric association filtering in rubrics.py"""

from canvas_sak.commands.rubrics import filter_assignment_associations


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
