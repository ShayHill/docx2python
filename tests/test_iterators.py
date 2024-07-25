"""Test docx2python.iterators.py

author: Shay Hill
created: 6/28/2019
"""

import itertools as it

import pytest

from docx2python.iterators import (
    enum_at_depth,
    enum_cells,
    enum_paragraphs,
    enum_rows,
    enum_tables,
    get_html_map,
    iter_cells,
    iter_paragraphs,
    iter_rows,
    iter_tables,
)

TABLES = [
    [
        [[["0000", "0001"], ["0010", "0011"]], [["0100", "0101"], ["0110", "0111"]]],
        [[["1000", "1001"], ["1010", "1011"]], [["1100", "1101"], ["1110", "1111"]]],
    ]
]


class TestOutOfRange:
    def test_enum_at_depth_low(self) -> None:
        """Raise ValueError when attempting to enumerate over depth < 1."""
        with pytest.raises(ValueError) as msg:
            _ = tuple(enum_at_depth(TABLES, 0))  # type: ignore
        assert "depth argument must be 1, 2, 3, 4, or 5" in str(msg.value)

    def test_enum_at_depth_high(self) -> None:
        """Raise ValueError when attempting to enumerate over depth < 1."""
        with pytest.raises(ValueError) as msg:
            _ = tuple(enum_at_depth(TABLES, 6))  # type: ignore
        assert "depth argument must be 1, 2, 3, 4, or 5" in str(msg.value)


class TestIterators:
    """Test iterators.iter_*"""

    def test_iter_tables(self) -> None:
        """Return all tables."""
        assert list(iter_tables(TABLES)) == TABLES

    def test_iter_rows(self) -> None:
        """Return all rows."""
        assert list(iter_rows(TABLES)) == list(it.chain(*iter_tables(TABLES)))

    def test_iter_cells(self) -> None:
        """Return all cells."""
        assert list(iter_cells(TABLES)) == list(it.chain(*iter_rows(TABLES)))

    def test_iter_paragraphs(self) -> None:
        """Return all paragraphs."""
        assert list(iter_paragraphs(TABLES)) == list(it.chain(*iter_cells(TABLES)))


class TestEnumerators:
    """Test iterators.enum_*"""

    def test_enum_tables(self) -> None:
        """Return all tables."""
        assert list(enum_tables(TABLES)) == [
            (
                (0,),
                [
                    [
                        [["0000", "0001"], ["0010", "0011"]],
                        [["0100", "0101"], ["0110", "0111"]],
                    ],
                    [
                        [["1000", "1001"], ["1010", "1011"]],
                        [["1100", "1101"], ["1110", "1111"]],
                    ],
                ],
            )
        ]

    def test_enum_rows(self) -> None:
        """Return all rows."""
        assert list(enum_rows(TABLES)) == [
            (
                (0, 0),
                [
                    [["0000", "0001"], ["0010", "0011"]],
                    [["0100", "0101"], ["0110", "0111"]],
                ],
            ),
            (
                (0, 1),
                [
                    [["1000", "1001"], ["1010", "1011"]],
                    [["1100", "1101"], ["1110", "1111"]],
                ],
            ),
        ]

    def test_enum_cells(self) -> None:
        """Return all cells."""
        assert list(enum_cells(TABLES)) == [
            ((0, 0, 0), [["0000", "0001"], ["0010", "0011"]]),
            ((0, 0, 1), [["0100", "0101"], ["0110", "0111"]]),
            ((0, 1, 0), [["1000", "1001"], ["1010", "1011"]]),
            ((0, 1, 1), [["1100", "1101"], ["1110", "1111"]]),
        ]

    def test_enum_paragraphs(self) -> None:
        """Return all paragraphs."""
        assert list(enum_paragraphs(TABLES)) == [
            ((0, 0, 0, 0), ["0000", "0001"]),
            ((0, 0, 0, 1), ["0010", "0011"]),
            ((0, 0, 1, 0), ["0100", "0101"]),
            ((0, 0, 1, 1), ["0110", "0111"]),
            ((0, 1, 0, 0), ["1000", "1001"]),
            ((0, 1, 0, 1), ["1010", "1011"]),
            ((0, 1, 1, 0), ["1100", "1101"]),
            ((0, 1, 1, 1), ["1110", "1111"]),
        ]


class TestGetHtmlMap:
    """Test iterators.get_html_map"""

    def test_get_html_map(self) -> None:
        """Create valid html."""
        # fmt: off
        assert get_html_map(TABLES) == (
            "<html>"
            "<body>"
            '<table border="1">'
            "<tr>"
            "<td>"
            "<pre>(0, 0, 0, 0) 00000001"
            "</pre>"
            "<pre>(0, 0, 0, 1) 00100011"
            "</pre>"
            "</td>"
            "<td>"
            "<pre>(0, 0, 1, 0) 01000101"
            "</pre>"
            "<pre>(0, 0, 1, 1) 01100111"
            "</pre>"
            "</td>"
            "</tr>"
            "<tr>"
            "<td>"
            "<pre>(0, 1, 0, 0) 10001001"
            "</pre>"
            "<pre>(0, 1, 0, 1) 10101011"
            "</pre>"
            "</td>"
            "<td>"
            "<pre>(0, 1, 1, 0) 11001101"
            "</pre>"
            "<pre>(0, 1, 1, 1) 11101111"
            "</pre>"
            "</td>"
            "</tr>"
            "</table>"
            "</body>"
            "</html>"
        )
        # fmt: on
