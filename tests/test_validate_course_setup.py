"""Tests for pure functions in validate_course_setup.py"""

import datetime
from types import SimpleNamespace

import pytest

from canvas_sak.commands.validate_course_setup import (
    check_missing_due_dates,
    check_until_date_consistency_for_group,
    classify_link,
    extract_links,
    format_timedelta,
    group_assignments_by_group,
    parse_iso_date,
)


def make_assignment(name, due_at=None, lock_at=None, submission_types=None,
                    assignment_group_id=1):
    """Helper to create assignment-like objects."""
    if submission_types is None:
        submission_types = ['online_upload']
    return SimpleNamespace(
        name=name,
        due_at=due_at,
        lock_at=lock_at,
        submission_types=submission_types,
        assignment_group_id=assignment_group_id,
    )


class TestParseIsoDate:
    def test_none_input(self):
        assert parse_iso_date(None) is None

    def test_empty_string(self):
        assert parse_iso_date('') is None

    def test_z_suffix(self):
        dt = parse_iso_date('2024-01-15T23:59:00Z')
        assert dt.year == 2024
        assert dt.month == 1
        assert dt.day == 15

    def test_offset_suffix(self):
        dt = parse_iso_date('2024-01-15T23:59:00+00:00')
        assert dt.tzinfo is not None


class TestFormatTimedelta:
    def test_zero(self):
        assert format_timedelta(datetime.timedelta(0)) == "0 seconds"

    def test_days_only(self):
        assert format_timedelta(datetime.timedelta(days=2)) == "2 days"

    def test_one_day(self):
        assert format_timedelta(datetime.timedelta(days=1)) == "1 day"

    def test_hours_only(self):
        assert format_timedelta(datetime.timedelta(hours=3)) == "3 hours"

    def test_one_hour(self):
        assert format_timedelta(datetime.timedelta(hours=1)) == "1 hour"

    def test_minutes_only(self):
        assert format_timedelta(datetime.timedelta(minutes=30)) == "30 minutes"

    def test_days_and_hours(self):
        assert format_timedelta(datetime.timedelta(days=1, hours=6)) == "1 day, 6 hours"


class TestCheckMissingDueDates:
    def test_no_assignments(self):
        assert check_missing_due_dates([]) == []

    def test_all_have_due_dates(self):
        assignments = [
            make_assignment("HW 1", due_at="2024-01-15T23:59:00Z"),
            make_assignment("HW 2", due_at="2024-01-22T23:59:00Z"),
        ]
        assert check_missing_due_dates(assignments) == []

    def test_one_missing(self):
        assignments = [
            make_assignment("HW 1", due_at="2024-01-15T23:59:00Z"),
            make_assignment("HW 2", due_at=None),
        ]
        assert check_missing_due_dates(assignments) == ["HW 2"]

    def test_all_missing(self):
        assignments = [
            make_assignment("HW 1"),
            make_assignment("HW 2"),
        ]
        assert check_missing_due_dates(assignments) == ["HW 1", "HW 2"]


class TestCheckUntilDateConsistency:
    def test_no_assignments(self):
        offset, count, issues = check_until_date_consistency_for_group([])
        assert offset is None
        assert count == 0
        assert issues == []

    def test_non_submittable_missing_due_date(self):
        assignments = [
            make_assignment("Attendance", submission_types=['none']),
            make_assignment("Ungraded", submission_types=['not_graded']),
        ]
        offset, count, issues = check_until_date_consistency_for_group(assignments)
        assert offset is None
        assert len(issues) == 2
        assert "non-submittable" in issues[0][1]

    def test_non_submittable_with_due_date_ok(self):
        assignments = [
            make_assignment("Attendance", due_at="2024-01-15T23:59:00Z",
                            submission_types=['none']),
        ]
        offset, count, issues = check_until_date_consistency_for_group(assignments)
        assert offset is None
        assert issues == []

    def test_consistent_offsets(self):
        assignments = [
            make_assignment("HW 1",
                            due_at="2024-01-15T23:59:00Z",
                            lock_at="2024-01-17T23:59:00Z"),
            make_assignment("HW 2",
                            due_at="2024-01-22T23:59:00Z",
                            lock_at="2024-01-24T23:59:00Z"),
        ]
        offset, count, issues = check_until_date_consistency_for_group(assignments)
        assert offset == datetime.timedelta(days=2)
        assert count == 2
        assert issues == []

    def test_inconsistent_offset(self):
        assignments = [
            make_assignment("HW 1",
                            due_at="2024-01-15T23:59:00Z",
                            lock_at="2024-01-17T23:59:00Z"),
            make_assignment("HW 2",
                            due_at="2024-01-22T23:59:00Z",
                            lock_at="2024-01-24T23:59:00Z"),
            make_assignment("HW 3",
                            due_at="2024-01-29T23:59:00Z",
                            lock_at="2024-01-30T23:59:00Z"),  # 1 day instead of 2
        ]
        offset, count, issues = check_until_date_consistency_for_group(assignments)
        assert offset == datetime.timedelta(days=2)
        assert len(issues) == 1
        assert issues[0][0] == "HW 3"
        assert "1 day" in issues[0][1]

    def test_missing_lock_date(self):
        assignments = [
            make_assignment("HW 1",
                            due_at="2024-01-15T23:59:00Z",
                            lock_at=None),
        ]
        offset, count, issues = check_until_date_consistency_for_group(assignments)
        assert len(issues) == 1
        assert "no until/lock date" in issues[0][1]

    def test_missing_due_date_with_lock(self):
        assignments = [
            make_assignment("HW 1",
                            due_at=None,
                            lock_at="2024-01-17T23:59:00Z"),
        ]
        offset, count, issues = check_until_date_consistency_for_group(assignments)
        assert len(issues) == 1
        assert "no due date" in issues[0][1]


