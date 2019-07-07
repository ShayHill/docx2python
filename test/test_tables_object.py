#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""Test docx2python.table_object

:author: Shay Hill
:created: 6/26/2019

"""
import pytest

from docx2python.depth_collector import CaretDepthError, DepthCollector


class TestDepthCollector:
    """Test tables_object.DepthCollector """

    def test_init(self) -> None:
        """Init containers"""
        inst = DepthCollector(3)
        assert inst.item_depth == 3
        assert inst.rightmost_branches == [[]]

    def test_last_caret(self) -> None:
        """Add empty list to caret[-1]. Append pointer to new list to caret. """
        inst = DepthCollector(3)
        inst.drop_caret()
        assert inst.rightmost_branches == [[[]], []]
        assert inst.rightmost_branches[-1] is inst.rightmost_branches[-2][-1]

    def test_caret_will_not_drop_past_item_depth(self) -> None:
        """Raise error before dropping caret past item_depth"""
        inst = DepthCollector(3)  # at depth 1
        inst.drop_caret()  # at depth 2
        inst.drop_caret()  # at depth 3 (item_depth)
        with pytest.raises(CaretDepthError):
            inst.drop_caret()

    def test_raise_caret(self) -> None:
        """Reduce caret list by one."""
        inst = DepthCollector(3)  # caret = [[]]
        inst.drop_caret()
        assert inst.rightmost_branches == [[[]], []]
        inst.raise_caret()
        assert inst.rightmost_branches == [[[]]]

    def test_caret_will_not_raise_past_root(self) -> None:
        """Raise error before raising caret to depth 0."""
        inst = DepthCollector(3)  # caret = [[]]
        with pytest.raises(CaretDepthError):
            inst.raise_caret()

    def test_set_caret(self) -> None:
        """Open or close branches to prepare for next branch or item."""
        inst = DepthCollector(3)
        inst.set_caret(3)
        assert inst.rightmost_branches == [[[[]]], [[]], []]
        inst.set_caret(2)
        assert inst.rightmost_branches == [[[[]]], [[]]]
        inst.set_caret(1)
        assert inst.rightmost_branches == [[[[]]]]

    def test_insert(self) -> None:
        """Place item at inst.item_depth."""
        inst = DepthCollector(5)
        inst.insert("text")
        assert inst.rightmost_branches[0] == [[[[["text"]]]]]
