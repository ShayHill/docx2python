#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""Collect xml text in a nested list

:author: Shay Hill
:created: 6/26/2019

::

    [  # tables
        [  # table
            [  # row
                [  # cell
                    [  # paragraph
                        ""  # text run
                    ]
                ]
            ]
        ]
    ]

Text in table cells and text outside of a table must be captured at depth=5. To keep
track of this, these few methods will put text where it needs to be.

The package will recursively descend into elements in the docx file, so the point at
which a table, row, cell, paragraph, or text run begins and ends is known. Drop and
raise the caret when these items are opened or closed in the xml. Insert text when
found.

Shorthand for this package. Instances of this class should not escape the package.
Pass out of package with depth_collector_instance.tree.
"""

from typing import Any, List, Tuple
from .text_runs import style_open, style_close
import re


class CaretDepthError(Exception):
    """Caller attempted to raise or lower DepthCollector caret out of range"""


class DepthCollector:
    """Insert items into a tree at a consistent depth."""

    def __init__(self, item_depth: int) -> None:
        """
        Record item depth and initiate data container.

        :param item_depth: content will only appear at this depth, though empty lists
            may appear above. I.e., this is how many brackets to open before inserting
            an item. E.g., item_depth = 3 => [[['item']]].
        """
        self.item_depth = item_depth
        self.rightmost_branches = [[]]
        self._run_styles = []
        self._par_styles = []
        self._pStyles = []
        self.run_queue = ""  # prefix for next run (for bullets, footnotes, etc.)
        self.log = []

    def set_run_style(self, style: List[str]) -> None:
        self._run_styles = style

    def add_pStyle(self, style: str) -> None:
        self._pStyles.append(style)

    def del_pStyle(self) -> None:
        self._pStyles = self._par_styles[:-1]

    def add_par_style(self, style: List[str]) -> None:
        self._par_styles.append(style)

    def del_par_style(self) -> None:
        self._par_styles = self._par_styles[:-1]

    def close_paragraph(self) -> None:
        if self._par_styles and self._par_styles[-1]:
            if self._par_styles[-1]:
                self.insert(style_close(self._par_styles[-1]))
            self.del_par_style()

    def open_paragraph(self) -> None:
        if self._par_styles and self._par_styles[-1]:
            self.insert(style_open(self._par_styles[-1]))

    @property
    def tree(self) -> List:
        """All collected items."""
        return self.rightmost_branches[0]

    @property
    def caret(self) -> List:
        """Lowest open child."""
        return self.rightmost_branches[-1]

    @property
    def caret_depth(self) -> int:
        return len(self.rightmost_branches)

    def drop_caret(self, reason="") -> None:
        """Create a new branch under caret."""
        if self.caret_depth >= self.item_depth:
            raise CaretDepthError("will not lower caret beneath item_depth")
        self.rightmost_branches[-1].append([])
        self.rightmost_branches.append(self.rightmost_branches[-1][-1])
        reason = reason + f"_dc_{self.caret_depth}"
        self.log.append(reason)
        if self.caret_depth == self.item_depth:
            self.open_paragraph()

    def raise_caret(self, reason="") -> None:
        """Close branch at caret and move up to parent."""
        # TODO: factor out self log
        if self.caret_depth == 1:
            raise CaretDepthError("will not raise caret above root")
        if self.caret_depth == self.item_depth:
            self.close_paragraph()
        self.rightmost_branches = self.rightmost_branches[:-1]
        reason = reason + f"_rc_{self.caret_depth}"
        self.log.append(reason)

    def set_caret(self, depth: int, reset: bool = True, reason="setting caret") -> None:
        """
        Set caret at given depth.

        :param depth: depth level for caret (between 1 and item_depth inclusive)
        :param reset: if caret is already at depth, close nested list and open
        another at the same depth. This is how consecutive paragraphs avoid being
        merged into one paragraph. You'll want this true for every element except
        text runs.
        """
        """Set caret at given depth."""
        if depth == None:
            return
        # if reset and self.caret_depth > 1 and depth == self.caret_depth:
        #     self.raise_caret(reason + f"_{self.caret_depth} -> {depth}")
        while self.caret_depth < depth:
            self.drop_caret(reason)
        while self.caret_depth > depth:
            self.raise_caret(reason)

    def insert(self, item: str) -> None:
        """Add item at item_depth. Add branches if necessary to reach depth."""
        if item:
            self.set_caret(self.item_depth, reset=False)
            # if not self.caret and self._par_styles:
            #     self.caret.append(self._par_styles[-1])
        if item.strip(" \t\n") and not re.match("----.*----", item):
            prefix = style_open(self._run_styles)
            suffix = style_close(self._run_styles)
            self.caret.append(f"{prefix}{item}{suffix}")
        elif item:
            self.caret.append(f"{item}")
        self._run_styles = []
