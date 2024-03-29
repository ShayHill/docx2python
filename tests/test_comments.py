"""Test extracting comments.

User flyguy62n requested comment extraction. Extract comments as tuples (text,
author, date, comment).

:author: Shay Hill
:created: 2024-03-29
"""
import os
import sys

project = os.path.abspath(os.path.join(__file__, "..", ".."))
sys.path.append(project)

from docx2python import docx2python
from pathlib import Path

# from .conftest import RESOURCES
RESOURCES = Path(project, "tests", "resources")


def test_comments() -> None:
    """Extract comments and some comment metadata."""
    pars = docx2python(RESOURCES / "comments.docx")
    comments = pars.comments
    pars.close()
    assert comments == [
        (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "Randy Bartels",
            "2024-03-28T17:22:00Z",
            "COMMENT",
        ),
        (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "Randy Bartels",
            "2024-03-28T17:22:00Z",
            "RESPONSE",
        ),
        (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "Shay Hill",
            "2024-03-29T12:10:00Z",
            "Response from Shay Hill",
        ),
        (
            "tempor incididunt ut labore et dolore magna aliqua.",
            "Shay Hill",
            "2024-03-29T12:28:00Z",
            "Comment on subset starting with tempor",
        ),
        (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "Randy Bartels",
            "2024-03-28T17:22:00Z",
            "COMMENT on par 5",
        ),
        (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "Randy Bartels",
            "2024-03-28T17:22:00Z",
            "RESPONSE to comment on par 5",
        ),
        (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "Shay Hill",
            "2024-03-29T12:10:00Z",
            "Response from Shay Hill on par 5",
        ),
        (
            "tempor incididunt ut labore et dolore magna aliqua.",
            "Shay Hill",
            "2024-03-29T12:28:00Z",
            "Comment on subset starting with tempor on par 5",
        ),
    ]

def test_no_comments() -> None:
    """Return an empty list when no comments are present."""
    pars = docx2python(RESOURCES / "apples_and_pears.docx")
    comments = pars.comments
    pars.close()
    assert comments == []

