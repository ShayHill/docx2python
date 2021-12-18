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

from contextlib import suppress
from dataclasses import dataclass, field
from typing import List, Optional, Union

from .text_runs import html_close, html_open


@dataclass
class Run:
    html_style: List[str] = field(default_factory=list)
    text: str = field(default="")

    def __str__(self):
        if self.text:
            return html_open(self.html_style) + self.text + html_close(self.html_style)
        return ""


@dataclass
class Par:
    html_style: List[str]
    runs: List[Run] = field(default_factory=list)

    @property
    def strings(self) -> List[str]:
        return [x for x in (str(y) for y in self.runs) if x]


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
        # TODO: factor out item_depth
        self.item_depth = item_depth
        self._par_depth = 4
        self._rightmost_branches = [[]]

        self._open_pars = []
        self._orphan_runs = []

    @staticmethod
    def _get_run_strings(runs: List[Run]) -> List[str]:
        """
        Return a string for each run in the current open paragraph. Ignore ""
        """
        return [x for x in (str(x) for x in runs) if x]

    def commence_paragraph(self, html_style: Optional[List[str]] = None) -> Par:
        html_style = html_style or []
        new_par = Par(html_style, self._orphan_runs + [Run([], html_open(html_style))])
        self._orphan_runs = []
        self._open_pars.append(new_par)
        return new_par

    def conclude_paragraph(self) -> None:
        old_par = self._open_pars.pop()
        old_par.runs.append(Run("", html_close(old_par.html_style)))
        self.insert(old_par.strings)

    def commence_run(self, html_style: str = "") -> None:
        self._open_runs.append(Run(html_style))

    def conclude_run(self) -> None:
        self.commence_run()

    @property
    def tree(self) -> List:
        """All collected items."""
        return self._rightmost_branches[0]

    @property
    def caret(self) -> List:
        """Lowest open child."""
        return self._rightmost_branches[-1]

    @property
    def caret_depth(self) -> int:
        return len(self._rightmost_branches)

    @property
    def _open_runs(self) -> List[Run]:
        with suppress(IndexError):
            return self._open_pars[-1].runs
        return self._orphan_runs

    @property
    def _open_run(self) -> Run:
        if not self._open_runs:
            self._open_runs.append(Run())
        return self._open_runs[-1]

    def _drop_caret(self) -> None:
        """Create a new branch under caret."""
        if self.caret_depth >= self.item_depth:
            raise CaretDepthError("will not lower caret beneath item_depth")
        self._rightmost_branches[-1].append([])
        self._rightmost_branches.append(self._rightmost_branches[-1][-1])

    def _raise_caret(self) -> None:
        """Close branch at caret and move up to parent."""
        if self.caret_depth == 1:
            raise CaretDepthError("will not raise caret above root")
        self._rightmost_branches = self._rightmost_branches[:-1]

    def set_caret(self, depth: Union[None, int]) -> None:
        """
        Set caret at given depth.

        :param depth: depth level for caret (between 1 and item_depth inclusive)
        another at the same depth. This is how consecutive paragraphs avoid being
        merged into one paragraph. You'll want this true for every element except
        text runs. :depth: == None means the element (perhaps ``body``) does not
        effect depth (see details in docx_text._get_elem_depth).
        """
        if depth is None:
            return
        while self.caret_depth < depth:
            self._drop_caret()
        while self.caret_depth > depth:
            self._raise_caret()

    def insert(self, item: List[str]) -> None:
        """Add item at self._par_depth. Add branches if necessary to reach depth.

        This dumps the contents of the most recently closed paragraph into the
        _rightmost_branches collector.
        """
        self.set_caret(self._par_depth)
        self._rightmost_branches[-1].append(item)

    def add_text_into_open_run(self, item: str) -> None:
        """
        Add item into previous run.

        This is for tags and other text that appears between run tags. All entries to
        ``add_text_into_open_run`` will be merged together.
        """
        self._open_run.text += item

    def insert_text_as_new_run(self, item: str, styled=False) -> None:
        """
        Close previous run, cache style, open and close new run, re-open cached style.

        This is for items like links that may be inside a run element with other text.

        Paraphrased in html:

            <run><b>some text<a href="">link</a>other text</b></run>

        Starts with an open run
            <run><b>some text

        Then hits the link. We'll make this a run inside the actual run

            <run><b>some text</b></run>  # close this open run
            <run><a href="">link</a></run>  # add link as a new run
            <run><b>  # open a new run with the same style as the aborted first run
        """
        open_style = self._open_run.html_style
        if styled:
            self._open_runs.append(Run(open_style, item))
        else:
            self._open_runs.append(Run("", item))
        self._open_runs.append(Run(open_style))
