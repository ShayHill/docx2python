"""Register namespace entries in xml ``document`` elements.

:author: Shay Hill
:created: 7/5/2019

A ``<w:document>`` element at the top of each xml file defines a namespace::

    <w:document
        xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
        xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    />

These entries can be accessed in the file by their abbreviations::

    <w:p>
        contents of paragraph
    </w:p>

``lxml.etree`` reads ``"<w:p>"`` as

``"{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"``

This module defines the necessary namespaces and transforms ``"w:p"`` to
``{http://...}p``. This allows readable code like::

    if element.tag == qn("w:p"):

instead of::

    if element.tag == "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p":

If somewhere along the line this package just stops working, it may be that the NSMAP
entries have been updated for whatever docx you're working with (though that's not
supposed to ever happen). *If* this happens::

    1) Unzip the docx.
    2) open ``word/document.xml`` in a text editor.
    3) Search for xmlns:w=[some string]
    4) update NSMAP['w'] = some string

Lxml allows (deceptively) easy access to a file's namespaces; however, this is
problematic because ``root_element.nsmap`` may not retrieve all nsmap entries. Other
entries may be buried inside sub-environments further down in the tree. It is safer
to explicate namespace mapping.

If you extend docx2text with other tags, additional NSMAP entries may be necessary.
"""


NSMAP = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "v": "urn:schemas-microsoft-com:vml",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
}


def qn(tag: str) -> str:
    """
    Turn a namespace-prefixed tag into a Clark-notation qualified tag.

    :param tag: namespace-prefixed tag, e.g. ``w:p``
    :return: Clark-notation qualified tag,
        e.g. ``{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p``

    Stands for 'qualified name', a utility function to turn a namespace prefixed tag
    name into a Clark-notation qualified tag name for lxml.

        >>> qn('w:cSld')
        '{http://schemas.../main}cSld'

    Source: https://github.com/python-openxml/python-docx/
    """
    prefix, tagroot = tag.split(":")
    uri = NSMAP[prefix]
    return f"{{{uri}}}{tagroot}"
