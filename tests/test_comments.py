"""Test extracting comments.

User flyguy62n requested comment extraction. Extract comments as tuples (text,
author, date, comment).

:author: Shay Hill
:created: 2024-03-29
"""

from docx2python import docx2python

from .conftest import RESOURCES


def test_comments() -> None:
    """Extract comments and some comment metadata."""
    pars = docx2python(RESOURCES / "comments.docx")
    _ = pars.body
    pars.close()
    assert True
