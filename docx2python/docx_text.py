"""Extract text from docx content files.

:author: Shay Hill
:created: 6/6/2019

Content in the extracted docx is found in the ``word`` folder:
    ``word/document.html``
    ``word/header1.html``
    ``word/footer1.html``
"""

from __future__ import annotations

import copy
from contextlib import suppress
from typing import TYPE_CHECKING, List, Literal, Sequence, cast

from docx2python.attribute_register import Tags, get_prefixed_tag
from docx2python.bullets_and_numbering import BulletGenerator
from docx2python.depth_collector import DepthCollector, Par, get_par_strings
from docx2python.forms import get_checkBox_entry, get_ddList_entry
from docx2python.iterators import iter_at_depth
from docx2python.namespace import qn
from docx2python.text_runs import gather_Pr

if TYPE_CHECKING:
    from lxml.etree import _Element as EtreeElement  # type: ignore

    from docx2python.docx_reader import File

ParsTable = List[List[List[List[Par]]]]
TextTable = List[List[List[List[List[str]]]]]


def _get_elem_depth(tree: EtreeElement) -> Literal[1, 2, 3, 4] | None:
    """Return depth in a nested list, relative to paragraphs (depth 4).

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
    if get_prefixed_tag(tree) in {Tags.DOCUMENT, Tags.BODY}:
        return None

    def search_at_depth(tree_: Sequence[EtreeElement], _depth: int = 0) -> int | None:
        """Width-first recursive search for Tags.PARAGRAPH.

        :param tree_: a sequence of elements which may contain a paragraph
        :return: depth of the first paragraph found, or None if no paragraph found
        """
        if not tree_:
            return None
        if any(get_prefixed_tag(x) == Tags.PARAGRAPH for x in tree_):
            return max(4 - _depth, 1)
        grandchildren = [list(x) for x in tree_]
        return search_at_depth([x for y in grandchildren for x in y], _depth + 1)

    return cast(Literal[1, 2, 3, 4], search_at_depth([tree]))


def _get_text_below(file: File, root: EtreeElement) -> str:
    """Return a string of all text below an element.

    :param file: an internal file element (e.g., header, footer, document))
    :param root: the root element of the document
    :return: a string of all text in the document
    """
    content_beneath_root = [
        x for y in [get_file_text(file, z) for z in root] for x in y
    ]
    return flatten_text(content_beneath_root)


class TagRunner:
    """Record or stage text from one xml element."""

    def __init__(self, file: File) -> None:
        """Gather context information necessary to perform some methods."""
        self.file = file
        self.tables = DepthCollector(file)
        self.bullets = BulletGenerator(file.context.numId2Attrs)

    def open(self, tree: EtreeElement) -> bool:
        """Open an output string or list then add element text to it.

        `open` methods will reture True if the element is to be recursed into.
        """
        tree_depth = _get_elem_depth(tree)
        self.tables.set_caret(tree_depth, tree)

        # not all tags are in the attribute register
        try:
            tag_name = Tags(get_prefixed_tag(tree)).name
        except ValueError:
            return True

        # not all tags have an open method
        method_name = f"_open_{tag_name.lower()}"
        try:
            method = getattr(self, method_name)
        except AttributeError:
            return True
        return method(tree)

    def close(self, tree: EtreeElement):
        """Take care of any cleanup after extracting element text."""
        tree_depth = _get_elem_depth(tree)

        # not all tags are in the attribute register
        try:
            tag_name = Tags(get_prefixed_tag(tree)).name
        except ValueError:
            self.tables.set_caret(tree_depth)
            return

        # not all tags have an open method
        method_name = f"_close_{tag_name.lower()}"
        try:
            method = getattr(self, method_name)
        except AttributeError:
            self.tables.set_caret(tree_depth)
            return
        method(tree)
        self.tables.set_caret(tree_depth)

    def _open_paragraph(self, tree: EtreeElement) -> bool:
        """Open a paragraph."""
        par = self.tables.commence_paragraph(tree)
        bullet = self.bullets.get_bullet(tree)
        position = self.bullets.get_list_position(tree)
        self.tables.insert_text_as_new_run(bullet)
        par.list_position = position
        return True

    def _open_run(self, tree: EtreeElement) -> bool:
        """Open a run."""
        self.tables.commence_run(tree)
        return True

    def _open_comment_range_end(self, tree: EtreeElement) -> bool:
        """Close a comment range."""
        self.tables.end_comment_range(tree.attrib[qn(tree, "w:id")])
        return False

    def _open_comment_range_start(self, tree: EtreeElement) -> bool:
        """Open a comment range."""
        self.tables.start_comment_range(tree.attrib[qn(tree, "w:id")])
        return False

    def _open_text(self, tree: EtreeElement) -> bool:
        """Open a text. These do not all contain text."""
        text = tree.text or ""
        self.tables.add_text_into_open_run(text)
        return True

    def _open_text_math(self, tree: EtreeElement) -> bool:
        """Open a math text."""
        return self._open_text(tree)

    def _open_math(self, tree: EtreeElement) -> bool:
        """Open a math."""
        text = "".join(str(x) for x in tree.itertext())
        self.tables.insert_text_as_new_run(f"<latex>{text}</latex>")
        return False

    def _open_br(self, tree: EtreeElement) -> bool:
        """Open a break."""
        _ = tree
        self.tables.add_code_into_open_run("\n")
        return True

    def _open_sym(self, tree: EtreeElement) -> bool:
        """Open a symbol."""
        font = str(tree.attrib.get(qn(tree, "w:font")))
        char = str(tree.attrib.get(qn(tree, "w:char")))
        if char:
            self.tables.add_code_into_open_run(
                f"<span style=font-family:{font}>&#x0{char[1:]};</span>"
            )
        return True

    def _open_footnote(self, tree: EtreeElement) -> bool:
        """Open a footnote."""
        footnote_type = str(tree.attrib.get(qn(tree, "w:type"), "")).lower()
        if "separator" not in footnote_type:
            self.tables.queue_run_for_next_paragraph(
                f"footnote{tree.attrib[qn(tree, 'w:id')]})\t"
            )
        return True

    def _open_endnote(self, tree: EtreeElement) -> bool:
        """Open an endnote."""
        endnote_type = str(tree.attrib.get(qn(tree, "w:type"), "")).lower()
        if "separator" not in endnote_type:
            self.tables.queue_run_for_next_paragraph(
                f"endnote{tree.attrib[qn(tree, 'w:id')]})\t"
            )
        return True

    def _open_hyperlink(self, tree: EtreeElement) -> bool:
        """Open a hyperlink."""
        text = _get_text_below(self.file, tree)
        try:
            rId = tree.attrib[qn(tree, "r:id")]
            link = self.file.rels[rId]
            anchor = tree.attrib.get(qn(tree, "w:anchor"))
            if link and anchor:
                link = link + "#" + anchor
            self.tables.insert_text_as_new_run(f'<a href="{link}">{text}</a>')
        except KeyError:
            self.tables.insert_text_as_new_run(text)
        return False

    def _open_form_checkbox(self, tree: EtreeElement) -> bool:
        """Open a form checkbox."""
        self.tables.insert_text_as_new_run(get_checkBox_entry(tree))
        return True

    def _open_form_ddlist(self, tree: EtreeElement) -> bool:
        """Open a form dropdown list."""
        self.tables.insert_text_as_new_run(get_ddList_entry(tree))
        return True

    def _open_footnote_reference(self, tree: EtreeElement) -> bool:
        """Open a footnote reference."""
        self.tables.insert_text_as_new_run(
            f"----footnote{tree.attrib[qn(tree, 'w:id')]}----"
        )
        return True

    def _open_endnote_reference(self, tree: EtreeElement) -> bool:
        """Open an endnote reference."""
        self.tables.insert_text_as_new_run(
            f"----endnote{tree.attrib[qn(tree, 'w:id')]}----"
        )
        return True

    def _open_image(self, tree: EtreeElement) -> bool:
        """Open an image."""
        with suppress(KeyError):
            rId = tree.attrib[qn(tree, "r:embed")]
            image = self.file.rels[rId]
            self.tables.insert_text_as_new_run(f"----{image}----")
        return True

    def _open_image_alt(self, tree: EtreeElement) -> bool:
        """Open an image alt."""
        with suppress(KeyError):
            description = tree.attrib["descr"]
            self.tables.insert_text_as_new_run(f"----Image alt text---->{description}<")
        return True

    def _open_imagedata(self, tree: EtreeElement) -> bool:
        """Open an image data."""
        with suppress(KeyError):
            rId = tree.attrib[qn(tree, "r:id")]
            image = self.file.rels[rId]
            self.tables.insert_text_as_new_run(f"----{image}----")
        return True

    def _open_tab(self, tree: EtreeElement) -> bool:
        """Open a tab."""
        _ = tree
        self.tables.insert_text_as_new_run("\t")
        return True

    def _close_paragraph(self, tree: EtreeElement):
        """Close a paragraph."""
        _ = tree
        self.tables.conclude_paragraph()

    def _close_run(self, tree: EtreeElement):
        """Close a run."""
        _ = tree
        self.tables.conclude_run()

    def _close_table_cell(self, tree: EtreeElement):
        """Close a table cell.

        Word treats vertically and horizontally merged cells differently.

        If the table cell is part of a vertically merged cell, it will be a Par
        instance with no text at this point. In this case, copy the Par from the
        above cell.

        If the table cell is part of a horizontally merged cell, it will not exist at
        this point. If duplicate_merged_cells is True, copy the cell to the left. If
        False, insert an empty cell.
        """
        do_merge = self.file.context.duplicate_merged_cells
        pr = gather_Pr(tree)
        tree_depth: Literal[3] = 3  # table cell
        this_tbl = self.tables.tree[-1]
        this_tr = this_tbl[-1]

        # vertical merge. copy cell above. These will already exist as Par instances
        # with no text.
        if do_merge and pr.get("vMerge", "Not None") is None and len(this_tbl) > 1:
            self.tables.set_caret(tree_depth)
            prev_tr = this_tbl[-2]
            tc_idx = len(this_tr) - 1
            this_tr[-1] = copy.deepcopy(prev_tr[tc_idx])

        # horizontal merge. copy cell to the left. These will not exist yet. If
        # self.file.context.duplicate_merged_cells is False, insert an empty cell.
        # Else insert a copy of the cell to the left.
        grid_span = pr.get("gridSpan") or 1
        for _ in range(int(grid_span) - 1):
            self.tables.set_caret(tree_depth)
            if do_merge:
                this_tr.append(copy.deepcopy(this_tr[-1]))
            else:
                this_tr.append([Par.new_empty_par(None)])


def new_depth_collector(file: File, root: EtreeElement | None = None) -> DepthCollector:
    """Populate a DepthCollector instance with text from a docx file.

    Xml as a string to a list of cell strings.

    :param file: File instance from which text will be extracted.
    :param root: Optionally extract content from a single element.
        If None, root_element of file will be used.
    :return: A 5-deep nested list of strings.

    Sorts the text into the DepthCollector instance, five-levels deep

    ``[table][row][cell][paragraph][run]`` is a string

    Joins the runs before returning, so return list will be

    ``[table][row][cell][paragraph]`` is a string

    If you'd like to extend or edit this package, the TagRunner class is probably
    where you want to do it. Nothing tricky here except keeping track of the text
    formatting.
    """
    root = root if root is not None else file.root_element
    tag_runner = TagRunner(file)

    def branches(tree: EtreeElement) -> None:
        """Recursively iterate over tree. Add text when found.

        :param tree: An Element from an xml file (etree)
        :effect: Adds text cells to outer variable `tables`.
        """
        recurse_into_tree = tag_runner.open(tree)

        if recurse_into_tree:
            for branch in tree:
                branches(branch)

        tag_runner.close(tree)

    branches(root)

    if tag_runner.tables.queued_runs:
        _ = tag_runner.tables.commence_paragraph()
    tag_runner.tables.conclude_paragraph()

    return tag_runner.tables


def get_file_content(file: File, root: EtreeElement | None = None) -> ParsTable:
    """Extract file content as a nested list of Par instances.

    :param file: File instance from which text will be extracted.
    :param root: Optionally extract content from a single element.
        If None, root_element of file will be used.
    :return: A nested list of Par instances [[[Par]]]

    ``[table][row][cell][par]`` is a Par instances
    """
    tables = new_depth_collector(file, root)
    return tables.tree


def get_file_text(file: File, root: EtreeElement | None = None) -> TextTable:
    """Extract file content as a nested list of strings.

    :param file: File instance from which text will be extracted.
    :param root: Optionally extract content from a single element.
        If None, root_element of file will be used.
    :return: A 5-deep nested list of strings.

    ``[table][row][cell][paragraph][run]`` is a string
    """
    return get_par_strings(get_file_content(file, root))


def flatten_text(text: TextTable) -> str:
    """Flatten a list of strings into a single string.

    :param text: A 5-deep nested list of strings.
    :return: A string.
    """
    pars = ["".join(x) for x in iter_at_depth(text, 4)]
    return "\n\n".join(pars)
