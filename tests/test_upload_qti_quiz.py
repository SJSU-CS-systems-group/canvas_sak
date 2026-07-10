"""Tests for upload_qti_quiz."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from canvas_sak.commands.upload_qti_quiz import upload_qti_quiz


def test_upload_qti_quiz_finds_future_courses(tmp_path):
    """upload-qti-quiz must look up courses with is_active=False so quizzes
    can be uploaded to courses whose term has not started yet (the normal
    case when setting up next semester)."""
    qti_file = tmp_path / "quiz.zip"
    qti_file.write_bytes(b"fake zip")

    recorded = {}

    def fake_get_course(canvas, name, is_active=True):
        recorded["is_active"] = is_active
        raise SystemExit(0)

    with patch("canvas_sak.commands.upload_qti_quiz.get_canvas_object", MagicMock()), \
         patch("canvas_sak.commands.upload_qti_quiz.get_course", fake_get_course):
        CliRunner().invoke(upload_qti_quiz, ["My Course", str(qti_file)])

    assert recorded["is_active"] is False
