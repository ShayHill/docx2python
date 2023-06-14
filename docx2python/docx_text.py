"""Extract text from docx content files.

:author: Shay Hill
:created: 6/6/2019

Content in the extracted docx is found in the ``word`` folder:
    ``word/document.html``
    ``word/header1.html``
    ``word/footer1.html``
"""
from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING, List, Sequence, cast

from lxml.etree import _Element as EtreeElement  # type: ignore

from .attribute_register import Tags
from .bullets_and_numbering import BulletGenerator
from .depth_collector import DepthCollector, Run
from .forms import get_checkBox_entry, get_ddList_entry
from .iterators import iter_at_depth
from .namespace import qn
from .text_runs import (
    gather_Pr,
    get_paragraph_formatting,
    get_pStyle,
    get_run_formatting,
)

if TYPE_CHECKING:
    from docx_reader import File

TablesList = List[List[List[List[str]]]]


def _get_elem_depth(tree: EtreeElement) -> int | None:
    """What depth is this element in a nested list, relative to paragraphs (depth 4)?

    :param tree: element in a docx content xml (header, footer, officeDocument, etc.)

    :return: 4 - recursion depth;
        None if no paragraphs are found or if descending into nest would cause a
        false start (e.g., Tags.DOCUMENT or Tags.BODY which often have A paragraph (but
        not the next paragraph) at one or two levels down.

    Typically, the docx is a table of tables::

        [  # entire document
            [  # table
                [  # table row
                    [  # table cell
                        [  # paragraph
                            "",  # run
                            "",  # run
                            "",  # run
                        ]
                    ]
                ]
            ]
        ]

    But this isn't always the case. Instead of looking explicitly for tables,
    table rows, and table cells, look inside elements for paragraphs to determine
    depth in the nested list.

    E.g., given a table row element with a paragraph two levels in, return 2.
    So, depth of element will be 4 - 2 = 3.

    document = depth 0
    table = depth 1
    table row = depth 2
    table cell = depth 3
    paragraph = depth 4
    below paragraph = depth 5

    There will only ever be one document list, so the min depth returned is 1
    """

    if tree.tag in {Tags.DOCUMENT, Tags.BODY}:
        return None

    def search_at_depth(tree_: Sequence[EtreeElement], _depth: int = 0) -> int | None:
        """Width-first recursive search for Tags.PARAGRAPH

        :param tree_: a sequence of elements which may contain a paragraph
        :return: depth of the first paragraph found, or None if no paragraph found
        """
        if not tree_:
            return None
        if any(x.tag == Tags.PARAGRAPH for x in tree_):
            return max(4 - _depth, 1)
        grandchildren = [list(x) for x in tree_]
        return search_at_depth([x for y in grandchildren for x in y], _depth + 1)

    return search_at_depth([tree])


def get_paragraphs(file: File, root: EtreeElement) -> list[str]:
    """Return a list of paragraphs from the document

    :param file: an internal file element (e.g., header, footer, document))
    :param root: the root element of the document
    :return: a list of paragraphs
    """
    all_paragraphs: list[str] = []
    for branch in root:
        all_paragraphs += list(iter_at_depth(get_text(file, branch), 5))
    return all_paragraphs


def merged_text_tree(file: File, root: EtreeElement) -> str:
    """Return a string of all text in the document

    :param file: an internal file element (e.g., header, footer, document))
    :param root: the root element of the document
    :return: a string of all text in the document
    """
    return "".join(get_paragraphs(file, root))


