"""Collect xml text in a nested list

:author: Shay Hill
:created: 6/26/2019

::

    [  # document
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

import dataclasses
import itertools as it
from contextlib import suppress
from typing import (
    TYPE_CHECKING,
    Any,
    Iterable,
    Iterator,
    List,
    Literal,
    Tuple,
    Union,
    cast,
)

from docx2python.attribute_register import get_localname
from docx2python.iterators import enum_at_depth
from docx2python.text_runs import (
    get_paragraph_formatting,
    get_pStyle,
    get_run_formatting,
    html_close,
    html_open,
)

if TYPE_CHECKING:
    from lxml.etree import _Element as EtreeElement  # type: ignore

    from docx2python.docx_reader import File


MaybeStr = Union[str, None]
Lineage = Tuple[Literal["document"], MaybeStr, MaybeStr, MaybeStr, MaybeStr]


@dataclasses.dataclass
class Run:
    """A text run. Html styles and text content"""

    html_style: list[str] = dataclasses.field(default_factory=list)
    text: str = ""

    def __str__(self) -> str:
        """Return any text content in the run

        :return: text content or "" if none
        """
        if self.text:
            return html_open(self.html_style) + self.text + html_close(self.html_style)
        return ""


@dataclasses.dataclass
class Par:
    """A text paragraph. Html styles and a list of run strings.

    list_position is where a paragraph falls in a list, if it is in a list at all.

    (None, []) means the paragraph is not in a list.
    ("1", [1]) means the paragraph is the first item in list "1".
    ("1", [1, 2]) means the paragraph is in list "1" here:
        1. item 1
            1. item (1, 1)
            2. item (1, 2)  # this paragraph
    """

    html_style: list[str]
    style: str
    lineage: Lineage
    runs: list[Run] = dataclasses.field(default_factory=list)
    list_position: tuple[str | None, list[int]] = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        """Set list_position to None"""
        self.list_position = (None, [])

    @property
    def run_strings(self) -> list[str]:
        """Return a list of strings from the runs

        :return: a string for each run with text content
        """
        return [x for x in (str(y) for y in self.runs) if x]


ParsTable = List[List[List[List[Par]]]]
TextTable = List[List[List[List[List[str]]]]]


def get_par_strings(nested_pars: ParsTable) -> TextTable:
    """Convert DepthCollector's nested Par instances into a nested list of strings.

    :param nested_pars: a list of Par instances. These will be the first element in
        the DepthCollector's tables list [[[[Par]]]]
    :return: a list of strings from the runs [[[[[str]]]]]
    """
    as_run_strings_lists: TextTable = []
    for tbl in nested_pars:
        as_run_strings_lists.append([])
        for row in tbl:
            as_run_strings_lists[-1].append([])
            for cell in row:
                as_run_strings_lists[-1][-1].append([])
                for par in cell:
                    as_run_strings_lists[-1][-1][-1].append(par.run_strings)

    return as_run_strings_lists


class CaretDepthError(Exception):
    """Caller attempted to raise or lower DepthCollector caret out of range"""


class DepthCollector:
    """Insert items into a tree at a consistent depth."""

    def __init__(self, file: File) -> None:
        """
        Record item depth and initiate data container.

        :param item_depth: content will only appear at this depth, though empty lists
            may appear above. I.e., this is how many brackets to open before inserting
            an item. E.g., item_depth = 3 => [[['item']]].
        """
        self._xml2html_format = file.context.xml2html_format
        self._par_depth: Literal[1, 2, 3, 4] = 4

        self._lineage: Lineage = ("document", None, None, None, None)
        self._rightmost_branches: list[Any] = [[]]

        self.open_pars: list[Par] = []
        self.orphan_runs: list[Run] = []

        self.comment_ranges: dict[str, tuple[int, int]] = {}

    def _set_in_lineage(self, index: Literal[1, 2, 3, 4], value: str | None):
        """Set a value in the lineage tuple."""
        prev = self._lineage[1:index]
        aftr = self._lineage[index + 1 :]
        tbl, row, cell, par = it.chain(prev, [value], aftr)
        self._lineage = ("document", tbl, row, cell, par)

    @property
    def _runs_so_far(self) -> Iterator[str]:
        """Return all runs seen so far.

        This is to mark the beginning and end of comment ranges.
        """
        for run_text in enum_at_depth(self.tree_text, 5):
            if run_text:
                yield cast(str, run_text)
        for par in self.open_pars:
            yield from par.run_strings
        for run in self.orphan_runs:
            if run.text:
                yield run.text

    def _count_runs(self) -> int:
        """Count the number of runs seen so far in current and previous paragraphs."""
        return len(list(self._runs_so_far))

    def start_comment_range(self, id_: str) -> None:
        """Start a comment range at the given address.

        :param id_: the `w:id` of the `w:commentRangeStart` element
        """
        cruns = self._count_runs()
        self.comment_ranges[id_] = (cruns, cruns)

    def end_comment_range(self, id_: str) -> None:
        """Start a comment range at the given address.

        :param id_: the `w:id` of the `w:commentRangeEnd` element
        """
        cruns = self._count_runs()
        beg = self.comment_ranges[id_][0]
        self.comment_ranges[id_] = (beg, cruns)

    def view_branch(self, address: Iterable[int]) -> Any:
        """Return the item at the given address

        :param address: a tuple of indices to the item to be returned
        :return: the item at the address.
            Returns a list of lists (of lists, ...) of strings
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

    def commence_paragraph(self, elem: EtreeElement | None = None) -> Par:
        """Gather any cached runs and open a new paragraph.

        :param elem: the paragraph element (for extracting style information)
        :return: the new paragraph
        """
        html_style: list[str] = []
        if elem is not None:
            html_style = get_paragraph_formatting(elem, self._xml2html_format) or []

        pStyle = ""
        if elem is not None:
            pStyle = get_pStyle(elem)

        new_par = Par(
            html_style,
            pStyle,
            self._lineage,
            [*self.orphan_runs, Run([], html_open(html_style))],
        )
        self.orphan_runs = []
        self.open_pars.append(new_par)
        return new_par

    def conclude_paragraph(self) -> None:
        """Close the current paragraph and add it to the tree."""
        old_par = self.open_pars.pop()
        old_par.runs.append(Run([], html_close(old_par.html_style)))
        self.insert(old_par)

    def commence_run(self, elem: EtreeElement | None = None) -> None:
        """Open a new run and add it to the current paragraph.

        :param elem: the run element (for extracting style information)
        """
        html_style: list[str] | None = None
        if elem is not None:
            html_style = get_run_formatting(elem, self._xml2html_format)
        html_style = html_style or []
        self._open_runs.append(Run(html_style or []))

    def conclude_run(self) -> None:
        """Close the current run and add it to the current paragraph."""
        self.commence_run()

    @property
    def tree(self) -> ParsTable:
        """All collected paragraphs as Par instances.

        :return: a nested list of _par_depth + 1 levels
        """
        return self._rightmost_branches[0]

    @property
    def tree_text(self) -> TextTable:
        """All collected paragraphs as lists of strings.

        :return: a string of all text in the tree
        """
        return get_par_strings(self.tree)

    @property
    def caret(self) -> list[str | list[str]]:
        """Lowest open child.

        :return: the list where new content will be appended
        """
        return self._rightmost_branches[-1]

    @property
    def caret_depth(self) -> Literal[1, 2, 3, 4]:
        """Depth of the lowest open child.

        :return: from 0 to _par_depth, the depth of the last-closed element in the
            tree.
        """
        return cast(Literal[1, 2, 3, 4], len(self._rightmost_branches))

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
        if self.caret_depth >= self._par_depth:
            raise CaretDepthError("will not lower caret beneath paragraph depth")
        self._rightmost_branches[-1].append([])
        self._rightmost_branches.append(self._rightmost_branches[-1][-1])

    def _raise_caret(self) -> None:
        """Close branch at caret and move up to parent.

        :raise CaretDepthError: if there is no outside list to which to ascend
        """
        if self.caret_depth == 1:
            raise CaretDepthError("will not raise caret above root")
        self._rightmost_branches = self._rightmost_branches[:-1]

    def set_caret(
        self, depth: None | Literal[1, 2, 3, 4], elem: EtreeElement | None = None
    ) -> None:
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
        if self.caret_depth == depth:
            lineage_at = None if elem is None else get_localname(elem)
            self._set_in_lineage(depth, lineage_at)
            return
        if self.caret_depth < depth:
            self._drop_caret()
        elif self.caret_depth > depth:
            self._set_in_lineage(depth, None)
            self._raise_caret()
        self.set_caret(depth, elem)

    def insert(self, par: Par) -> None:
        """Add item at self._par_depth. Add branches if necessary to reach depth.

        :param item: list of strings to insert at caret

        This dumps the contents of the most recently closed paragraph into the
        _rightmost_branches collector.
        """
        self.set_caret(self._par_depth)
        self._rightmost_branches[-1].append(par)

    def add_text_into_open_run(self, item: str) -> None:
        """
        Add item into previous run.

        :param item: string to insert into previous run

        This is for formatting tags and other text that appears between run tags. All
        entries to ``add_text_into_open_run`` will be merged together.
        """
        if self._xml2html_format:
            item = item.replace("&", "&amp;")
            item = item.replace("<", "&lt;")
            item = item.replace(">", "&gt;")
        self._open_run.text += item

    def add_code_into_open_run(self, item: str) -> None:
        """
        Add text into previous run without escaping symbols.

        :param item: string to insert into previous run
        """
        self._open_run.text += item

    def insert_text_as_new_run(self, item: str) -> None:
        """
        Close previous run, cache style, open and close new run, re-open cached style.

        :param item: string to insert into new run

        This is for items like links that may be inside a run element with other text.

        Paraphrased in html:

            <run><b>some text<a href="">link</a>other text</b></run>

        Starts with an open run
            <run><b>some text

        Then hits the link.

            <run><b>some text  # this is where we are
            <run><b>some text</b></run>  # close this open run
            <run><a href="">link</a></run>  # add link as a new run
            <run><b>  # open a new run with the same style as the aborted first run
        """
        open_style = self._open_run.html_style
        self._open_runs.append(Run([], item))
        self._open_runs.append(Run(open_style))
