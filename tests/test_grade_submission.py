"""Tests for grade_submission command."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch, call

from click.testing import CliRunner

from canvas_sak.core import canvas_sak


def make_canvas(course, users, submission):
    """Helper to create mock Canvas + course + assignment + submission."""
    mock_canvas = MagicMock()
    mock_canvas.get_current_user.return_value = SimpleNamespace(id=1)
    mock_canvas.get_courses.return_value = [course]
    return mock_canvas


def make_course(name="CS249 Spring 2026"):
    course = MagicMock()
    course.name = name
    course.start_at_date = None
    course.end_at_date = None
    course.get_course_level_assignment_data.return_value = [
        {'title': 'Homework 1', 'assignment_id': 101},
    ]
    return course


def make_submission(user_id=42):
    sub = MagicMock()
    sub.user_id = user_id
    return sub


class TestGradeSubmissionDryrun:
    """Test that dryrun mode shows what would happen without modifying anything."""

    @patch('canvas_sak.commands.grade_submission.get_canvas_object')
    @patch('canvas_sak.commands.grade_submission.get_course')
    @patch('canvas_sak.commands.grade_submission.get_assignment')
    def test_dryrun_does_not_grade(self, mock_get_assignment, mock_get_course,
                                    mock_get_canvas):
        course = make_course()
        assignment = MagicMock()
        assignment.name = "Homework 1"
        assignment.points_possible = 100
        submission = make_submission()
        assignment.get_submission.return_value = submission

        mock_get_canvas.return_value = MagicMock()
        mock_get_course.return_value = course
        mock_get_assignment.return_value = assignment

        runner = CliRunner()
        result = runner.invoke(canvas_sak, [
            'grade-submission', 'CS249', 'Homework',
            '--canvasid', '42', '--grade', '95', '--message', 'Good work'
        ])

        assert result.exit_code == 0
        submission.edit.assert_not_called()

    @patch('canvas_sak.commands.grade_submission.get_canvas_object')
    @patch('canvas_sak.commands.grade_submission.get_course')
    @patch('canvas_sak.commands.grade_submission.get_assignment')
    def test_no_dryrun_applies_grade_and_comment(self, mock_get_assignment,
                                                  mock_get_course, mock_get_canvas):
        course = make_course()
        assignment = MagicMock()
        assignment.name = "Homework 1"
        assignment.points_possible = 100
        submission = make_submission()
        submission.edit.return_value = None
        submission.upload_comment.return_value = None
        assignment.get_submission.return_value = submission

        mock_get_canvas.return_value = MagicMock()
        mock_get_course.return_value = course
        mock_get_assignment.return_value = assignment

        runner = CliRunner()
        result = runner.invoke(canvas_sak, [
            'grade-submission', 'CS249', 'Homework',
            '--canvasid', '42', '--grade', '95', '--message', 'Good work',
            '--no-dryrun'
        ])

        assert result.exit_code == 0
        submission.edit.assert_called_once_with(
            submission={'posted_grade': '95'},
            comment={'text_comment': 'Good work'}
        )

    @patch('canvas_sak.commands.grade_submission.get_canvas_object')
    @patch('canvas_sak.commands.grade_submission.get_course')
    @patch('canvas_sak.commands.grade_submission.get_assignment')
    def test_no_dryrun_with_comment(self, mock_get_assignment,
                                     mock_get_course, mock_get_canvas):
        course = make_course()
        assignment = MagicMock()
        assignment.name = "Homework 1"
        assignment.points_possible = 100
        submission = make_submission()
        submission.edit.return_value = None
        assignment.get_submission.return_value = submission

        mock_get_canvas.return_value = MagicMock()
        mock_get_course.return_value = course
        mock_get_assignment.return_value = assignment

        runner = CliRunner()
        result = runner.invoke(canvas_sak, [
            'grade-submission', 'CS249', 'Homework',
            '--canvasid', '42', '--grade', '95', '--message', 'Nice job',
            '--no-dryrun'
        ])

        assert result.exit_code == 0
        submission.edit.assert_called_once_with(
            submission={'posted_grade': '95'},
            comment={'text_comment': 'Nice job'}
        )


class TestGradeSubmissionStudentLookup:
    """Test that --canvasid and --sisid resolve to correct user."""

    @patch('canvas_sak.commands.grade_submission.get_canvas_object')
    @patch('canvas_sak.commands.grade_submission.get_course')
    @patch('canvas_sak.commands.grade_submission.get_assignment')
    def test_canvasid_lookup(self, mock_get_assignment, mock_get_course,
                              mock_get_canvas):
        course = make_course()
        assignment = MagicMock()
        assignment.name = "Homework 1"
        assignment.points_possible = 100
        submission = make_submission(user_id=42)
        assignment.get_submission.return_value = submission

        mock_get_canvas.return_value = MagicMock()
        mock_get_course.return_value = course
        mock_get_assignment.return_value = assignment

        runner = CliRunner()
        result = runner.invoke(canvas_sak, [
            'grade-submission', 'CS249', 'Homework',
            '--canvasid', '42', '--grade', '95', '--message', 'Good'
        ])

        assert result.exit_code == 0
        assignment.get_submission.assert_called_once_with(42, include=[])

    @patch('canvas_sak.commands.grade_submission.get_canvas_object')
    @patch('canvas_sak.commands.grade_submission.get_course')
    @patch('canvas_sak.commands.grade_submission.get_assignment')
    def test_sisid_lookup(self, mock_get_assignment, mock_get_course,
                           mock_get_canvas):
        course = make_course()
        enrollment = SimpleNamespace(user={'id': 42}, sis_user_id='jdoe01')
        course.get_enrollments.return_value = [enrollment]
        assignment = MagicMock()
        assignment.name = "Homework 1"
        assignment.points_possible = 100
        submission = make_submission(user_id=42)
        assignment.get_submission.return_value = submission

        mock_get_canvas.return_value = MagicMock()
        mock_get_course.return_value = course
        mock_get_assignment.return_value = assignment

        runner = CliRunner()
        result = runner.invoke(canvas_sak, [
            'grade-submission', 'CS249', 'Homework',
            '--sisid', 'jdoe01', '--grade', '95', '--message', 'Good'
        ])

        assert result.exit_code == 0
        assignment.get_submission.assert_called_once_with(42, include=[])

    @patch('canvas_sak.commands.grade_submission.get_canvas_object')
    @patch('canvas_sak.commands.grade_submission.get_course')
    @patch('canvas_sak.commands.grade_submission.get_assignment')
    def test_sisid_not_found(self, mock_get_assignment, mock_get_course,
                              mock_get_canvas):
        course = make_course()
        enrollment = SimpleNamespace(user={'id': 42}, sis_user_id='other01')
        course.get_enrollments.return_value = [enrollment]
        assignment = MagicMock()
        assignment.name = "Homework 1"
        mock_get_canvas.return_value = MagicMock()
        mock_get_course.return_value = course
        mock_get_assignment.return_value = assignment

        runner = CliRunner()
        result = runner.invoke(canvas_sak, [
            'grade-submission', 'CS249', 'Homework',
            '--sisid', 'jdoe01', '--grade', '95', '--message', 'Good'
        ])

        assert result.exit_code != 0


class TestGradeSubmissionValidation:
    """Test input validation."""

    def test_requires_canvasid_or_sisid(self):
        runner = CliRunner()
        result = runner.invoke(canvas_sak, [
            'grade-submission', 'CS249', 'Homework',
            '--grade', '95', '--message', 'Good'
        ])
        assert result.exit_code != 0

    def test_rejects_both_canvasid_and_sisid(self):
        runner = CliRunner()
        result = runner.invoke(canvas_sak, [
            'grade-submission', 'CS249', 'Homework',
            '--canvasid', '42', '--sisid', 'jdoe01',
            '--grade', '95', '--message', 'Good'
        ])
        assert result.exit_code != 0


class TestDeletePrevious:
    """Test --delete-previous removes prior comments/attachments from current user."""

    def _make_comment(self, comment_id, author_id, text, attachments=None):
        comment = {'id': comment_id, 'author_id': author_id, 'comment': text}
        if attachments:
            comment['attachments'] = attachments
        return comment

    @patch('canvas_sak.commands.grade_submission.get_canvas_object')
    @patch('canvas_sak.commands.grade_submission.get_course')
    @patch('canvas_sak.commands.grade_submission.get_assignment')
    def test_dryrun_shows_what_would_be_deleted(self, mock_get_assignment,
                                                 mock_get_course, mock_get_canvas):
        canvas = MagicMock()
        canvas.user_id = 99
        mock_get_canvas.return_value = canvas

        course = make_course()
        course.id = 1
        mock_get_course.return_value = course

        assignment = MagicMock()
        assignment.name = "Homework 1"
        assignment.id = 101
        submission = make_submission(user_id=42)
        submission.course_id = 1
        submission.assignment_id = 101
        submission.submission_comments = [
            self._make_comment(10, 99, 'old feedback'),
            self._make_comment(11, 42, 'student question'),
            self._make_comment(12, 99, 'more feedback', [{'id': 1, 'display_name': 'rubric.pdf'}]),
        ]
        assignment.get_submission.return_value = submission
        mock_get_assignment.return_value = assignment

        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(canvas_sak, [
            'grade-submission', 'CS249', 'Homework',
            '--canvasid', '42', '--grade', '95', '--message', 'New feedback',
            '--delete-previous'
        ])

        assert result.exit_code == 0
        # should not actually delete in dryrun
        submission._requester.request.assert_not_called()

    @patch('canvas_sak.commands.grade_submission.get_canvas_object')
    @patch('canvas_sak.commands.grade_submission.get_course')
    @patch('canvas_sak.commands.grade_submission.get_assignment')
    def test_no_dryrun_deletes_own_comments_only(self, mock_get_assignment,
                                                  mock_get_course, mock_get_canvas):
        canvas = MagicMock()
        canvas.user_id = 99
        mock_get_canvas.return_value = canvas

        course = make_course()
        course.id = 1
        mock_get_course.return_value = course

        assignment = MagicMock()
        assignment.name = "Homework 1"
        assignment.id = 101
        submission = make_submission(user_id=42)
        submission.course_id = 1
        submission.assignment_id = 101
        submission.submission_comments = [
            self._make_comment(10, 99, 'old feedback'),
            self._make_comment(11, 42, 'student question'),
            self._make_comment(12, 99, 'more feedback'),
        ]
        assignment.get_submission.return_value = submission
        mock_get_assignment.return_value = assignment

        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(canvas_sak, [
            'grade-submission', 'CS249', 'Homework',
            '--canvasid', '42', '--grade', '95', '--message', 'New feedback',
            '--delete-previous', '--no-dryrun'
        ])

        assert result.exit_code == 0
        # should delete comments 10 and 12 (from user 99) but not 11 (from student)
        delete_calls = [c for c in submission._requester.request.call_args_list
                        if c[0][0] == 'DELETE']
        assert len(delete_calls) == 2
        assert '10' in delete_calls[0][0][1]
        assert '12' in delete_calls[1][0][1]

    @patch('canvas_sak.commands.grade_submission.get_canvas_object')
    @patch('canvas_sak.commands.grade_submission.get_course')
    @patch('canvas_sak.commands.grade_submission.get_assignment')
    def test_grade_negative_one_unsets_grade(self, mock_get_assignment,
                                             mock_get_course, mock_get_canvas):
        canvas = MagicMock()
        canvas.user_id = 99
        mock_get_canvas.return_value = canvas

        course = make_course()
        mock_get_course.return_value = course

        assignment = MagicMock()
        assignment.name = "Homework 1"
        assignment.id = 101
        submission = make_submission(user_id=42)
        submission.course_id = 1
        submission.assignment_id = 101
        submission.submission_comments = []
        assignment.get_submission.return_value = submission
        mock_get_assignment.return_value = assignment

        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(canvas_sak, [
            'grade-submission', 'CS249', 'Homework',
            '--canvasid', '42', '--grade', '-1', '--message', 'Regrade',
            '--delete-previous', '--no-dryrun'
        ])

        assert result.exit_code == 0
        submission.edit.assert_called_once_with(
            submission={'posted_grade': ''},
            comment={'text_comment': 'Regrade'}
        )

    @patch('canvas_sak.commands.grade_submission.get_canvas_object')
    @patch('canvas_sak.commands.grade_submission.get_course')
    @patch('canvas_sak.commands.grade_submission.get_assignment')
    def test_no_previous_comments_still_works(self, mock_get_assignment,
                                               mock_get_course, mock_get_canvas):
        canvas = MagicMock()
        canvas.user_id = 99
        mock_get_canvas.return_value = canvas

        course = make_course()
        mock_get_course.return_value = course

        assignment = MagicMock()
        assignment.name = "Homework 1"
        assignment.id = 101
        submission = make_submission(user_id=42)
        submission.course_id = 1
        submission.assignment_id = 101
        submission.submission_comments = []
        assignment.get_submission.return_value = submission
        mock_get_assignment.return_value = assignment

        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(canvas_sak, [
            'grade-submission', 'CS249', 'Homework',
            '--canvasid', '42', '--grade', '95', '--message', 'Feedback',
            '--delete-previous', '--no-dryrun'
        ])

        assert result.exit_code == 0
        submission.edit.assert_called_once()


class TestShowPreviousGrade:
    """Test that the current grade is shown before updating."""

    @patch('canvas_sak.commands.grade_submission.get_canvas_object')
    @patch('canvas_sak.commands.grade_submission.get_course')
    @patch('canvas_sak.commands.grade_submission.get_assignment')
    def test_shows_previous_grade_in_dryrun(self, mock_get_assignment,
                                             mock_get_course, mock_get_canvas):
        course = make_course()
        assignment = MagicMock()
        assignment.name = "Homework 1"
        submission = make_submission()
        submission.grade = '85'
        assignment.get_submission.return_value = submission

        mock_get_canvas.return_value = MagicMock()
        mock_get_course.return_value = course
        mock_get_assignment.return_value = assignment

        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(canvas_sak, [
            'grade-submission', 'CS249', 'Homework',
            '--canvasid', '42', '--grade', '95', '--message', 'Good work'
        ])

        assert result.exit_code == 0
        assert 'current grade: 85 (+10)' in result.stderr

    @patch('canvas_sak.commands.grade_submission.get_canvas_object')
    @patch('canvas_sak.commands.grade_submission.get_course')
    @patch('canvas_sak.commands.grade_submission.get_assignment')
    def test_shows_previous_grade_in_no_dryrun(self, mock_get_assignment,
                                                mock_get_course, mock_get_canvas):
        course = make_course()
        assignment = MagicMock()
        assignment.name = "Homework 1"
        submission = make_submission()
        submission.grade = '85'
        submission.edit.return_value = None
        assignment.get_submission.return_value = submission

        mock_get_canvas.return_value = MagicMock()
        mock_get_course.return_value = course
        mock_get_assignment.return_value = assignment

        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(canvas_sak, [
            'grade-submission', 'CS249', 'Homework',
            '--canvasid', '42', '--grade', '95', '--message', 'Good work',
            '--no-dryrun'
        ])

        assert result.exit_code == 0
        assert 'current grade: 85 (+10)' in result.stderr

    @patch('canvas_sak.commands.grade_submission.get_canvas_object')
    @patch('canvas_sak.commands.grade_submission.get_course')
    @patch('canvas_sak.commands.grade_submission.get_assignment')
    def test_shows_negative_delta(self, mock_get_assignment,
                                   mock_get_course, mock_get_canvas):
        course = make_course()
        assignment = MagicMock()
        assignment.name = "Homework 1"
        submission = make_submission()
        submission.grade = '95'
        assignment.get_submission.return_value = submission

        mock_get_canvas.return_value = MagicMock()
        mock_get_course.return_value = course
        mock_get_assignment.return_value = assignment

        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(canvas_sak, [
            'grade-submission', 'CS249', 'Homework',
            '--canvasid', '42', '--grade', '85', '--message', 'Regrade'
        ])

        assert result.exit_code == 0
        assert 'current grade: 95 (-10)' in result.stderr

    @patch('canvas_sak.commands.grade_submission.get_canvas_object')
    @patch('canvas_sak.commands.grade_submission.get_course')
    @patch('canvas_sak.commands.grade_submission.get_assignment')
    def test_shows_zero_delta(self, mock_get_assignment,
                               mock_get_course, mock_get_canvas):
        course = make_course()
        assignment = MagicMock()
        assignment.name = "Homework 1"
        submission = make_submission()
        submission.grade = '95'
        assignment.get_submission.return_value = submission

        mock_get_canvas.return_value = MagicMock()
        mock_get_course.return_value = course
        mock_get_assignment.return_value = assignment

        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(canvas_sak, [
            'grade-submission', 'CS249', 'Homework',
            '--canvasid', '42', '--grade', '95', '--message', 'Same'
        ])

        assert result.exit_code == 0
        assert 'current grade: 95 (+0)' in result.stderr

    @patch('canvas_sak.commands.grade_submission.get_canvas_object')
    @patch('canvas_sak.commands.grade_submission.get_course')
    @patch('canvas_sak.commands.grade_submission.get_assignment')
    def test_no_delta_for_non_numeric_grade(self, mock_get_assignment,
                                             mock_get_course, mock_get_canvas):
        course = make_course()
        assignment = MagicMock()
        assignment.name = "Homework 1"
        submission = make_submission()
        submission.grade = 'A'
        assignment.get_submission.return_value = submission

        mock_get_canvas.return_value = MagicMock()
        mock_get_course.return_value = course
        mock_get_assignment.return_value = assignment

        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(canvas_sak, [
            'grade-submission', 'CS249', 'Homework',
            '--canvasid', '42', '--grade', '95', '--message', 'Good'
        ])

        assert result.exit_code == 0
        assert 'current grade: A' in result.stderr
        assert '(+' not in result.stderr
        assert '(-' not in result.stderr

    @patch('canvas_sak.commands.grade_submission.get_canvas_object')
    @patch('canvas_sak.commands.grade_submission.get_course')
    @patch('canvas_sak.commands.grade_submission.get_assignment')
    def test_no_delta_when_unsetting_grade(self, mock_get_assignment,
                                            mock_get_course, mock_get_canvas):
        course = make_course()
        assignment = MagicMock()
        assignment.name = "Homework 1"
        submission = make_submission()
        submission.grade = '85'
        assignment.get_submission.return_value = submission

        mock_get_canvas.return_value = MagicMock()
        mock_get_course.return_value = course
        mock_get_assignment.return_value = assignment

        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(canvas_sak, [
            'grade-submission', 'CS249', 'Homework',
            '--canvasid', '42', '--grade', '-1', '--message', 'Clearing'
        ])

        assert result.exit_code == 0
        assert 'current grade: 85' in result.stderr
        assert '(+' not in result.stderr
        assert '(-' not in result.stderr

    @patch('canvas_sak.commands.grade_submission.get_canvas_object')
    @patch('canvas_sak.commands.grade_submission.get_course')
    @patch('canvas_sak.commands.grade_submission.get_assignment')
    def test_no_previous_grade_shows_nothing(self, mock_get_assignment,
                                              mock_get_course, mock_get_canvas):
        course = make_course()
        assignment = MagicMock()
        assignment.name = "Homework 1"
        submission = make_submission()
        submission.grade = None
        assignment.get_submission.return_value = submission

        mock_get_canvas.return_value = MagicMock()
        mock_get_course.return_value = course
        mock_get_assignment.return_value = assignment

        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(canvas_sak, [
            'grade-submission', 'CS249', 'Homework',
            '--canvasid', '42', '--grade', '95', '--message', 'Good work'
        ])

        assert result.exit_code == 0
        assert 'current grade' not in result.stderr


class TestOnlyChanges:
    """Test --only-changes skips update when grade is unchanged."""

    @patch('canvas_sak.commands.grade_submission.get_canvas_object')
    @patch('canvas_sak.commands.grade_submission.get_course')
    @patch('canvas_sak.commands.grade_submission.get_assignment')
    def test_skips_when_grade_unchanged(self, mock_get_assignment,
                                        mock_get_course, mock_get_canvas):
        course = make_course()
        assignment = MagicMock()
        assignment.name = "Homework 1"
        submission = make_submission()
        submission.grade = '95'
        submission.edit.return_value = None
        assignment.get_submission.return_value = submission

        mock_get_canvas.return_value = MagicMock()
        mock_get_course.return_value = course
        mock_get_assignment.return_value = assignment

        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(canvas_sak, [
            'grade-submission', 'CS249', 'Homework',
            '--canvasid', '42', '--grade', '95', '--message', 'Good',
            '--only-changes', '--no-dryrun'
        ])

        assert result.exit_code == 0
        submission.edit.assert_not_called()
        assert 'skipping' in result.stderr

    @patch('canvas_sak.commands.grade_submission.get_canvas_object')
    @patch('canvas_sak.commands.grade_submission.get_course')
    @patch('canvas_sak.commands.grade_submission.get_assignment')
    def test_skips_when_grade_unchanged_dryrun(self, mock_get_assignment,
                                                mock_get_course, mock_get_canvas):
        course = make_course()
        assignment = MagicMock()
        assignment.name = "Homework 1"
        submission = make_submission()
        submission.grade = '95'
        assignment.get_submission.return_value = submission

        mock_get_canvas.return_value = MagicMock()
        mock_get_course.return_value = course
        mock_get_assignment.return_value = assignment

        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(canvas_sak, [
            'grade-submission', 'CS249', 'Homework',
            '--canvasid', '42', '--grade', '95', '--message', 'Good',
            '--only-changes'
        ])

        assert result.exit_code == 0
        assert 'skipping' in result.stderr
        assert 'would grade' not in result.stderr

    @patch('canvas_sak.commands.grade_submission.get_canvas_object')
    @patch('canvas_sak.commands.grade_submission.get_course')
    @patch('canvas_sak.commands.grade_submission.get_assignment')
    def test_applies_when_grade_changed(self, mock_get_assignment,
                                        mock_get_course, mock_get_canvas):
        course = make_course()
        assignment = MagicMock()
        assignment.name = "Homework 1"
        submission = make_submission()
        submission.grade = '85'
        submission.edit.return_value = None
        assignment.get_submission.return_value = submission

        mock_get_canvas.return_value = MagicMock()
        mock_get_course.return_value = course
        mock_get_assignment.return_value = assignment

        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(canvas_sak, [
            'grade-submission', 'CS249', 'Homework',
            '--canvasid', '42', '--grade', '95', '--message', 'Updated',
            '--only-changes', '--no-dryrun'
        ])

        assert result.exit_code == 0
        submission.edit.assert_called_once()

    @patch('canvas_sak.commands.grade_submission.get_canvas_object')
    @patch('canvas_sak.commands.grade_submission.get_course')
    @patch('canvas_sak.commands.grade_submission.get_assignment')
    def test_applies_when_no_previous_grade(self, mock_get_assignment,
                                             mock_get_course, mock_get_canvas):
        course = make_course()
        assignment = MagicMock()
        assignment.name = "Homework 1"
        submission = make_submission()
        submission.grade = None
        submission.edit.return_value = None
        assignment.get_submission.return_value = submission

        mock_get_canvas.return_value = MagicMock()
        mock_get_course.return_value = course
        mock_get_assignment.return_value = assignment

        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(canvas_sak, [
            'grade-submission', 'CS249', 'Homework',
            '--canvasid', '42', '--grade', '95', '--message', 'First grade',
            '--only-changes', '--no-dryrun'
        ])

        assert result.exit_code == 0
        submission.edit.assert_called_once()

    @patch('canvas_sak.commands.grade_submission.get_canvas_object')
    @patch('canvas_sak.commands.grade_submission.get_course')
    @patch('canvas_sak.commands.grade_submission.get_assignment')
    def test_compares_numerically(self, mock_get_assignment,
                                   mock_get_course, mock_get_canvas):
        """95.0 and 95 should be considered the same grade."""
        course = make_course()
        assignment = MagicMock()
        assignment.name = "Homework 1"
        submission = make_submission()
        submission.grade = '95.0'
        submission.edit.return_value = None
        assignment.get_submission.return_value = submission

        mock_get_canvas.return_value = MagicMock()
        mock_get_course.return_value = course
        mock_get_assignment.return_value = assignment

        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(canvas_sak, [
            'grade-submission', 'CS249', 'Homework',
            '--canvasid', '42', '--grade', '95', '--message', 'Good',
            '--only-changes', '--no-dryrun'
        ])

        assert result.exit_code == 0
        submission.edit.assert_not_called()
        assert 'skipping' in result.stderr


class TestGradeSubmissionAttachment:
    """Test that --attachment uploads a file with the comment."""

    @patch('canvas_sak.commands.grade_submission.get_canvas_object')
    @patch('canvas_sak.commands.grade_submission.get_course')
    @patch('canvas_sak.commands.grade_submission.get_assignment')
    def test_dryrun_shows_attachment(self, mock_get_assignment, mock_get_course,
                                     mock_get_canvas):
        course = make_course()
        assignment = MagicMock()
        assignment.name = "Homework 1"
        assignment.points_possible = 100
        submission = make_submission()
        assignment.get_submission.return_value = submission

        mock_get_canvas.return_value = MagicMock()
        mock_get_course.return_value = course
        mock_get_assignment.return_value = assignment

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open('feedback.pdf', 'w') as f:
                f.write('fake pdf content')

            result = runner.invoke(canvas_sak, [
                'grade-submission', 'CS249', 'Homework',
                '--canvasid', '42', '--grade', '95', '--message', 'See attached',
                '--attachment', 'feedback.pdf'
            ])

        assert result.exit_code == 0
        submission.upload_comment.assert_not_called()

    @patch('canvas_sak.commands.grade_submission.get_canvas_object')
    @patch('canvas_sak.commands.grade_submission.get_course')
    @patch('canvas_sak.commands.grade_submission.get_assignment')
    def test_no_dryrun_uploads_attachment(self, mock_get_assignment,
                                          mock_get_course, mock_get_canvas):
        course = make_course()
        assignment = MagicMock()
        assignment.name = "Homework 1"
        assignment.points_possible = 100
        submission = make_submission()
        submission.edit.return_value = None
        submission.upload_comment.return_value = None
        assignment.get_submission.return_value = submission

        mock_get_canvas.return_value = MagicMock()
        mock_get_course.return_value = course
        mock_get_assignment.return_value = assignment

        runner = CliRunner(mix_stderr=False)
        with runner.isolated_filesystem():
            with open('feedback.pdf', 'w') as f:
                f.write('fake pdf content')

            result = runner.invoke(canvas_sak, [
                'grade-submission', 'CS249', 'Homework',
                '--canvasid', '42', '--grade', '95', '--message', 'See attached',
                '--attachment', 'feedback.pdf',
                '--no-dryrun'
            ])

        assert result.exit_code == 0
        submission.edit.assert_called_once_with(
            submission={'posted_grade': '95'},
            comment={'text_comment': 'See attached'}
        )
        submission.upload_comment.assert_called_once()
