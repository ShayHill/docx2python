""" The tags and attributes docx2python knows how to handle.

:author: Shay Hill
:created: 3/18/2021

A lot of the information in a docx file isn't text or text attributes. Docx files
record spelling errors, revision history, etc. Docx2Python will ignore (by design)
much of this.
"""
from enum import Enum
from typing import Callable, Iterator, NamedTuple, Optional

from lxml.etree import _Element as EtreeElement  # type: ignore

from .namespace import qn


class HtmlFormatter(NamedTuple):
    """
    The information needed to group and format html tags.

    If a text run has multiple span attributes, Docx2Python does not open multiple
    span elements.

    ``<span style="font-size:12"><span style="font-weight:bold"> ...``

    Instead, these elements are first grouped by self.container, then by
    self.property, then printed all together.

    ``<span style="font-size:12;font-weight:bold">``

    This makes a more-readable text extraction, but it does involve passing these
    HtmlFormatter instances around A LOT.

    Formatting in the xml file will appear as child elements of an rPr or pPr element:

    ``<w:sz w:val="32"/>``

    self.formatter will be a function that takes the element tag name (here ``sz``)
    and element ``w:val`` attribute (here ``"32"``).
    """

    formatter: Callable[[str, str], str] = lambda tag, val: tag
    container: Optional[str] = None  # e.g., 'span'
    property_: Optional[str] = None  # e.g., 'style'


# An HtmlFormatter instance for every xml format Docx2Python recognizes.
# This mapping can be extended from outside by
#
#     import docx2python
#     docx2python.attribute_register.xml2html_formatter[xml_format] =
#         docx2python.attribute_register.HtmlFormatter(args)
XML2HTML_FORMATTER = {
    "b": HtmlFormatter(),
    "i": HtmlFormatter(),
    "u": HtmlFormatter(),
    "strike": HtmlFormatter(lambda tag, val: "s"),
    "vertAlign": HtmlFormatter(lambda tag, val: val[:3]),  # subscript and superscript
    "smallCaps": HtmlFormatter(
        lambda tag, val: "font-variant:small-caps", "span", "style"
    ),
    "caps": HtmlFormatter(lambda tag, val: "text-transform:uppercase", "span", "style"),
    "highlight": HtmlFormatter(
        lambda tag, val: f"background-color:{val}", "span", "style"
    ),
    "sz": HtmlFormatter(lambda tag, val: f"font-size:{val}pt", "span", "style"),
    "color": HtmlFormatter(lambda tag, val: f"color:{val}", "span", "style"),
    "Heading1": HtmlFormatter(lambda tag, val: "h1"),
    "Heading2": HtmlFormatter(lambda tag, val: "h2"),
    "Heading3": HtmlFormatter(lambda tag, val: "h3"),
    "Heading4": HtmlFormatter(lambda tag, val: "h4"),
    "Heading5": HtmlFormatter(lambda tag, val: "h5"),
    "Heading6": HtmlFormatter(lambda tag, val: "h6"),
}


class Tags(str, Enum):
    """
    These are the tags that provoke some action in docx2python.
    """

    BODY = qn("w:body")
    BR = qn("w:br")
    DOCUMENT = qn("w:document")
    ENDNOTE = qn("w:endnote")
    ENDNOTE_REFERENCE = qn("w:endnoteReference")
    FOOTNOTE = qn("w:footnote")
    FOOTNOTE_REFERENCE = qn("w:footnoteReference")
    FORM_CHECKBOX = qn("w:checkBox")
    FORM_DDLIST = qn("w:ddList")  # drop-down form
    HYPERLINK = qn("w:hyperlink")
    IMAGE = qn("a:blip")
    IMAGE_ALT = qn("wp:docPr")
    IMAGEDATA = qn("v:imagedata")
    MATH = qn("m:oMath")
    PARAGRAPH = qn("w:p")
    PAR_PROPERTIES = qn("w:pPr")
    RUN = qn("w:r")
    RUN_PROPERTIES = qn("w:rPr")
    SYM = qn("w:sym")
    TAB = qn("w:tab")
    TABLE = qn("w:tbl")
    TABLE_CELL = qn("w:tc")
    TABLE_ROW = qn("w:tr")
    TEXT = qn("w:t")
    TEXT_MATH = qn("m:t")


# elem.attrib key for relationship ids. These can find the information they reference by
# ``file_instance.rels[elem.attrib[RELS_ID]]``
RELS_ID = qn("r:id")

_CONTENT_TAGS = set(Tags) - {Tags.RUN_PROPERTIES, Tags.PAR_PROPERTIES}


def has_content(tree: EtreeElement) -> Optional[str]:
    """
    Does the element have any descendent content elements?

    :param tree: xml element
    :return: first content tag found or None if no content tags are found

    This is to check for text in any skipped elements.

    Docx2Python ignores spell check, revision, and other elements. This function checks
    that no content (paragraphs, run, text, link, ...) is contained in children of any
    ignored elements.

    If no content is found, the element can be safely ignored going forward.
    """

    def iter_content(tree_: EtreeElement) -> Iterator[str]:
        """Yield all content elements in tree

        :param tree_: xml element
        :yield: child content elements
        :return: None
        """
        if tree_.tag in _CONTENT_TAGS:
            yield tree_.tag
        for branch in tree_:
            yield from iter_content(branch)

    return next(iter_content(tree), None)
