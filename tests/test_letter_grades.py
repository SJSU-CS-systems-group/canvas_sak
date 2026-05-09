"""Tests for letter-grade helpers in core."""

import pytest

from canvas_sak.core import to_letter_grade, points_to_letter, letter_grades


class TestPointsToLetter:
    def test_zero_returns_F_not_WU(self):
        """Bug repro: a literal 0 used to return 'WU' (withdrew unauthorized)
        because of the `if not points` early return. A real failing student
        with 0 points should be an F."""
        assert points_to_letter(0, 0) == "F"
        assert points_to_letter(0.0, 0) == "F"

    def test_none_returns_WU(self):
        """Missing/None grades still indicate no submission."""
        assert points_to_letter(None, 0) == "WU"

    def test_letter_thresholds_match_table(self):
        assert points_to_letter(96, 0) == "A+"
        assert points_to_letter(93, 0) == "A"
        assert points_to_letter(90, 0) == "A-"
        assert points_to_letter(86, 0) == "B+"
        assert points_to_letter(83, 0) == "B"
        assert points_to_letter(80, 0) == "B-"
        assert points_to_letter(76, 0) == "C+"
        assert points_to_letter(73, 0) == "C"
        assert points_to_letter(70, 0) == "C-"
        assert points_to_letter(60, 0) == "D-"
        assert points_to_letter(59, 0) == "F"

    def test_round_is_added(self):
        assert points_to_letter(89, 1) == "A-"


class TestToLetterGrade:
    def test_aligned_with_letter_grades_table(self):
        """to_letter_grade should agree with the letter_grades table at the
        coarse A/B/C/D/F level."""
        # Pick the coarse buckets from the table.
        for points, letter in letter_grades:
            coarse = letter[0]  # 'A+' -> 'A', 'B-' -> 'B', etc.
            assert to_letter_grade(points) == coarse, \
                f"score {points} should be {coarse} but got {to_letter_grade(points)}"

    def test_boundary_90_is_A(self):
        assert to_letter_grade(90) == "A"

    def test_boundary_80_is_B(self):
        assert to_letter_grade(80) == "B"

    def test_below_60_is_F(self):
        assert to_letter_grade(59) == "F"
        assert to_letter_grade(0) == "F"
