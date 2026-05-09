"""Tests for the todo command."""

import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from canvas_sak.commands.todo import assignments_in_window, parse_remove_file, todo_key, upcoming_assignments
from canvas_sak.core import canvas_sak


def _make_todo_item(todo_type, assignment_name, context_name, needs_grading_count=0, due_at=None):
    item = SimpleNamespace(
        type=todo_type,
        assignment={"name": assignment_name, "due_at": due_at},
        course_id=1,
        context_name=context_name,
        context_type="Course",
        html_url="https://canvas.example.com/courses/1/assignments/1",
        needs_grading_count=needs_grading_count,
        ignore_permanently="https://canvas.example.com/api/v1/users/self/todo/assignment_1/grading?permanent=1",
    )
    return item


class TestTodo:
    @patch("canvas_sak.commands.todo.get_canvas_object")
    def test_tab_separated_output(self, mock_get_canvas):
        canvas = MagicMock()
        mock_get_canvas.return_value = canvas

        todo_item = _make_todo_item("grading", "Homework 1", "SP26: CS-149 Sec 01 - Operating Systems", needs_grading_count=5)
        canvas.get_todo_items.return_value = [todo_item]

        runner = CliRunner()
        result = runner.invoke(canvas_sak, ["todo"])
        assert result.exit_code == 0
        assert "\t" in result.output
        fields = result.output.strip().split("\t")
        assert fields[1] == "grading"
        assert fields[2] == "Homework 1"
        assert "(5 to grade)" in fields[3]

    @patch("canvas_sak.commands.todo.get_canvas_object")
    def test_lists_submitting_items_with_due_date(self, mock_get_canvas):
        canvas = MagicMock()
        mock_get_canvas.return_value = canvas

        todo_item = _make_todo_item("submitting", "Essay 1", "SP26: CS-149 Sec 01 - Operating Systems", due_at="2026-03-15T23:59:00Z")
        canvas.get_todo_items.return_value = [todo_item]

        runner = CliRunner()
        result = runner.invoke(canvas_sak, ["todo"])
        assert result.exit_code == 0
        assert "Essay 1" in result.output
        assert "submitting" in result.output
        assert "due: 2026-03-15T23:59:00Z" in result.output

    @patch("canvas_sak.commands.todo.get_canvas_object")
    def test_empty_todo_list(self, mock_get_canvas):
        canvas = MagicMock()
        mock_get_canvas.return_value = canvas
        canvas.get_todo_items.return_value = []

        runner = CliRunner()
        result = runner.invoke(canvas_sak, ["todo"])
        assert result.exit_code == 0
        assert "no todo items" in result.output


class TestParseRemoveFile:
    def test_parses_tab_separated_lines(self):
        lines = ["CS101:Intro\tgrading\tHomework 1\t(5 to grade)\n"]
        keys = parse_remove_file(lines)
        assert todo_key("CS101:Intro", "grading", "Homework 1") in keys

    def test_skips_blank_lines(self):
        lines = ["", "CS101:Intro\tgrading\tHomework 1\n", ""]
        keys = parse_remove_file(lines)
        assert len(keys) == 1

    def test_skips_lines_with_fewer_than_3_fields(self):
        lines = ["CS101:Intro\tgrading\n"]
        keys = parse_remove_file(lines)
        assert len(keys) == 0


