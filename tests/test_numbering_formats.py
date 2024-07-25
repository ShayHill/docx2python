"""Test functions in docx2python.numbering_formats.py

:author: Shay Hill
:created: 6/26/2019
"""

from random import randint

import pytest

from docx2python.numbering_formats import (
    bullet,
    decimal,
    lower_letter,
    lower_roman,
    upper_letter,
    upper_roman,
)
from tests.helpers.utils import ARABIC_2_ROMAN


class TestLowerLetter:
    """Test numbering_formats.lower_letter"""

    def test_convert_positive_int(self) -> None:
        """Convert a positive integer to a string of letters"""
        assert lower_letter(1) == "a"
        assert lower_letter(26) == "z"
        assert lower_letter(27) == "aa"

    def test_zero(self) -> None:
        """Raise a value error for < 1"""
        with pytest.raises(ValueError) as msg:
            _ = lower_letter(0)
        assert "0 and <1 are not defined" in str(msg.value)

    def test_neg(self) -> None:
        """Raise a value error for < 1"""
        with pytest.raises(ValueError) as msg:
            _ = lower_letter(-1)
        assert "0 and <1 are not defined" in str(msg.value)


def test_upper_letter() -> None:
    """Same as lower_letter, but upper"""
    for _ in range(100):
        n = randint(1, 10000)
        assert upper_letter(n) == lower_letter(n).upper()


class TestLowerRoman:
    """Test numbering_formats.lower_roman"""

    def test_convert_positive_int(self) -> None:
        """Convert a positive integer to a string of letters"""
        for arabic, roman in ARABIC_2_ROMAN.items():
            assert lower_roman(arabic) == roman

    def test_zero(self) -> None:
        """Raise a value error for < 1"""
        with pytest.raises(ValueError) as msg:
            _ = lower_roman(0)
        assert "Roman" in str(msg.value)

    def test_neg(self) -> None:
        """Raise a value error for < 1"""
        with pytest.raises(ValueError) as msg:
            _ = lower_roman(-1)
        assert "Roman" in str(msg.value)


def test_upper_roman() -> None:
    """Same as lower_roman, but upper"""
    for _ in range(100):
        n = randint(1, 10000)
        assert upper_roman(n) == lower_roman(n).upper()


def test_decimal() -> None:
    """Return string representation of input"""
    for i in range(10):
        assert decimal(i) == str(i)


def test_bullet() -> None:
    """Return same string for every input."""
    for i in range(10):
        assert bullet(i) == bullet(i * 10)
