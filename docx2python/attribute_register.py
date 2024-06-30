"""The tags and attributes docx2python knows how to handle.

:author: Shay Hill
:created: 3/18/2021

A lot of the information in a docx file isn't text or text attributes. Docx files
record spelling errors, revision history, etc. Docx2Python will ignore (by design)
much of this.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Callable, Iterator, NamedTuple

from lxml import etree

if TYPE_CHECKING:
    from lxml.etree import _Element as EtreeElement  # type: ignore


def get_localname(elem: EtreeElement) -> str:
    """Return the localname of the element tag.

    :param elem: xml element
    :return: localname of element tag

    Where `elem.tag` would return something like
    `{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p`

    ...

    return `p`.
    """
    qname = etree.QName(elem.tag)
    return qname.localname


def get_prefixed_tag(elem: EtreeElement) -> str:
    """Return the element tag with a prefix instead of a full uri.

    :param elem: xml element
    :return: prefixed tag of element

    Where `elem.tag` would return something like
    `{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p`.

    ...

    return `w:p`.

    `w:p` is the tag as it appears inside the element within the xml. Lxml expands
    the tag to `{http:...}p`. This function returns the tag as it appears in the xml.

    Purpose:

    The full tag name contains a full namespace uri for an element. Docx2Python
    handles many elements identically even where they have different namespace uris.
    For example:

    * `{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p` and
    * `{http://purl.oclc.org/ooxml/wordprocessingml/main}p`

    are both paragraphs. The first with the default Word namespace and the second
    with the what MS refers to as the "strict open xml namespace". Docx2Python can
    will recognize both as paragraphs and treat them identically. To that end,
    Docx2Python identifies such paragraphs by their matching "prefixed tag" names
    (`w:p`), not their full tag names.
    """
    return f"{elem.prefix}:{get_localname(elem)}"


def _just_return_tag(tag: str, val: str) -> str:
    """
    A formatter that just returns the tag name.

    :param tag: xml tag name
    :param val: xml attribute value
    :return: tag name
    """
    del val
    return tag


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

    formatter: Callable[[str, str], str] = _just_return_tag
    container: str | None = None  # e.g., 'span'
    property_: str | None = None  # e.g., 'style'


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

    BODY = "w:body"
    BR = "w:br"
    COMMENT_RANGE_END = "w:commentRangeEnd"
    COMMENT_RANGE_START = "w:commentRangeStart"
    DOCUMENT = "w:document"
    ENDNOTE = "w:endnote"
    ENDNOTE_REFERENCE = "w:endnoteReference"
    FOOTNOTE = "w:footnote"
    FOOTNOTE_REFERENCE = "w:footnoteReference"
    FORM_CHECKBOX = "w:checkBox"
    FORM_DDLIST = "w:ddList"  # drop-down form
    HYPERLINK = "w:hyperlink"
    IMAGE = "a:blip"
    IMAGEDATA = "v:imagedata"
    IMAGE_ALT = "wp:docPr"
    MATH = "m:oMath"
    PARAGRAPH = "w:p"
    PAR_PROPERTIES = "w:pPr"
    RUN = "w:r"
    RUN_PROPERTIES = "w:rPr"
    SYM = "w:sym"
    TAB = "w:tab"
    TABLE = "w:tbl"
    TABLE_CELL = "w:tc"
    TABLE_ROW = "w:tr"
    TEXT = "w:t"
    TEXT_MATH = "m:t"


_CONTENT_TAGS = set(Tags) - {Tags.RUN_PROPERTIES, Tags.PAR_PROPERTIES}


def _is_content(elem: EtreeElement) -> bool:
    """Is the element a content element?

    sdf   :param elem: xml element
    :return: True if the element is a content element

    Docx2Python ignores spell check, revision, and other elements. This function
    checks that the element is a content element.

    If the element is a content element, it will be processed further.
    """
    return get_prefixed_tag(elem) in _CONTENT_TAGS


def has_content(tree: EtreeElement) -> str | None:
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
        if _is_content(tree_):
            yield tree_.tag
        for branch in tree_:
            yield from iter_content(branch)

    return next(iter_content(tree), None)
