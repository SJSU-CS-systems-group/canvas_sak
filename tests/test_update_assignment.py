"""Tests for update_assignment command."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from canvas_sak.commands.update_assignment import process_assignment


def make_assignment(name, allowed_attempts=-1, submission_types=None, quiz_id=None,
                    points_possible=100.0, published=True, assignment_group_id=1):
    """Helper to create assignment-like objects."""
    if submission_types is None:
        submission_types = ['online_upload']
    ns = SimpleNamespace(
        name=name,
        allowed_attempts=allowed_attempts,
        submission_types=submission_types,
        points_possible=points_possible,
        grading_type='points',
        published=published,
        allowed_extensions=[],
        omit_from_final_grade=False,
        peer_reviews=False,
        due_at=None,
        unlock_at=None,
        lock_at=None,
        assignment_group_id=assignment_group_id,
    )
    ns.edit = MagicMock()
    if quiz_id is not None:
        ns.quiz_id = quiz_id
    return ns


def make_quiz(allowed_attempts=1):
    """Helper to create quiz-like objects."""
    quiz = SimpleNamespace(allowed_attempts=allowed_attempts)
    quiz.edit = MagicMock(return_value=quiz)
    return quiz


class TestProcessAssignmentQuizAttempts:
    """Bug: assignment objects for quizzes always report allowed_attempts=-1,
    but the quiz object has the real value. process_assignment should use the
    quiz's allowed_attempts when available."""

    def test_quiz_assignment_shows_quiz_attempts(self, capsys):
        """A quiz assignment should display the quiz's allowed_attempts, not the assignment's."""
        assignment = make_assignment(
            "Chapter 7 Quiz",
            allowed_attempts=-1,
            submission_types=['online_quiz'],
            quiz_id=42,
        )
        quiz = make_quiz(allowed_attempts=1)
        quizzes = {42: quiz}

        process_assignment(assignment, {}, group_names={1: "Quizzes"}, quizzes=quizzes)

        captured = capsys.readouterr()
        assert "Allowed Attempts: 1" in captured.out

    def test_quiz_assignment_unlimited_attempts(self, capsys):
        """A quiz with unlimited attempts should still show -1."""
        assignment = make_assignment(
            "Chapter 8 Quiz",
            allowed_attempts=-1,
            submission_types=['online_quiz'],
            quiz_id=43,
        )
        quiz = make_quiz(allowed_attempts=-1)
        quizzes = {43: quiz}

        process_assignment(assignment, {}, group_names={1: "Quizzes"}, quizzes=quizzes)

        captured = capsys.readouterr()
        assert "Allowed Attempts: -1" in captured.out

    def test_non_quiz_assignment_uses_assignment_attempts(self, capsys):
        """A regular assignment should still use the assignment's own allowed_attempts."""
        assignment = make_assignment(
            "Homework 1",
            allowed_attempts=3,
            submission_types=['online_upload'],
        )

        process_assignment(assignment, {}, group_names={1: "Homework"}, quizzes={})

        captured = capsys.readouterr()
        assert "Allowed Attempts: 3" in captured.out

    def test_quiz_assignment_no_quizzes_map_falls_back(self, capsys):
        """If quizzes map is not provided, fall back to assignment's allowed_attempts."""
        assignment = make_assignment(
            "Chapter 7 Quiz",
            allowed_attempts=-1,
            submission_types=['online_quiz'],
            quiz_id=42,
        )

        process_assignment(assignment, {}, group_names={1: "Quizzes"})

        captured = capsys.readouterr()
        assert "Allowed Attempts: -1" in captured.out


class TestProcessAssignmentQuizUpdate:
    """Bug: update-assignment --attempts updates the assignment object but not
    the quiz object. For quiz assignments, allowed_attempts must be updated
    on the quiz via quiz.edit()."""

    def test_attempts_update_edits_quiz_not_assignment(self):
        """When updating attempts on a quiz assignment, quiz.edit() should be called
        and allowed_attempts should be removed from the assignment update."""
        assignment = make_assignment(
            "Chapter 7 Quiz",
            allowed_attempts=-1,
            submission_types=['online_quiz'],
            quiz_id=42,
        )
        quiz = make_quiz(allowed_attempts=1)
        quizzes = {42: quiz}

        process_assignment(assignment, {'allowed_attempts': -1},
                           group_names={1: "Quizzes"}, quizzes=quizzes)

        quiz.edit.assert_called_once_with(quiz={'allowed_attempts': -1})
        # assignment.edit should be called without allowed_attempts
        if assignment.edit.called:
            call_kwargs = assignment.edit.call_args
            assignment_dict = call_kwargs[1].get('assignment', call_kwargs[0][0] if call_kwargs[0] else {})
            assert 'allowed_attempts' not in assignment_dict

    def test_attempts_update_on_non_quiz_edits_assignment(self):
        """For regular assignments, allowed_attempts should stay in assignment.edit()."""
        assignment = make_assignment(
            "Homework 1",
            allowed_attempts=1,
            submission_types=['online_upload'],
        )

        process_assignment(assignment, {'allowed_attempts': 3},
                           group_names={1: "Homework"}, quizzes={})

        assignment.edit.assert_called_once_with(assignment={'allowed_attempts': 3})

    def test_quiz_update_with_other_kwargs_splits_correctly(self):
        """When updating both attempts and other fields on a quiz assignment,
        attempts goes to quiz.edit() and other fields go to assignment.edit()."""
        assignment = make_assignment(
            "Chapter 7 Quiz",
            allowed_attempts=1,
            submission_types=['online_quiz'],
            quiz_id=42,
        )
        quiz = make_quiz(allowed_attempts=1)
        quizzes = {42: quiz}

        process_assignment(assignment, {'allowed_attempts': -1, 'points_possible': 50.0},
                           group_names={1: "Quizzes"}, quizzes=quizzes)

        quiz.edit.assert_called_once_with(quiz={'allowed_attempts': -1})
        assignment.edit.assert_called_once_with(assignment={'points_possible': 50.0})

    def test_quiz_update_displays_new_attempts(self, capsys):
        """After updating, the displayed attempts should reflect the new value."""
        assignment = make_assignment(
            "Chapter 7 Quiz",
            allowed_attempts=-1,
            submission_types=['online_quiz'],
            quiz_id=42,
        )
        quiz = make_quiz(allowed_attempts=1)
        # quiz.edit returns updated quiz
        updated_quiz = make_quiz(allowed_attempts=-1)
        quiz.edit = MagicMock(return_value=updated_quiz)
        quizzes = {42: quiz}

        process_assignment(assignment, {'allowed_attempts': -1},
                           group_names={1: "Quizzes"}, quizzes=quizzes)

        captured = capsys.readouterr()
        assert "Allowed Attempts: -1" in captured.out
