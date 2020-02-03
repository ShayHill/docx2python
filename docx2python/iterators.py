#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
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

from typing import Any, Iterable, Iterator, List, NamedTuple, Sequence, Tuple

TablesList = List[List[List[List[Any]]]]

IndexedItem = NamedTuple("IndexedItem", [("index", Tuple[int, ...]), ("value", Any)])


def enum_at_depth(nested: Sequence[Any], depth: int) -> Iterator[IndexedItem]:
    """
    Enumerate over a nested sequence at depth.

    :param nested: a (nested) sequence
    :param depth: depth of iteration

        * ``1`` => ``((i,), nested[i])``
        * ``2`` => ``((i, j), nested[:][j])``
        * ``3`` => ``((i, j, k), nested[:][:][k])``
        * ...

    :returns: tuples (tuple "address", item)

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
        """
        for index_tuple, sequence in enumd:
            if type(sequence) != argument_type:
                raise TypeError("will not iterate over sequence item")
            for i, item in enumerate(sequence):
                yield IndexedItem(index_tuple + (i,), item)

    depth_n = (IndexedItem((i,), x) for i, x in enumerate(nested))
    for depth in range(1, depth):
        depth_n = enumerate_next_depth(depth_n)
    return depth_n


def iter_at_depth(nested: Sequence[Any], depth: int) -> Iterator[Any]:
    """
    Iterate over a nested sequence at depth.

    :param nested: a (nested) sequence
    :param depth: depth of iteration

        * ``1`` => ``nested[i]``
        * ``2`` => ``nested[:][j]``
        * ``3`` => ``nested[:][:][k]``
        * ...

    :returns: sub-sequences or items in nested

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
    return (value for index, value in enum_at_depth(nested, depth))


def iter_tables(tables: TablesList) -> Iterator[List[List[List[Any]]]]:
    """
    Iterate over ``tables[i]``

    Analog of iter_at_depth(tables, 1)

    :param tables: ``[[[["string"]]]]``
    :return: ``tables[0], tables[1], ... tables[i]``
    """
    return iter_at_depth(tables, 1)


def iter_rows(tables: TablesList) -> Iterator[List[List[Any]]]:
    """
    Iterate over ``tables[:][j]``

    Analog of iter_at_depth(tables, 2)

    :param tables: ``[[[["string"]]]]``
    :return: ``tables[0][0], tables[0][1], ... tables[i][j]``
    """
    return iter_at_depth(tables, 2)


def iter_cells(tables: TablesList) -> Iterator[List[Any]]:
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
    """
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
    tables = tables.copy()

    # prepend index tuple to each paragraph
    for (i, j, k, l), paragraph in enum_at_depth(tables, 4):
        tables[i][j][k][l] = " ".join([str((i, j, k, l)), paragraph])

    # wrap each paragraph in <pre> tags
    for (i, j, k), cell in enum_at_depth(tables, 3):
        tables[i][j][k] = "".join(["<pre>{}</pre>".format(x) for x in cell])

    # wrap each cell in <td> tags
    for (i, j), row in enum_at_depth(tables, 2):
        tables[i][j] = "".join(["<td>{}</td>".format(x) for x in row])

    # wrap each row in <tr> tags
    for (i,), table in enum_at_depth(tables, 1):
        tables[i] = "".join("<tr>{}</tr>".format(x) for x in table)

    # wrap each table in <table> tags
    tables = "".join(['<table border="1">{}</table>'.format(x) for x in tables])

    return "<html><body>" + tables + "</body></html>"
