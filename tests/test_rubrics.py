"""Tests for rubric association filtering in rubrics.py"""

from types import SimpleNamespace

from canvas_sak.commands.rubrics import (
    build_criteria_param,
    filter_assignment_associations,
    find_rubrics_by_name,
    format_rubric_definition,
    is_rubric_definition_file,
    parse_rubric_definitions,
    parse_rubrics_file,
    select_rubric_definitions,
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


CRITERIA = [
    {
        'description': 'Correctness',
        'long_description': 'how well it works',
        'points': 10.0,
        'ratings': [
            {'description': 'Full marks', 'long_description': 'everything correct', 'points': 10.0},
            {'description': 'Partial: some tests fail', 'points': 5.0},
            {'description': 'No marks', 'points': 0.0},
        ],
    },
    {
        'description': 'Style',
        'points': 10.0,
        'ratings': [
            {'description': 'Good', 'points': 10.0},
            {'description': 'Poor', 'points': 0.0},
        ],
    },
]


class TestRubricDefinitionRoundTrip:
    def test_display_output_parses_back_to_same_structure(self):
        """The displayed rubric must be usable as-is with --update-with."""
        lines = format_rubric_definition('Project Rubric', 20.0, CRITERIA)
        parsed = parse_rubric_definitions(lines)
        assert len(parsed) == 1
        rubric = parsed[0]
        assert rubric['title'] == 'Project Rubric'
        assert [c['description'] for c in rubric['criteria']] == ['Correctness', 'Style']
        correctness = rubric['criteria'][0]
        assert correctness['points'] == 10.0
        assert correctness['long_description'] == 'how well it works'
        assert [(r['description'], r['points']) for r in correctness['ratings']] == [
            ('Full marks', 10.0),
            ('Partial: some tests fail', 5.0),
            ('No marks', 0.0),
        ]
        assert correctness['ratings'][0]['long_description'] == 'everything correct'
        style = rubric['criteria'][1]
        assert 'long_description' not in style
        assert len(style['ratings']) == 2

    def test_multiple_rubrics_in_one_file(self):
        lines = (format_rubric_definition('Rubric A', 10, CRITERIA[:1])
                 + format_rubric_definition('Rubric B', 10, CRITERIA[1:]))
        parsed = parse_rubric_definitions(lines)
        assert [r['title'] for r in parsed] == ['Rubric A', 'Rubric B']

    def test_rubric_without_points_round_trips(self):
        lines = format_rubric_definition('Project Rubric', 'N/A', CRITERIA)
        parsed = parse_rubric_definitions(lines)
        assert parsed[0]['title'] == 'Project Rubric'
        assert len(parsed[0]['criteria']) == 2


class TestIsRubricDefinitionFile:
    def test_definition_file_is_detected(self):
        lines = format_rubric_definition('Project Rubric', 20, CRITERIA)
        assert is_rubric_definition_file(lines)

    def test_association_file_is_not_a_definition_file(self):
        lines = ['Project Rubric (20 pts)', '  - hw1', '  - hw2']
        assert not is_rubric_definition_file(lines)
        # and it still parses as an association file
        assert parse_rubrics_file(lines) == [('Project Rubric', ['hw1', 'hw2'])]


class TestSelectRubricDefinitions:
    definitions = [
        {'title': 'Project Rubric', 'criteria': []},
        {'title': 'project rubric (old)', 'criteria': []},
        {'title': 'Essay Rubric', 'criteria': []},
    ]

    def test_single_definition_is_used_regardless_of_name(self):
        only = [{'title': 'Renamed Rubric', 'criteria': []}]
        assert select_rubric_definitions(only, 'Project Rubric') == only

    def test_exact_title_match_wins_over_partial(self):
        result = select_rubric_definitions(self.definitions, 'Project Rubric')
        assert [d['title'] for d in result] == ['Project Rubric']

    def test_partial_match_is_case_insensitive(self):
        result = select_rubric_definitions(self.definitions, 'essay')
        assert [d['title'] for d in result] == ['Essay Rubric']

    def test_ambiguous_partial_match_returns_all(self):
        result = select_rubric_definitions(self.definitions, 'project')
        assert [d['title'] for d in result] == ['Project Rubric', 'project rubric (old)']

    def test_no_match_returns_empty_list(self):
        assert select_rubric_definitions(self.definitions, 'quiz') == []


class TestBuildCriteriaParam:
    def test_builds_indexed_hashes_for_canvas_api(self):
        param = build_criteria_param(CRITERIA)
        assert list(param.keys()) == ['0', '1']
        assert param['0']['description'] == 'Correctness'
        assert param['0']['long_description'] == 'how well it works'
        assert param['0']['points'] == 10.0
        assert list(param['0']['ratings'].keys()) == ['0', '1', '2']
        assert param['0']['ratings']['1'] == {
            'description': 'Partial: some tests fail',
            'long_description': '',
            'points': 5.0,
        }
        assert param['1']['long_description'] == ''
