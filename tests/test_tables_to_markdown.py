"""Test converting tables to markdown.

This is more of an example that an actual test, because I've had multiple requests
for tables as markdown. The new features in docx2python v3 make this straightforward.

:author: Shay Hill
:created: 2024-07-14
"""

from __future__ import annotations

from conftest import RESOURCES

from docx2python import docx2python
from docx2python.depth_collector import Par
from docx2python.iterators import is_tbl, iter_at_depth, iter_tables


def _print_tc(cell: list[Par]) -> str:
    """Print a table cell as a string on one line."""
    ps = ["".join(p.run_strings).replace("\n", " ") for p in cell]
    return "\n\n".join(ps)


def _join_and_enclose_with_pipes(strings: list[str]) -> str:
    """Join strings with pipes and enclose with pipes."""
    return "|" + "|".join(strings) + "|"


def _print_text(tbl: list[list[list[Par]]]) -> str:
    """Text in this list [[[Par]]] is not a table. It's just text."""
    all_cells = iter_at_depth(tbl, 2)
    return "\n\n".join(_print_tc(tc) for tc in all_cells)


def _print_tbl(tbl: list[list[list[Par]]]) -> str:
    """Text in this list [[[Par]]] is a table."""
    rows_as_string_lists = [[_print_tc(tc) for tc in tr] for tr in tbl]
    rows_as_string_lists.insert(1, ["---"] * len(rows_as_string_lists[0]))
    rows_as_strings = [
        _join_and_enclose_with_pipes(row) for row in rows_as_string_lists
    ]
    return "\n".join(rows_as_strings)


EXPECT = """This document has paragraphs.

|This|Document|
|---|---|
|Also|Has|
|Tables||

There are paragraphs between tables. These are used to check the .lineage attribute of Par instances.

Here is another paragraph between the first and second tables.

|One  More  Table|
|---|
|One|
|More|
|Table|

"""


def test_tables_to_markdown():
    with docx2python(RESOURCES / "paragraphs_and_tables.docx") as extraction:
        tables = extraction.document_pars

    as_text: list[str] = []

    for possible_table in iter_tables(tables):
        if is_tbl(possible_table):
            as_text.append(_print_tbl(possible_table))
        else:
            as_text.append(_print_text(possible_table))

    assert "\n\n".join(as_text) == EXPECT