class TestExtractLinks:
    def test_empty_html(self):
        assert extract_links('') == []

    def test_none_html(self):
        assert extract_links(None) == []

    def test_anchor_links(self):
        html = '<a href="https://example.com">Link</a>'
        links = extract_links(html)
        assert len(links) == 1
        assert links[0] == ('a', 'href', 'https://example.com')

    def test_image_links(self):
        html = '<img src="/courses/123/files/456/preview">'
        links = extract_links(html)
        assert len(links) == 1
        assert links[0] == ('img', 'src', '/courses/123/files/456/preview')

    def test_iframe_links(self):
        html = '<iframe src="https://youtube.com/embed/abc"></iframe>'
        links = extract_links(html)
        assert len(links) == 1
        assert links[0] == ('iframe', 'src', 'https://youtube.com/embed/abc')

    def test_multiple_links(self):
        html = '''
        <a href="https://a.com">A</a>
        <img src="/img.png">
        <a href="https://b.com">B</a>
        '''
        links = extract_links(html)
        assert len(links) == 3

    def test_no_href(self):
        html = '<a name="anchor">text</a>'
        links = extract_links(html)
        assert len(links) == 0


class TestClassifyLink:
    CANVAS = "https://canvas.example.com"
    COURSE_ID = 123

    def test_skip_anchor(self):
        cat, path = classify_link('#section', self.CANVAS, self.COURSE_ID)
        assert cat == 'skip'

    def test_skip_mailto(self):
        cat, path = classify_link('mailto:foo@bar.com', self.CANVAS, self.COURSE_ID)
        assert cat == 'skip'

    def test_skip_javascript(self):
        cat, path = classify_link('javascript:void(0)', self.CANVAS, self.COURSE_ID)
        assert cat == 'skip'

    def test_skip_empty(self):
        cat, path = classify_link('', self.CANVAS, self.COURSE_ID)
        assert cat == 'skip'

    def test_skip_none(self):
        cat, path = classify_link(None, self.CANVAS, self.COURSE_ID)
        assert cat == 'skip'

    def test_relative_internal(self):
        cat, path = classify_link('/courses/123/pages/syllabus', self.CANVAS, self.COURSE_ID)
        assert cat == 'internal'
        assert path == '/courses/123/pages/syllabus'

    def test_relative_internal_strips_query(self):
        cat, path = classify_link('/courses/123/pages/syllabus?foo=bar', self.CANVAS, self.COURSE_ID)
        assert cat == 'internal'
        assert path == '/courses/123/pages/syllabus'

    def test_relative_other_course(self):
        cat, path = classify_link('/courses/999/pages/something', self.CANVAS, self.COURSE_ID)
        assert cat == 'internal_other'

    def test_absolute_internal(self):
        cat, path = classify_link('https://canvas.example.com/courses/123/assignments/5', self.CANVAS, self.COURSE_ID)
        assert cat == 'internal'
        assert path == '/courses/123/assignments/5'

    def test_absolute_other_course(self):
        cat, path = classify_link('https://canvas.example.com/courses/999/pages/foo', self.CANVAS, self.COURSE_ID)
        assert cat == 'internal_other'

    def test_external(self):
        cat, path = classify_link('https://google.com', self.CANVAS, self.COURSE_ID)
        assert cat == 'external'
        assert path == 'https://google.com'

    def test_relative_non_course(self):
        cat, path = classify_link('/profile', self.CANVAS, self.COURSE_ID)
        assert cat == 'skip'


class TestGroupAssignmentsByGroup:
    def test_single_group(self):
        assignments = [
            make_assignment("HW 1", assignment_group_id=10),
            make_assignment("HW 2", assignment_group_id=10),
        ]
        grouped = group_assignments_by_group(assignments, {10: "Homework"})
        assert list(grouped.keys()) == ["Homework"]
        assert len(grouped["Homework"]) == 2

    def test_multiple_groups(self):
        assignments = [
            make_assignment("HW 1", assignment_group_id=10),
            make_assignment("Quiz 1", assignment_group_id=20),
            make_assignment("HW 2", assignment_group_id=10),
        ]
        grouped = group_assignments_by_group(assignments, {10: "Homework", 20: "Quizzes"})
        assert set(grouped.keys()) == {"Homework", "Quizzes"}
        assert len(grouped["Homework"]) == 2
        assert len(grouped["Quizzes"]) == 1

    def test_unknown_group_id(self):
        assignments = [
            make_assignment("HW 1", assignment_group_id=99),
        ]
        grouped = group_assignments_by_group(assignments, {})
        assert len(grouped) == 1
        key = list(grouped.keys())[0]
        assert "Unknown" in key

    def test_empty_assignments(self):
        grouped = group_assignments_by_group([], {10: "Homework"})
        assert grouped == {}
