"""Tests for upload_qti_quiz."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from canvas_sak.commands.upload_qti_quiz import upload_qti_quiz


def invoke_and_record_is_active(qti_file, extra_args=()):
    recorded = {}

    def fake_get_course(canvas, name, is_active=True):
        recorded["is_active"] = is_active
        raise SystemExit(0)

    with patch("canvas_sak.commands.upload_qti_quiz.get_canvas_object", MagicMock()), \
         patch("canvas_sak.commands.upload_qti_quiz.get_course", fake_get_course):
        CliRunner().invoke(upload_qti_quiz, ["My Course", str(qti_file), *extra_args])

    return recorded["is_active"]


def test_upload_qti_quiz_defaults_to_active_courses(tmp_path):
    """By default upload-qti-quiz only searches active courses."""
    qti_file = tmp_path / "quiz.zip"
    qti_file.write_bytes(b"fake zip")

    assert invoke_and_record_is_active(qti_file) is True


def test_upload_qti_quiz_inactive_flag_finds_future_courses(tmp_path):
    """--inactive lets upload-qti-quiz find courses whose term has not
    started yet (the normal case when setting up next semester)."""
    qti_file = tmp_path / "quiz.zip"
    qti_file.write_bytes(b"fake zip")

    assert invoke_and_record_is_active(qti_file, ["--inactive"]) is False
