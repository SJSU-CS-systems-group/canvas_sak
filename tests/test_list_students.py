"""Tests for list-students helpers."""

from canvas_sak.commands.list_students import format_sections


class TestFormatSections:
    def test_empty_enrollments_returns_empty_string(self):
        assert format_sections([], {1: "Section A"}) == ""
        assert format_sections(None, {1: "Section A"}) == ""

    def test_single_section(self):
        enrollments = [{"course_section_id": 1}]
        assert format_sections(enrollments, {1: "Section A"}) == "Section A"

    def test_multiple_sections_comma_separated(self):
        enrollments = [{"course_section_id": 1}, {"course_section_id": 2}]
        names = {1: "Section A", 2: "Section B"}
        assert format_sections(enrollments, names) == "Section A, Section B"

    def test_duplicate_sections_listed_once(self):
        enrollments = [{"course_section_id": 1}, {"course_section_id": 1}]
        assert format_sections(enrollments, {1: "Section A"}) == "Section A"

    def test_unknown_section_falls_back_to_id(self):
        enrollments = [{"course_section_id": 42}]
        assert format_sections(enrollments, {}) == "42"

    def test_enrollment_without_section_id_skipped(self):
        enrollments = [{}, {"course_section_id": 1}]
        assert format_sections(enrollments, {1: "Section A"}) == "Section A"