class TestTodoRemove:
    @patch("canvas_sak.commands.todo.requests")
    @patch("canvas_sak.commands.todo.get_canvas_object")
    def test_remove_dryrun(self, mock_get_canvas, mock_requests):
        canvas = MagicMock()
        mock_get_canvas.return_value = canvas

        todo_item = _make_todo_item("grading", "Homework 1", "SP26: CS-149 Sec 01 - Operating Systems", needs_grading_count=5)
        canvas.get_todo_items.return_value = [todo_item]

        runner = CliRunner(mix_stderr=False)
        with runner.isolated_filesystem():
            with open("remove.txt", "w") as f:
                f.write("SP26:CS-149\tgrading\tHomework 1\n")
            result = runner.invoke(canvas_sak, ["todo", "--remove", "remove.txt"])

        assert result.exit_code == 0
        assert "would remove" in result.stderr
        assert "dryrun" in result.stderr
        mock_requests.delete.assert_not_called()

    @patch("canvas_sak.commands.todo.core")
    @patch("canvas_sak.commands.todo.requests")
    @patch("canvas_sak.commands.todo.get_canvas_object")
    def test_remove_no_dryrun(self, mock_get_canvas, mock_requests, mock_core):
        canvas = MagicMock()
        mock_get_canvas.return_value = canvas
        mock_core.access_token = "fake-token"

        todo_item = _make_todo_item("grading", "Homework 1", "SP26: CS-149 Sec 01 - Operating Systems", needs_grading_count=5)
        canvas.get_todo_items.return_value = [todo_item]

        runner = CliRunner(mix_stderr=False)
        with runner.isolated_filesystem():
            with open("remove.txt", "w") as f:
                f.write("SP26:CS-149\tgrading\tHomework 1\n")
            result = runner.invoke(canvas_sak, ["todo", "--remove", "remove.txt", "--no-dryrun"])

        assert result.exit_code == 0
        assert "removed:" in result.stderr
        mock_requests.delete.assert_called_once()

    @patch("canvas_sak.commands.todo.requests")
    @patch("canvas_sak.commands.todo.get_canvas_object")
    def test_remove_no_match(self, mock_get_canvas, mock_requests):
        canvas = MagicMock()
        mock_get_canvas.return_value = canvas

        todo_item = _make_todo_item("grading", "Homework 1", "SP26: CS-149 Sec 01 - Operating Systems", needs_grading_count=5)
        canvas.get_todo_items.return_value = [todo_item]

        runner = CliRunner(mix_stderr=False)
        with runner.isolated_filesystem():
            with open("remove.txt", "w") as f:
                f.write("CS999:Fake\tgrading\tNonexistent\n")
            result = runner.invoke(canvas_sak, ["todo", "--remove", "remove.txt"])

        assert result.exit_code == 0
        assert "0 item(s)" in result.stderr
        mock_requests.delete.assert_not_called()


def _make_assignment(name, due_at=None, lock_at=None):
    return SimpleNamespace(name=name, due_at=due_at, lock_at=lock_at)


def _iso_offset_from_now(*, days):
    """Build a Canvas-style ISO timestamp offset from the actual current time
    by the given number of days. Used by CLI tests so fixtures stay inside
    the command's now-relative windows regardless of when the suite runs."""
    dt = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=days)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


