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

from typing import List
from dataclasses import dataclass

from .text_runs import html_close, html_open


@dataclass
class Run:
    html_style: str
    text: str = ""

    def __str__(self):
        if self.text:
            return html_open(self.html_style) + self.text + html_close(self.html_style)
        return ""


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
        self._rPss = []  # current open run styles
        self._pPss = []  # current open run-style-type paragraph styles
        self._pStyles = []  # current open paragraph-only styles (e.g.: <h1>)
        self._par_queue = []  # for footnotes (add content before opening paragraph)
        self._rPr_queue = []  # for hyperlinks (add 'a href=""' as prop for next run)

        self._open_runs = []

    def queue_rPr(self, style: List[str]) -> None:
        self._rPr_queue += style

    def add_rPs(self, style: List[str]) -> None:
        self._rPss.append(style)

    def add_pPs(self, style: List[str]) -> None:
        self._pPss.append(style)

    def add_pStyle(self, style: str) -> None:
        self._pStyles.append(style)

    def open_paragraph(self) -> None:
        pass
        # if self._pStyles:
        #     self.insert(self._pStyles[-1], even_if_empty=True)
        # while self._par_queue:
        #     self.insert(self._par_queue.pop(0))
        # if self._pPss and self._pPss[-1]:
        #     self.insert(html_open(self._pPss[-1]))

    def close_paragraph(self) -> None:
        for run in self._open_runs:
            self.insert(str(run))
        self._open_runs = []
        # if self._pPss and self._pPss[-1]:
        #     self.insert(html_close(self._pPss[-1]))
        # self._pStyles = self._pStyles[:-1]
        # self._pPss = self._pPss[:-1]

    def queue_paragraph_text(self, string_: str) -> None:
        """
        Add text to be inserted when next paragraph is opened.

        :param string_: this text will appear after pStyle, before pPr
        :effect: add item to self._par_queue
        """
        self._par_queue.append(string_)

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

    def drop_caret(self) -> None:
        """Create a new branch under caret."""
        if self.caret_depth >= self.item_depth:
            raise CaretDepthError("will not lower caret beneath item_depth")
        self.rightmost_branches[-1].append([])
        self.rightmost_branches.append(self.rightmost_branches[-1][-1])
        if self.caret_depth == self.item_depth:
            self.open_paragraph()

    def raise_caret(self) -> None:
        """Close branch at caret and move up to parent."""
        if self.caret_depth == 1:
            raise CaretDepthError("will not raise caret above root")
        if self.caret_depth == self.item_depth:
            self.close_paragraph()
        self.rightmost_branches = self.rightmost_branches[:-1]

    def set_caret(self, depth: int) -> None:
        """
        Set caret at given depth.

        :param depth: depth level for caret (between 1 and item_depth inclusive)
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
            self.drop_caret()
        while self.caret_depth > depth:
            self.raise_caret()

    def insert(self, item: str, even_if_empty: bool = False) -> None:
        """Add item at item_depth. Add branches if necessary to reach depth."""
        self.set_caret(self.item_depth)
        if item or even_if_empty:
            self.caret.append(f"{item}")
        self._rPss = self._rPss[-1:]

    def insert_text(self, item: str) -> None:
        """
        Add text which might be wrapped in html tags.

        :param item:
        :return:

        This text catches any open run styles

        Don't wrap an empty style
        """
        if not self._open_runs:
            self._open_runs.append(Run(""))
        self._open_runs[-1].text += item
        # try:
        #     rPs = self._rPss.pop()
        # except IndexError:
        #     rPs = []
        # rPs[:0] = self._rPr_queue
        # if item and rPs:
        #     item = html_open(rPs) + item + html_close(rPs)
        # self.insert(item)
        # del self._rPr_queue[:]

    def insert_run(self, item: str, styled=False) -> None:
        """
        Close any open runs. Insert item. Renew previous style.
        """
        try:
            open_style = self._open_runs[-1].html_style
        except IndexError:
            open_style = ""
        if styled:
            self._open_runs.append(Run(open_style, item))
        else:
            self._open_runs.append(Run("", item))
        self._open_runs.append(Run(open_style))
