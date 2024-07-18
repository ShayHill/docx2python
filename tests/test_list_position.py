"""Test list_position attribute of list paragraphs.

:author: Shay Hill
:created: 2024-07-17
"""

from docx2python.iterators import iter_at_depth
from docx2python.main import docx2python
from tests.conftest import RESOURCES


class TestListPosition:
    def test_explicit(self):
        # """List paragraphs match hand-counted list_position."""
        with docx2python(RESOURCES / "example.docx") as content:
            pars = iter_at_depth(content.officeDocument_pars, 4)
        positions = [p.list_position for p in pars]
        assert positions == [
            ("2", [1]),
            ("2", [1, 1]),
            ("2", [1, 2]),
            ("2", [1, 2, 1]),
            ("2", [1, 2, 1, 1]),
            ("2", [1, 2, 1, 2]),
            ("2", [1, 2, 1, 2, 1]),
            ("2", [1, 2, 1, 2, 1, 1]),
            ("2", [1, 2, 1, 2, 1, 1, 1]),
            ("2", [1, 2, 1, 2, 1, 1, 2]),
            ("2", [2]),
            ("2", [2, 1]),
            ("1", [1]),
            ("1", [1, 1]),
            ("1", [1, 1, 1]),
            (None, []),
            (None, []),
            (None, []),
            (None, []),
            (None, []),
            (None, []),
            (None, []),
            (None, []),
            (None, []),
            (None, []),
            (None, []),
            (None, []),
            (None, []),
            (None, []),
            (None, []),
            (None, []),
            (None, []),
            (None, []),
            (None, []),
            (None, []),
            (None, []),
            (None, []),
            (None, []),
            (None, []),
        ]
