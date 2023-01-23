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

from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass, field
from typing import Any, Iterable

from .text_runs import html_close, html_open


@dataclass
class Run:
    """A text run. Html styles and text content"""

    html_style: list[str] = field(default_factory=list)
    text: str = field(default="")

    def __str__(self) -> str:
        """Return any text content in the run

        :return: text content or "" if none
        """
        if self.text:
            return html_open(self.html_style) + self.text + html_close(self.html_style)
        return ""


@dataclass
class Par:
    """A text paragraph. Html styles and a list of run strings"""

    html_style: list[str]
    runs: list[Run] = field(default_factory=list)

    @property
    def strings(self) -> list[str]:
        """Return a list of strings from the runs

        :return: a string for each run with text content
        """
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

        self._rightmost_branches: list[Any] = [[]]

        self.open_pars: list[Par] = []
        self.orphan_runs: list[Run] = []

    def view_branch(self, address: Iterable[int]) -> Any:
        """Return the item at the given address

        :param address: a tuple of indices to the item to be returned
        :return: the item at the address
        """
        branch = self._rightmost_branches
        for i in address:
            branch = branch[i]
        return branch

    @staticmethod
    def _get_run_strings(runs: list[Run]) -> list[str]:
        """Return a string for each run in the current open paragraph. Ignore ""

        :param runs: list of runs
        :return: a string for each run with text content
        """
        return [x for x in (str(x) for x in runs) if x]

    def commence_paragraph(self, html_style: list[str] | None = None) -> Par:
        """Gather any cached runs and open a new paragraph.

        :param html_style: html style to apply to the paragraph
        :return: the new paragraph
        """
        html_style = html_style or []
        new_par = Par(html_style, self.orphan_runs + [Run([], html_open(html_style))])
        self.orphan_runs = []
        self.open_pars.append(new_par)
        return new_par

    def conclude_paragraph(self) -> None:
        """Close the current paragraph and add it to the tree."""
        old_par = self.open_pars.pop()
        old_par.runs.append(Run([], html_close(old_par.html_style)))
        self.insert(old_par.strings)

    def commence_run(self, html_style: list[str] | None = None) -> None:
        """Open a new run and add it to the current paragraph.

        :param html_style: html style to apply to the run
        """
        self._open_runs.append(Run(html_style or []))

    def conclude_run(self) -> None:
        """Close the current run and add it to the current paragraph."""
        self.commence_run()

    @property
    def tree(self) -> list[str | list[str]]:
        """All collected items.

        :return: a nested list of _par_depth + 1 levels
        """
        return self._rightmost_branches[0]

    @property
    def caret(self) -> list[str | list[str]]:
        """Lowest open child.

        :return: the list where new content will be appended
        """
        return self._rightmost_branches[-1]

    @property
    def caret_depth(self) -> int:
        """Depth of the lowest open child.

        :return: from 0 to _par_depth, the depth of the last-closed element in the
            tree.
        """
        return len(self._rightmost_branches)

    @property
    def _open_runs(self) -> list[Run]:
        """Runs in the current paragraph.

        :return: a list of runs
        """
        with suppress(IndexError):
            return self.open_pars[-1].runs
        return self.orphan_runs

    @property
    def _open_run(self) -> Run:
        """The last run in the current paragraph.

        :return: a run
        """
        if not self._open_runs:
            self._open_runs.append(Run())
        return self._open_runs[-1]

    def _drop_caret(self) -> None:
        """Create a new branch under caret.

        :raise CaretDepthError: if caret is already at the maximum depth
        :return: None
        """
        if self.caret_depth >= self.item_depth:
            raise CaretDepthError("will not lower caret beneath item_depth")
        self._rightmost_branches[-1].append([])
        self._rightmost_branches.append(self._rightmost_branches[-1][-1])

    def _raise_caret(self) -> None:
        """Close branch at caret and move up to parent.

        :raise CaretDepthError: if there is no outside list to which to ascend
        """
        if self.caret_depth == 1:
            raise CaretDepthError("will not raise caret above root")
        self._rightmost_branches = self._rightmost_branches[:-1]

    def set_caret(self, depth: None | int) -> None:
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

    def insert(self, item: list[str]) -> None:
        """Add item at self._par_depth. Add branches if necessary to reach depth.

        :param item: list of strings to insert at caret

        This dumps the contents of the most recently closed paragraph into the
        _rightmost_branches collector.
        """
        self.set_caret(self._par_depth)
        self._rightmost_branches[-1].append(item)

    def add_text_into_open_run(self, item: str) -> None:
        """
        Add item into previous run.

        :param item: string to insert into previous run

        This is for tags and other text that appears between run tags. All entries to
        ``add_text_into_open_run`` will be merged together.
        """
        self._open_run.text += item

    def insert_text_as_new_run(self, item: str, styled: bool = False) -> None:
        """
        Close previous run, cache style, open and close new run, re-open cached style.

        :param item: string to insert into new run
        :param styled: True if item has associated html styles

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
            self._open_runs.append(Run([], item))
        self._open_runs.append(Run(open_style))
