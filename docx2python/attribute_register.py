"""The tags and attributes docx2python knows how to handle.

:author: Shay Hill
:created: 3/18/2021

A lot of the information in a docx file isn't text or text attributes. Docx files
record spelling errors, revision history, etc. Docx2Python will ignore (by design)
much of this.

This module defines which xml tags are implemented and how they are transformed into
html tags.
"""

from __future__ import annotations

import uuid
import warnings
from enum import Enum
from typing import TYPE_CHECKING, Callable, Iterator, NamedTuple

from lxml import etree

if TYPE_CHECKING:
    from lxml.etree import _Element as EtreeElement  # type: ignore

# ===============================================================================
# Examine and reformat html tags
# ===============================================================================


def get_localname(elem: EtreeElement) -> str:
    """Return the localname of the element tag.

    :param elem: xml element
    :return: localname of element tag

    Where `elem.tag` would return something like
    `{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p`

    ...

    return `p`.

    ---

    Some converted Word documents have bad tags due to a conversion in the error.
    These will raise a ValueError when passed to `etree.QName`. If a file with tags
    like this is opened in Word and saved again, any element with a bad tag will be
    stripped. Docx2Python does the same thing.  For any tag that raises a ValueError
    in `etree.QName`, this function will return a random string, and docx2python will
    silently ignore the element with the bad tag.
    """
    try:
        qname = etree.QName(elem.tag)
    except ValueError:
        warnings.warn(f"skipping invalid tag name '{elem.tag}'", stacklevel=2)
        return f"FAILED-{uuid.uuid4()}"
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


# ===============================================================================
# Format xml tags as html tags
#
# Instances of the HtmlFormatter class define hot to format xml tags as html tags.
# ===============================================================================


def _format_just_return_tag(tag: str, val: str) -> str:
    """Echo the name tag argument.

    :param tag: xml tag name
    :param val: xml attribute value
    :return: tag name

    This is a formatter function for HtmlFormatter instances.
    """
    del val
    return tag


class HtmlFormatter(NamedTuple):
    """The information needed to group and format html tags.

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

    formatter: Callable[[str, str], str] = _format_just_return_tag
    container: str | None = None  # e.g., 'span'
    property_: str | None = None  # e.g., 'style'


def _format_strike(tag: str, val: str) -> str:
    """Return 's' for the strike tag.

    :param tag: xml tag name (strike)
    :param val: xml attribute value ("")
    :return: "s"

    This is a formatter function for HtmlFormatter instances.
    """
    del val
    del tag
    return "s"


def _format_vertAlign(tag: str, val: str) -> str:
    """Return the first three characters of the vertAlign value.

    :param tag: xml tag name (vertAlign)
    :param val: xml attribute value (superscript or subscript)
    :return: first three characters of val (sub or sup)

    This is a formatter function for HtmlFormatter instances.
    """
    del tag
    return val[:3]


def _format_smallCaps(tag: str, val: str) -> str:
    """Return 'font-variant:small-caps'.

    :param tag: xml tag name (smallCaps)
    :param val: xml attribute value ("")
    :return: "font-variant:small-caps"

    This is a formatter function for HtmlFormatter instances.
    """
    del val
    del tag
    return "font-variant:small-caps"


def _format_caps(tag: str, val: str) -> str:
    """Return 'text-transform:uppercase'.

    :param tag: xml tag name (caps)
    :param val: xml attribute value ("")
    :return: "text-transform:uppercase"

    This is a formatter function for HtmlFormatter instances.
    """
    del val
    del tag
    return "text-transform:uppercase"


def _format_highlight(tag: str, val: str) -> str:
    """Return 'background-color:val'.

    :param tag: xml tag name (highlight)
    :param val: xml attribute value (color)
    :return: "background-color:val"

    This is a formatter function for HtmlFormatter instances.
    """
    del tag
    return f"background-color:{val}"


def _format_sz(tag: str, val: str) -> str:
    """Return 'font-size:{val}pt'.

    :param tag: xml tag name (sz)
    :param val: xml attribute value (font size in points)
    :return: "font-size:{val}pt"

    This is a formatter function for HtmlFormatter instances.
    """
    del tag
    return f"font-size:{val}pt"


def _format_color(tag: str, val: str) -> str:
    """Return 'color:val'.

    :param tag: xml tag name (color)
    :param val: xml attribute value (color)
    :return: "color:val"

    This is a formatter function for HtmlFormatter instances.
    """
    del tag
    return f"color:{val}"


def _format_heading(tag: str, val: str) -> str:
    """Return 'h{val}'.

    :param tag: xml tag name (Heading1, Heading2, ...)
    :param val: xml attribute value ("")
    :return: "h{val}"

    This is a formatter function for HtmlFormatter instances.
    """
    del val
    return f"h{tag[-1]}"


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
    "strike": HtmlFormatter(_format_strike),
    "vertAlign": HtmlFormatter(_format_vertAlign),  # subscript and superscript
    "smallCaps": HtmlFormatter(_format_smallCaps, "span", "style"),
    "caps": HtmlFormatter(_format_caps, "span", "style"),
    "highlight": HtmlFormatter(_format_highlight, "span", "style"),
    "sz": HtmlFormatter(_format_sz, "span", "style"),
    "color": HtmlFormatter(_format_color, "span", "style"),
    "Heading1": HtmlFormatter(_format_heading),
    "Heading2": HtmlFormatter(_format_heading),
    "Heading3": HtmlFormatter(_format_heading),
    "Heading4": HtmlFormatter(_format_heading),
    "Heading5": HtmlFormatter(_format_heading),
    "Heading6": HtmlFormatter(_format_heading),
}


# ===============================================================================
# Tags that provoke some action in docx2python
# ===============================================================================


class Tags(str, Enum):
    """Tags that provoke some action in docx2python."""

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
    SDT = "w:sdt"
    SDT_PROPERTIES = "w:sdtPr"
    SYM = "w:sym"
    TAB = "w:tab"
    TABLE = "w:tbl"
    TABLE_CELL = "w:tc"
    TABLE_ROW = "w:tr"
    TEXT = "w:t"
    TEXT_MATH = "m:t"


_CONTENT_TAGS = set(Tags) - {
    Tags.RUN_PROPERTIES,
    Tags.PAR_PROPERTIES,
    Tags.SDT_PROPERTIES,
}


def _is_content(elem: EtreeElement) -> bool:
    """Is the element a content element?

    :param elem: xml element
    :return: True if the element is a content element

    Docx2Python ignores spell check, revision, and other elements. This function
    checks that the element is a content element.

    If the element is a content element, it will be processed further.
    """
    return get_prefixed_tag(elem) in _CONTENT_TAGS


def has_content(tree: EtreeElement) -> str | None:
    """Determine if the element has any descendent content elements.

    :param tree: xml element
    :return: first content tag found or None if no content tags are found

    This is to check for text in any skipped elements.

    Docx2Python ignores spell check, revision, and other elements. This function checks
    that no content (paragraphs, run, text, link, ...) is contained in children of any
    ignored elements.

    If no content is found, the element can be safely ignored going forward.
    """

    def iter_content(tree_: EtreeElement) -> Iterator[str]:
        """Yield all content elements in tree.

        :param tree_: xml element
        :yield: child content elements
        :return: None
        """
        if _is_content(tree_):
            yield str(tree_.tag)
        for branch in tree_:
            yield from iter_content(branch)

    return next(iter_content(tree), None)