class TestUpcomingAssignments:
    def test_due_within_window(self):
        now = datetime.datetime(2026, 3, 1, tzinfo=datetime.timezone.utc)
        assignments = [_make_assignment("HW1", due_at="2026-03-05T23:59:00Z")]
        result = upcoming_assignments(assignments, now, 10)
        assert len(result) == 1
        assert result[0][0] == "HW1"
        assert result[0][1] == "due"

    def test_lock_within_window(self):
        now = datetime.datetime(2026, 3, 1, tzinfo=datetime.timezone.utc)
        assignments = [_make_assignment("HW2", lock_at="2026-03-08T07:59:00Z")]
        result = upcoming_assignments(assignments, now, 10)
        assert len(result) == 1
        assert result[0][1] == "locks"

    def test_due_and_lock_both_within_window(self):
        now = datetime.datetime(2026, 3, 1, tzinfo=datetime.timezone.utc)
        assignments = [_make_assignment("HW3", due_at="2026-03-05T00:00:00Z", lock_at="2026-03-08T00:00:00Z")]
        result = upcoming_assignments(assignments, now, 10)
        assert len(result) == 2
        types = {r[1] for r in result}
        assert types == {"due", "locks"}

    def test_past_dates_excluded(self):
        now = datetime.datetime(2026, 3, 1, tzinfo=datetime.timezone.utc)
        assignments = [_make_assignment("Old", due_at="2026-02-20T00:00:00Z")]
        result = upcoming_assignments(assignments, now, 10)
        assert len(result) == 0

    def test_beyond_window_excluded(self):
        now = datetime.datetime(2026, 3, 1, tzinfo=datetime.timezone.utc)
        assignments = [_make_assignment("Far", due_at="2026-04-01T00:00:00Z")]
        result = upcoming_assignments(assignments, now, 10)
        assert len(result) == 0

    def test_no_dates_excluded(self):
        now = datetime.datetime(2026, 3, 1, tzinfo=datetime.timezone.utc)
        assignments = [_make_assignment("NoDates")]
        result = upcoming_assignments(assignments, now, 10)
        assert len(result) == 0

    def test_sorted_by_date(self):
        now = datetime.datetime(2026, 3, 1, tzinfo=datetime.timezone.utc)
        assignments = [
            _make_assignment("Later", due_at="2026-03-09T00:00:00Z"),
            _make_assignment("Sooner", due_at="2026-03-03T00:00:00Z"),
        ]
        result = upcoming_assignments(assignments, now, 10)
        assert result[0][0] == "Sooner"
        assert result[1][0] == "Later"


class TestUpcomingCommand:
    @patch("canvas_sak.commands.todo.get_courses")
    @patch("canvas_sak.commands.todo.get_canvas_object")
    def test_upcoming_output(self, mock_get_canvas, mock_get_courses):
        canvas = MagicMock()
        mock_get_canvas.return_value = canvas

        course = MagicMock()
        course.name = "SP26: CMPE-30 Programming Concept and Meth - All Sections"
        course.get_assignments.return_value = [
            _make_assignment("Place Boats", due_at=_iso_offset_from_now(days=3)),
        ]
        mock_get_courses.return_value = [course]

        runner = CliRunner()
        result = runner.invoke(canvas_sak, ["todo", "--upcoming"])
        assert result.exit_code == 0
        lines = result.output.strip().split("\n")
        assert lines[0] == "upcoming"
        assert "Place Boats" in result.output

    @patch("canvas_sak.commands.todo.get_courses")
    @patch("canvas_sak.commands.todo.get_canvas_object")
    def test_upcoming_empty(self, mock_get_canvas, mock_get_courses):
        canvas = MagicMock()
        mock_get_canvas.return_value = canvas

        course = MagicMock()
        course.name = "SP26: CMPE-30 Programming"
        course.get_assignments.return_value = [
            _make_assignment("Old HW", due_at="2025-01-01T00:00:00Z"),
        ]
        mock_get_courses.return_value = [course]

        runner = CliRunner()
        result = runner.invoke(canvas_sak, ["todo", "--upcoming"])
        assert result.exit_code == 0
        assert "no upcoming" in result.output


class TestRecentPastAssignments:
    def test_due_in_recent_past(self):
        now = datetime.datetime(2026, 3, 1, tzinfo=datetime.timezone.utc)
        start = now - datetime.timedelta(days=10)
        assignments = [_make_assignment("HW1", due_at="2026-02-25T23:59:00Z")]
        result = assignments_in_window(assignments, start, now)
        assert len(result) == 1
        assert result[0][0] == "HW1"
        assert result[0][1] == "due"

    def test_locked_in_recent_past(self):
        now = datetime.datetime(2026, 3, 1, tzinfo=datetime.timezone.utc)
        start = now - datetime.timedelta(days=10)
        assignments = [_make_assignment("HW2", lock_at="2026-02-22T07:59:00Z")]
        result = assignments_in_window(assignments, start, now)
        assert len(result) == 1
        assert result[0][1] == "locks"

    def test_too_old_excluded(self):
        now = datetime.datetime(2026, 3, 1, tzinfo=datetime.timezone.utc)
        start = now - datetime.timedelta(days=10)
        assignments = [_make_assignment("Ancient", due_at="2026-01-01T00:00:00Z")]
        result = assignments_in_window(assignments, start, now)
        assert len(result) == 0

    def test_future_excluded(self):
        now = datetime.datetime(2026, 3, 1, tzinfo=datetime.timezone.utc)
        start = now - datetime.timedelta(days=10)
        assignments = [_make_assignment("Future", due_at="2026-03-15T00:00:00Z")]
        result = assignments_in_window(assignments, start, now)
        assert len(result) == 0