def get_text(file: File, root: EtreeElement | None = None) -> TablesList:
    """Xml as a string to a list of cell strings.

    :param file: File instance from which text will be extracted.
    :param root: Optionally extract content from a single element.
        If None, root_element of file will be used.
    :return: A 5-deep nested list of strings.

    Sorts the text into the DepthCollector instance, five-levels deep

    ``[table][row][cell][paragraph][run]`` is a string

    Joins the runs before returning, so return list will be

    ``[table][row][cell][paragraph]`` is a string

    If you'd like to extend or edit this package, this function is probably where you
    want to do it. Nothing tricky here except keeping track of the text formatting.
    """
    root = root if root is not None else file.root_element
    bullets = BulletGenerator(file.context.numId2numFmts)
    # numId2count = _new_list_counter()
    tables = DepthCollector(5)

    xml2html = file.context.xml2html_format

    def branches(tree: EtreeElement) -> None:
        """
        Recursively iterate over tree. Add text when found.

        :param tree: An Element from an xml file (etree)
        :effect: Adds text cells to outer variable `tables`.
        """
        do_descend = True

        tree_depth = _get_elem_depth(tree)
        tables.set_caret(tree_depth)

        # queue up tags before opening any paragraphs or runs
        if tree.tag == Tags.PARAGRAPH:
            par = tables.commence_paragraph(get_paragraph_formatting(tree, xml2html))
            if file.context.do_pStyle:
                par.runs.insert(0, Run([], get_pStyle(tree) or "None"))
            tables.insert_text_as_new_run(bullets.get_bullet(tree))

        elif tree.tag == Tags.RUN:
            tables.commence_run(get_run_formatting(tree, xml2html))

        elif tree.tag in {Tags.TEXT, Tags.TEXT_MATH}:
            # oddly enough, these don't all contain text
            text = tree.text if tree.text is not None else ""
            if xml2html:
                text = text.replace("&", "&amp;")
                text = text.replace("<", "&lt;")
                text = text.replace(">", "&gt;")
            tables.add_text_into_open_run(text)

        elif tree.tag == Tags.MATH:
            # read equations
            text = "".join(str(x) for x in tree.itertext())
            do_descend = False
            tables.insert_text_as_new_run(f"<latex>{text}</latex>")

        elif tree.tag == Tags.BR:
            tables.add_text_into_open_run("\n")

        elif tree.tag == Tags.SYM:
            font = str(tree.attrib.get(qn("w:font")))
            char = str(tree.attrib.get(qn("w:char")))
            if char:
                tables.add_text_into_open_run(
                    f"<span style=font-family:{font}>&#x0{char[1:]};</span>"
                )

        elif tree.tag == Tags.FOOTNOTE:
            footnote_type = str(tree.attrib.get(qn("w:type"), "")).lower()
            if "separator" not in footnote_type:
                tables.insert_text_as_new_run(
                    f"footnote{str(tree.attrib[qn('w:id')])})\t"
                )

        elif tree.tag == Tags.ENDNOTE:
            endnote_type = str(tree.attrib.get(qn("w:type"), "")).lower()
            if "separator" not in endnote_type:
                tables.insert_text_as_new_run(
                    f"endnote{str(tree.attrib[qn('w:id')])})\t"
                )

        elif tree.tag == Tags.HYPERLINK:
            # look for an href, ignore internal references (anchors)
            text = merged_text_tree(file, tree)
            do_descend = False
            try:
                rId = tree.attrib[qn("r:id")]
                link = file.rels[rId]
                tables.insert_text_as_new_run(f'<a href="{link}">{text}</a>')
            except KeyError:
                tables.insert_text_as_new_run(text)

        if tree.tag == Tags.FORM_CHECKBOX:
            tables.insert_text_as_new_run(get_checkBox_entry(tree))

        elif tree.tag == Tags.FORM_DDLIST:
            tables.insert_text_as_new_run(get_ddList_entry(tree))

        elif tree.tag == Tags.FOOTNOTE_REFERENCE:
            tables.insert_text_as_new_run(
                f"----footnote{str(tree.attrib[qn('w:id')])}----"
            )

        elif tree.tag == Tags.ENDNOTE_REFERENCE:
            tables.insert_text_as_new_run(
                f"----endnote{str(tree.attrib[qn('w:id')])}----"
            )

        elif tree.tag == Tags.IMAGE:
            with suppress(KeyError):
                rId = tree.attrib[qn("r:embed")]
                image = file.rels[rId]
                tables.insert_text_as_new_run(f"----{image}----")

        elif tree.tag == Tags.IMAGE_ALT:
            with suppress(KeyError):
                description = tree.attrib["descr"]
                tables.insert_text_as_new_run(f"----Image alt text---->{description}<")

        elif tree.tag == Tags.IMAGEDATA:
            with suppress(KeyError):
                rId = tree.attrib[qn("r:id")]
                image = file.rels[rId]
                tables.insert_text_as_new_run(f"----{image}----")

        elif tree.tag == Tags.TAB:
            tables.insert_text_as_new_run("\t")

        if do_descend:
            for branch in tree:
                branches(branch)

        if tree.tag == Tags.PARAGRAPH:
            tables.conclude_paragraph()

        elif tree.tag == Tags.TABLE_CELL and file.context.duplicate_merged_cells:
            pr = gather_Pr(tree)

            if pr.get("vMerge", "Not None") is None:
                tables.set_caret(tree_depth)
                cell_idx = len(tables.caret) - 1
                assert isinstance(tree_depth, int)
                prev_row_cell = tables.view_branch((tree_depth - 2, -2, cell_idx))
                tables.caret[-1] = prev_row_cell

            grid_span = pr.get("gridSpan", 1)
            assert grid_span is not None
            for _ in range(int(grid_span) - 1):
                tables.set_caret(tree_depth)
                tables.caret.append(tables.caret[-1])

        elif tree.tag == Tags.RUN:
            tables.conclude_run()

        tables.set_caret(tree_depth)

    branches(root)

    if tables.orphan_runs:
        _ = tables.commence_paragraph()
    if tables.open_pars:
        tables.conclude_paragraph()

    return cast(TablesList, tables.tree)
