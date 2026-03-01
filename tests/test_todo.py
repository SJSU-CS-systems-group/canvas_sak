"""Tests for the todo command."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from canvas_sak.commands.todo import parse_remove_file, todo_key
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

        runner = CliRunner()
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

        runner = CliRunner()
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

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("remove.txt", "w") as f:
                f.write("CS999:Fake\tgrading\tNonexistent\n")
            result = runner.invoke(canvas_sak, ["todo", "--remove", "remove.txt"])

        assert result.exit_code == 0
        assert "0 item(s)" in result.stderr
        mock_requests.delete.assert_not_called()
