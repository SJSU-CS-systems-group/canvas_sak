"""Tests for discussion header handling in upload_canvas_course.py"""

from canvas_sak.commands.upload_canvas_course import (
    DISCUSSION_KEYWORDS,
    build_discussion_params,
    parse_headers,
)


class TestParseDiscussionHeaders:
    def test_title_may_contain_colons(self):
        headers, body = parse_headers(
            "title: Discussion: Week 3: Compute\n\nbody text\n", DISCUSSION_KEYWORDS)
        assert headers["title"] == "Discussion: Week 3: Compute"
        assert "body text" in body

    def test_graded_headers_recognized(self):
        content = ("title: d\n"
                   "points: 1\n"
                   "assignment_group: Study Discussion\n"
                   "available: 2026-08-24-13:00\n"
                   "due: 2026-08-31-13:00\n"
                   "until: 2026-08-31-13:00\n"
                   "allow_rating: true\n"
                   "only_graders_can_rate: true\n"
                   "\nbody\n")
        headers, body = parse_headers(content, DISCUSSION_KEYWORDS)
        assert headers["points"] == "1"
        assert headers["assignment_group"] == "Study Discussion"
        assert headers["due"] == "2026-08-31-13:00"
        assert body.strip() == "body"


class TestBuildDiscussionParams:
    def test_plain_discussion_passes_through_without_assignment(self):
        params, group = build_discussion_params(
            {"title": "Discussion: Week 3", "published": "true"})
        assert params == {"title": "Discussion: Week 3", "published": "true"}
        assert group is None

    def test_points_make_a_graded_discussion(self):
        params, _ = build_discussion_params({"title": "d", "points": "1"})
        assert params["assignment"] == {"points_possible": 1.0,
                                        "grading_type": "points"}
        assert "points" not in params

    def test_dates_go_to_the_assignment_in_iso_format(self):
        params, _ = build_discussion_params(
            {"title": "d", "points": "1",
             "available": "2026-08-24-13:00",
             "due": "2026-08-31-13:00",
             "until": "2026-08-31-13:00"})
        assignment = params["assignment"]
        assert assignment["unlock_at"].startswith("2026-08-24T13:00")
        assert assignment["due_at"].startswith("2026-08-31T13:00")
        assert assignment["lock_at"] == assignment["due_at"]
        for key in ("available", "due", "until"):
            assert key not in params

    def test_assignment_group_name_returned_for_caller_to_resolve(self):
        params, group = build_discussion_params(
            {"title": "d", "points": "1", "assignment_group": "Study Discussion"})
        assert group == "Study Discussion"
        assert "assignment_group" not in params

    def test_assignment_group_without_points_is_still_graded(self):
        params, group = build_discussion_params(
            {"title": "d", "assignment_group": "Study Discussion"})
        assert params["assignment"] == {}
        assert group == "Study Discussion"

    def test_rating_flags_normalized_to_lowercase(self):
        params, _ = build_discussion_params(
            {"title": "d", "allow_rating": "True", "only_graders_can_rate": "TRUE"})
        assert params["allow_rating"] == "true"
        assert params["only_graders_can_rate"] == "true"
