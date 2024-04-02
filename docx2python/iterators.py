"""Iterate over extracted docx content.

:author: Shay Hill
:created: 6/28/2019

This package extracts docx text as::

    [  # tables
        [  # table
            [  # row
                [  # cell
                    ""  # paragraph
                ]
            ]
        ]
    ]

These functions help manipulate that deep nest without deep indentation.

"""

from __future__ import annotations

from typing import Any, Iterable, Iterator, List, NamedTuple, Sequence, Union, cast

TablesList = List[List[List[List[Any]]]]

# A collapsed TablesList
CollTL = List[Union[str, "CollTL"]]


def join_leaves(
    joint: str, str_tree: CollTL, to_depth: int, _depth: int = 0
) -> CollTL | str:
    """Join the leaves of a nested list of strings at a certain depth.

    :param joint: string to join leaves
    :param str_tree: a nested list of strings with all strings at the same depth
    :param to_depth: depth at which to join strings. This has to be explicit, because
        all strings are at the same depth, but this depth cannot necessarily be
        inferred, because the tree may have no leaves at all. The `to_depth` argument
        is the depth the tree will be collapsed TO. So, if `to_depth` is 0, the tree
        will be collapsed to a single string. If `to_depth` is 1, the tree will be
        collapsed to a list of strings. If `to_depth` is 2, the tree will be
        collapsed to a list of lists of strings, etc.

        You can only collapse one depth, and that depth must be explicated. Remember
        that in a tree, the depth is the shortest path from the root to a leaf. So
        the top node is at depth 0, its children are at depth 1, their children are
        at depth 2, etc.
    :param _depth: for recursion. Do not enter this argument.

    The most common use in this project will be to collapse nested lists of runs into
    nested lists of paragraphs.

    runs = [
        [
            [
                [
                    [
                        "run1", "run2"
                    ],
                    [
                        "run3", "run4"
                    ]
                ]
            ]
        ]
    ]

    `_join_leaves("", runs, 3)` =>

    [
        [
            [
                [
                    "run1run2",
                    "run3run4"
                ]
            ]
        [
    ]
    """
    if _depth == to_depth:
        return joint.join(cast(List[str], str_tree))
    return [join_leaves(joint, cast(CollTL, b), to_depth, _depth + 1) for b in str_tree]


class IndexedItem(NamedTuple):
    """The address (indices in a nested list) of an item and the item itself."""

    # TODO: rename index for docx 3.0
    index: tuple[int, ...]  # type: ignore
    value: Any


