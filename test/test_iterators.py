#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""Test docx2python.iterators.py

author: Shay Hill
created: 6/28/2019
"""

import pytest

from docx2python.iterators import (
    IndexedItem,
    enum_at_depth,
    enum_cells,
    enum_paragraphs,
    enum_rows,
    enum_tables,
    iter_cells,
    iter_paragraphs,
    iter_rows,
    iter_tables,
)

TABLES = [
    [[["0000", "0001"], ["0010", "0011"]], [["0100", "0101"], ["0110", "0111"]]],
    [[["1000", "1001"], ["1010", "1011"]], [["1100", "1101"], ["1110", "1111"]]],
]


class TestOutOfRange:
    def test_enum_at_depth_low(self) -> None:
        """Raise ValueError when attempting to enumerate over depth < 1."""
        with pytest.raises(ValueError) as msg:
            tuple(enum_at_depth(TABLES, 0))
        assert "must be >= 1" in str(msg.value)

    def test_enum_at_depth_high(self) -> None:
        """Raise ValueError when attempting to enumerate over depth < 1."""
        with pytest.raises(TypeError) as msg:
            tuple(enum_at_depth(TABLES, 5))
        assert "will not iterate over sequence item" in str(msg.value)


class TestIterators:
    """Test iterators.iter_* """

    def test_iter_tables(self) -> None:
        assert list(iter_tables(TABLES)) == TABLES

    def test_iter_rows(self) -> None:
        assert list(iter_rows(TABLES)) == TABLES[0] + TABLES[1]

    def test_iter_cells(self) -> None:
        assert (
            list(iter_cells(TABLES))
            == TABLES[0][0] + TABLES[0][1] + TABLES[1][0] + TABLES[1][1]
        )

    def test_iter_paragraphs(self) -> None:
        assert (
            list(iter_paragraphs(TABLES))
            == TABLES[0][0][0]
            + TABLES[0][0][1]
            + TABLES[0][1][0]
            + TABLES[0][1][1]
            + TABLES[1][0][0]
            + TABLES[1][0][1]
            + TABLES[1][1][0]
            + TABLES[1][1][1]
        )


class TestEnumerators:

    """Test iterators.enum_* """

    def test_enum_tables(self) -> None:
        assert list(enum_tables(TABLES)) == [
            IndexedItem(
                index=(0,),
                value=[
                    [["0000", "0001"], ["0010", "0011"]],
                    [["0100", "0101"], ["0110", "0111"]],
                ],
            ),
            IndexedItem(
                index=(1,),
                value=[
                    [["1000", "1001"], ["1010", "1011"]],
                    [["1100", "1101"], ["1110", "1111"]],
                ],
            ),
        ]

    def test_enum_rows(self) -> None:
        assert list(enum_rows(TABLES)) == [
            IndexedItem(index=(0, 0), value=[["0000", "0001"], ["0010", "0011"]]),
            IndexedItem(index=(0, 1), value=[["0100", "0101"], ["0110", "0111"]]),
            IndexedItem(index=(1, 0), value=[["1000", "1001"], ["1010", "1011"]]),
            IndexedItem(index=(1, 1), value=[["1100", "1101"], ["1110", "1111"]]),
        ]

    def test_enum_cells(self) -> None:
        assert list(enum_cells(TABLES)) == [
            IndexedItem(index=(0, 0, 0), value=["0000", "0001"]),
            IndexedItem(index=(0, 0, 1), value=["0010", "0011"]),
            IndexedItem(index=(0, 1, 0), value=["0100", "0101"]),
            IndexedItem(index=(0, 1, 1), value=["0110", "0111"]),
            IndexedItem(index=(1, 0, 0), value=["1000", "1001"]),
            IndexedItem(index=(1, 0, 1), value=["1010", "1011"]),
            IndexedItem(index=(1, 1, 0), value=["1100", "1101"]),
            IndexedItem(index=(1, 1, 1), value=["1110", "1111"]),
        ]

    def test_enum_paragraphs(self) -> None:
        assert list(enum_paragraphs(TABLES)) == [
            IndexedItem(index=(0, 0, 0, 0), value="0000"),
            IndexedItem(index=(0, 0, 0, 1), value="0001"),
            IndexedItem(index=(0, 0, 1, 0), value="0010"),
            IndexedItem(index=(0, 0, 1, 1), value="0011"),
            IndexedItem(index=(0, 1, 0, 0), value="0100"),
            IndexedItem(index=(0, 1, 0, 1), value="0101"),
            IndexedItem(index=(0, 1, 1, 0), value="0110"),
            IndexedItem(index=(0, 1, 1, 1), value="0111"),
            IndexedItem(index=(1, 0, 0, 0), value="1000"),
            IndexedItem(index=(1, 0, 0, 1), value="1001"),
            IndexedItem(index=(1, 0, 1, 0), value="1010"),
            IndexedItem(index=(1, 0, 1, 1), value="1011"),
            IndexedItem(index=(1, 1, 0, 0), value="1100"),
            IndexedItem(index=(1, 1, 0, 1), value="1101"),
            IndexedItem(index=(1, 1, 1, 0), value="1110"),
            IndexedItem(index=(1, 1, 1, 1), value="1111"),
        ]