class TestRecentPastCommand:
    @patch("canvas_sak.commands.todo.get_courses")
    @patch("canvas_sak.commands.todo.get_canvas_object")
    def test_recent_past_output(self, mock_get_canvas, mock_get_courses):
        canvas = MagicMock()
        mock_get_canvas.return_value = canvas

        course = MagicMock()
        course.name = "SP26: CMPE-142 Sec 01 - Operating Systems"
        course.get_assignments.return_value = [
            _make_assignment("converse", due_at=_iso_offset_from_now(days=-3)),
        ]
        mock_get_courses.return_value = [course]

        runner = CliRunner()
        result = runner.invoke(canvas_sak, ["todo", "--recent-past"])
        assert result.exit_code == 0
        lines = result.output.strip().split("\n")
        assert lines[0] == "recent past"
        assert "converse" in result.output

    @patch("canvas_sak.commands.todo.get_courses")
    @patch("canvas_sak.commands.todo.get_canvas_object")
    def test_recent_past_empty(self, mock_get_canvas, mock_get_courses):
        canvas = MagicMock()
        mock_get_canvas.return_value = canvas

        course = MagicMock()
        course.name = "SP26: CMPE-30 Programming"
        course.get_assignments.return_value = [
            _make_assignment("Old HW", due_at="2025-01-01T00:00:00Z"),
        ]
        mock_get_courses.return_value = [course]

        runner = CliRunner()
        result = runner.invoke(canvas_sak, ["todo", "--recent-past"])
        assert result.exit_code == 0
        assert "no recent" in result.output

    @patch("canvas_sak.commands.todo.get_courses")
    @patch("canvas_sak.commands.todo.get_canvas_object")
    def test_both_flags(self, mock_get_canvas, mock_get_courses):
        canvas = MagicMock()
        mock_get_canvas.return_value = canvas

        course = MagicMock()
        course.name = "SP26: CMPE-30 Programming"
        course.get_assignments.return_value = [
            _make_assignment("Old HW", due_at="2025-01-01T00:00:00Z"),
        ]
        mock_get_courses.return_value = [course]

        runner = CliRunner()
        result = runner.invoke(canvas_sak, ["todo", "--upcoming", "--recent-past"])
        assert result.exit_code == 0
        assert "no upcoming or recent" in result.output

    @patch("canvas_sak.commands.todo.get_courses")
    @patch("canvas_sak.commands.todo.get_canvas_object")
    def test_both_flags_with_results(self, mock_get_canvas, mock_get_courses):
        canvas = MagicMock()
        mock_get_canvas.return_value = canvas

        course = MagicMock()
        course.name = "SP26: CMPE-30 Programming"
        course.get_assignments.return_value = [
            _make_assignment("Past HW", due_at=_iso_offset_from_now(days=-3)),
            _make_assignment("Future HW", due_at=_iso_offset_from_now(days=3)),
        ]
        mock_get_courses.return_value = [course]

        runner = CliRunner()
        result = runner.invoke(canvas_sak, ["todo", "--upcoming", "--recent-past"])
        assert result.exit_code == 0
        lines = result.output.strip().split("\n")
        assert lines[0] == "recent past"
        assert "Past HW" in lines[1]
        upcoming_idx = lines.index("upcoming")
        assert upcoming_idx > 1
        assert "Future HW" in lines[upcoming_idx + 1]