def enum_at_depth(nested: Sequence[Any], depth: int) -> Iterator[IndexedItem]:
    """Enumerate over a nested sequence at depth.

    :param nested: a (nested) sequence
    :param depth: depth of iteration

        * ``1`` => ``((i,), nested[i])``
        * ``2`` => ``((i, j), nested[:][j])``
        * ``3`` => ``((i, j, k), nested[:][:][k])``
        * ...

    :return: tuples (tuple "address", item)
    :raise ValueError: if depth is less than 1

    >>> sequence = [
    ...     [[["a", "b"], ["c"]], [["d", "e"]]],
    ...     [[["f"], ["g", "h"]]]
    ... ]

    >>> for x in enum_at_depth(sequence, 1): print(x)
    IndexedItem(index=(0,), value=[[['a', 'b'], ['c']], [['d', 'e']]])
    IndexedItem(index=(1,), value=[[['f'], ['g', 'h']]])

    >>> for x in enum_at_depth(sequence, 2): print(x)
    IndexedItem(index=(0, 0), value=[['a', 'b'], ['c']])
    IndexedItem(index=(0, 1), value=[['d', 'e']])
    IndexedItem(index=(1, 0), value=[['f'], ['g', 'h']])

    >>> for x in enum_at_depth(sequence, 3): print(x)
    IndexedItem(index=(0, 0, 0), value=['a', 'b'])
    IndexedItem(index=(0, 0, 1), value=['c'])
    IndexedItem(index=(0, 1, 0), value=['d', 'e'])
    IndexedItem(index=(1, 0, 0), value=['f'])
    IndexedItem(index=(1, 0, 1), value=['g', 'h'])

    >>> for x in enum_at_depth(sequence, 4): print(x)
    IndexedItem(index=(0, 0, 0, 0), value='a')
    IndexedItem(index=(0, 0, 0, 1), value='b')
    IndexedItem(index=(0, 0, 1, 0), value='c')
    IndexedItem(index=(0, 1, 0, 0), value='d')
    IndexedItem(index=(0, 1, 0, 1), value='e')
    IndexedItem(index=(1, 0, 0, 0), value='f')
    IndexedItem(index=(1, 0, 1, 0), value='g')
    IndexedItem(index=(1, 0, 1, 1), value='h')

    >>> list(enum_at_depth(sequence, 5))
    Traceback (most recent call last):
    ...
    TypeError: will not iterate over sequence item

    This error is analogous to the ``TypeError: 'int' object is not iterable`` you
    would see if attempting to enumerate over a non-iterable. In this case,
    you've attempted to enumerate over an item that *may* be iterable, but is not of
    the same type as the ``nested`` sequence argument. This type checking is how we
    can safely descend into a nested list of strings.
    """
    if depth < 1:
        raise ValueError("depth argument must be >= 1")
    argument_type = type(nested)

    def enumerate_next_depth(enumd: Iterable[IndexedItem]) -> Iterator[IndexedItem]:
        """
        Descend into a nested sequence, enumerating along descent

        :param enumd: tuples (tuple of indices, sequences)
        :return: updated index tuples with items from each sequence.
        :raises TypeError: if the sequence is not of the same type as the ``nested``.
            This will happen if you try to iterate into a string in a list of
            strings.
        """
        for index_tuple, sequence in enumd:
            if not isinstance(sequence, argument_type):
                raise TypeError("will not iterate over sequence item")
            for i, item in enumerate(sequence):
                yield IndexedItem((*index_tuple, i), item)

    depth_n: Iterator[IndexedItem]
    depth_n = (IndexedItem((i,), x) for i, x in enumerate(nested))
    for _ in range(1, depth):
        depth_n = enumerate_next_depth(depth_n)
    return (x for x in depth_n)


def iter_at_depth(nested: Sequence[Any], depth: int) -> Iterator[Any]:
    """
    Iterate over a nested sequence at depth.

    :param nested: a (nested) sequence
    :param depth: depth of iteration

        * ``1`` => ``nested[i]``
        * ``2`` => ``nested[:][j]``
        * ``3`` => ``nested[:][:][k]``
        * ...

    :return: sub-sequences or items in nested

    >>> sequence = [
    ...     [[["a", "b"], ["c"]], [["d", "e"]]],
    ...     [[["f"], ["g", "h"]]]
    ... ]

    >>> for x in iter_at_depth(sequence, 1): print(x)
    [[['a', 'b'], ['c']], [['d', 'e']]]
    [[['f'], ['g', 'h']]]

    >>> for x in iter_at_depth(sequence, 2): print(x)
    [['a', 'b'], ['c']]
    [['d', 'e']]
    [['f'], ['g', 'h']]

    >>> for x in iter_at_depth(sequence, 3): print(x)
    ['a', 'b']
    ['c']
    ['d', 'e']
    ['f']
    ['g', 'h']

    >>> list(iter_at_depth(sequence, 4))
    ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    """
    return (value for _, value in enum_at_depth(nested, depth))


def iter_tables(tables: TablesList) -> Iterator[list[list[list[Any]]]]:
    """
    Iterate over ``tables[i]``

    Analog of iter_at_depth(tables, 1)

    :param tables: ``[[[["string"]]]]``
    :return: ``tables[0], tables[1], ... tables[i]``
    """
    return iter_at_depth(tables, 1)


def iter_rows(tables: TablesList) -> Iterator[list[list[Any]]]:
    """
    Iterate over ``tables[:][j]``

    Analog of iter_at_depth(tables, 2)

    :param tables: ``[[[["string"]]]]``
    :return: ``tables[0][0], tables[0][1], ... tables[i][j]``
    """
    return iter_at_depth(tables, 2)


def iter_cells(tables: TablesList) -> Iterator[list[Any]]:
    """
    Iterate over ``tables[:][:][k]``

    Analog of iter_at_depth(tables, 3)

    :param tables: ``[[[["string"]]]]``
    :return: ``tables[0][0][0], tables[0][0][1], ... tables[i][j][k]``
    """
    return iter_at_depth(tables, 3)


