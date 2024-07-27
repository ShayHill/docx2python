"""Attempt to properly handle merged table cells.

:author: Shay Hill
:created: 2023-01-23
"""

from docx2python import docx2python
from tests.conftest import RESOURCES


class TestMergedCells:
    def test_duplicate_merged_cells_false(self):
        """By default, duplicate merged cells."""
        with docx2python(
            RESOURCES / "merged_cells.docx", duplicate_merged_cells=False
        ) as content:
            # fmt: off
            assert content.body == [
                [
                    [["0-0"],  ["0-12"],  [""],  ["0-3"]],
                    [["12-0"], ["1-1"],    ["1-2"],    ["1-3"]],
                    [[""],     ["2-1"],    ["2-2"],    ["2-3"]],
                    [["3-0"],  ["34-123"], [""], [""]],
                    [["4-0"],  [""], [""], [""]],
                ],
                [[[""]]],
            ]
            # fmt: on

    def test_duplicate_merged_cells_true(self):
        """Duplicate contents in merged cells for an mxn table list."""
        with docx2python(RESOURCES / "merged_cells.docx") as content:
            # fmt: off
            assert content.body == [
                [
                    [["0-0"],  ["0-12"],   ["0-12"],   ["0-3"]],
                    [["12-0"], ["1-1"],    ["1-2"],    ["1-3"]],
                    [["12-0"], ["2-1"],    ["2-2"],    ["2-3"]],
                    [["3-0"],  ["34-123"], ["34-123"], ["34-123"]],
                    [["4-0"],  ["34-123"], ["34-123"], ["34-123"]],
                ],
                [[[""]]],
            ]
            # fmt: on