def iter_paragraphs(tables: TablesList) -> Iterator[str]:
    """
    Iterate over ``tables[:][:][:][l]``

    Analog of iter_at_depth(tables, 4)

    :param tables: ``[[[["string"]]]]``
    :return: ``tables[0][0][0][0], tables[0][0][0][1], ... tables[i][j][k][l]``
    """
    return iter_at_depth(tables, 4)


def enum_tables(tables: TablesList) -> Iterator[IndexedItem]:
    """
    Enumerate over ``tables[i]``

    Analog of enum_at_depth(tables, 1)

    :param tables: ``[[[["string"]]]]``
    :return:
        ``((0, ), tables[0]) ... , ((i, ), tables[i])``
    """
    return enum_at_depth(tables, 1)


def enum_rows(tables: TablesList) -> Iterator[IndexedItem]:
    """
    Enumerate over ``tables[:][j]``

    Analog of enum_at_depth(tables, 2)

    :param tables: ``[[[["string"]]]]``
    :return:
        ``((0, 0), tables[0][0]) ... , ((i, j), tables[i][j])``
    """
    return enum_at_depth(tables, 2)


def enum_cells(tables: TablesList) -> Iterator[IndexedItem]:
    """
    Enumerate over ``tables[:][:][k]``

    Analog of enum_at_depth(tables, 3)

    :param tables: ``[[[["string"]]]]``
    :return:
        ``((0, 0, 0), tables[0][0][0]) ... , ((i, j, k), tables[i][j][k])``
    """
    return enum_at_depth(tables, 3)


def enum_paragraphs(tables: TablesList) -> Iterator[IndexedItem]:
    """
    Enumerate over ``tables[:][:][:][l]``

    Analog of enum_at_depth(tables, 4)

    :param tables: ``[[[["string"]]]]``
    :return:
        ``((0, 0, 0, 0), tables[0][0][0][0]) ... , ((i, j, k, l), tables[i][j][k][l])``
    """
    return enum_at_depth(tables, 4)


def get_text(tables: TablesList) -> str:
    r"""
    Short cut to pull text from any subset of extracted content.

    :param tables: ``[[[["string"]]]]``
    :return: "string" (all paragraphs in tables joined with '\n\n'
    """
    return "\n\n".join(iter_at_depth(tables, 4))


def get_html_map(tables: TablesList) -> str:
    """
    Create a visual map in html format.

    :param tables: ``[[[["string"]]]]``
    :return: html to show all strings with index tuples

    Create an html string that can be rendered in a browser to show the relative
    location and index tuple of every paragraph in the document.

    * Each table will be a grid of cell boxes, outlined in black. * Each paragraph
    will be prepended with an index tuple. (e.g., ``[[[['text']]]]`` will appear as
    ``(0, 0, 0, 0) text``.
    """
    # prepend index tuple to each paragraph
    tables_4deep = cast(List[List[List[List[str]]]], tables)
    for (i, j, k, m), paragraph in enum_at_depth(tables, 4):
        tables_4deep[i][j][k][m] = " ".join([str((i, j, k, m)), paragraph])

    # wrap each paragraph in <pre> tags
    tables_3deep = cast(List[List[List[str]]], tables_4deep)
    for (i, j, k), cell in enum_at_depth(tables_4deep, 3):
        cell_strs = (str(x) for x in cell)
        tables_3deep[i][j][k] = "".join([f"<pre>{x}</pre>" for x in cell_strs])

    # wrap each cell in <td> tags
    tables_2deep = cast(List[List[str]], tables_3deep)
    for (i, j), row in enum_at_depth(tables_3deep, 2):
        tables_2deep[i][j] = "".join([f"<td>{x}</td>" for x in row])

    # wrap each row in <tr> tags
    tables_1deep = cast(List[str], tables_2deep)
    for (i,), table in enum_at_depth(tables_2deep, 1):
        tables_1deep[i] = "".join(f"<tr>{x}</tr>" for x in table)

    # wrap each table in <table> tags
    tables_ = "".join([f'<table border="1">{x}</table>' for x in tables_1deep])

    return "<html><body>" + tables_ + "</body></html>"
