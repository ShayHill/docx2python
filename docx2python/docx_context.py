"""Content from files that aren't ``word/document.xml``.

:author: Shay Hill
:created: 6/26/2019

Most of the "meat" in a docx file is in ``word/document.xml``. These functions retrieve
numbering formats, images, and font styles from *other* files in a decompressed docx.
"""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from lxml import etree

from docx2python.attribute_register import get_localname
from docx2python.namespace import find_by_qn, findall_by_qn, get_attrib_by_qn

if TYPE_CHECKING:
    import zipfile

    from lxml.etree import _Element as EtreeElement  # type: ignore


@dataclasses.dataclass
class NumIdAttrs:
    """NumIdAttrs represents numbering attributes, such as format and start index."""

    fmt: str | None
    start: int | None


def collect_numAttrs(numFmts_root: EtreeElement) -> dict[str, list[NumIdAttrs]]:
    """Collect abstractNum bullet attributes into a dictionary.

    :param numFmts_root: Root element of ``word/numbering.xml``.
    :return: numId mapped to numFmts (by ilvl)

    :background:

    ``word/numbering.xml`` will have two sections.

    **SECTION 1** - Some abstractNum elements defining numbering formats for multiple
    indentation levels::

        <w:abstractNum w:abstractNumId="0">
            <w:lvl w:ilvl="0"><w:numFmt w:val="decimal"/></w:lvl>
            <w:lvl w:ilvl="1"><w:numFmt w:val="lowerLetter"/></w:lvl>
            ...
        </w:abstractNum>

    **SECTION 2** - Some num elements, each referencing an abstractNum. Multiple nums
    may reference the same abstractNum, but each will maintain a separate count (i.e.,
    each numbered paragraph will start from 1, even if it shares a style with another
    paragraph.)::

        <w:num w:numId="1">
            <w:abstractNumId w:val="0"/>
        </w:num>
        <w:num w:numId="2">
            <w:abstractNumId w:val="5"/>
        </w:num>

    **E.g, Given**: *above*

    **E.g., Returns**::

        {
            # -----ilvl=0------ilvl=1------ilvl=2---
            "1": [ NumIdAttrs(fmt:"decimal",start:2),
                NumIdAttrs(fmt:"lowerLetter",start:1), ...],
            "2": ...
        }
    """
    abstractNumId2Attrs: dict[str, list[NumIdAttrs]] = {}

    for abstractNum in findall_by_qn(numFmts_root, "w:abstractNum"):
        id_ = str(get_attrib_by_qn(abstractNum, "w:abstractNumId"))

        abstractNumId2Attrs[id_] = []
        for lvl in findall_by_qn(abstractNum, "w:lvl"):
            numFmtEl = find_by_qn(lvl, "w:numFmt")
            fmt = None
            if numFmtEl is not None:
                fmt = str(get_attrib_by_qn(numFmtEl, "w:val"))
            startEl = find_by_qn(lvl, "w:start")
            start = None
            if startEl is not None:
                qn = get_attrib_by_qn(startEl, "w:val")
                start = int(qn)
            abstractNumId2Attrs[id_].append(NumIdAttrs(fmt=fmt, start=start))

    numId2attrs: dict[str, list[NumIdAttrs]] = {}
    num: EtreeElement
    for num in findall_by_qn(numFmts_root, "w:num"):
        numId = get_attrib_by_qn(num, "w:numId")
        abstractNumId = find_by_qn(num, "w:abstractNumId")
        if abstractNumId is None:
            continue
        abstractNumIdval = get_attrib_by_qn(abstractNumId, "w:val")
        numId2attrs[str(numId)] = abstractNumId2Attrs[str(abstractNumIdval)]

    return numId2attrs


def collect_rels(zipf: zipfile.ZipFile) -> dict[str, list[dict[str, str]]]:
    """Map file to relId to attrib.

    :param zipf: created by ``zipfile.ZipFile("docx_filename")``
    :return: a deep dictionary ``{filename: list of Relationships``

    Each rel in list of Relationships is::

        {
            "Id": "rId1",
            "Type": "http...",
            "Target": "path to file in docx"
        }

    There are several rels files:

    ``_rels/.rels``: rels related to entire structure.  The identity of
        ``word/document.xml`` is here. (It might be called ``word/document2.xml`` or
        something else. Checking here is the best way to make sure.)

    ``word/_rels/document.xml.rels``: images, headers, etc. referenced by
        ``word/document.xml``

    ``word/_rels/header1.xml.rels``: images, etc. for ``header1.xml``

    ...

    Get everything from everywhere. Map ``_rels/.rels`` to ``'rels'`` and everything
    else to e.g., ``'document'`` or ``'header'``. RelIds are **not** unique between
    these files.

    **E.g, Given**::

    # one of several files

        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <Relationships xmlns="http://schemas.../relationships">
            <Relationship Id="rId3" Type="http://schemas... \
                /extended-properties" Target="docProps/app.xml"/>
            <Relationship Id="rId2" Type="http://schemas... \
                /core-properties" Target="docProps/core.xml"/>
            <Relationship Id="rId1" Type="http://schemas... \
                /officeDocument" Target="word/document.xml"/>
            <Relationship Id="rId4" Type="http://schemas... \
                /custom-properties" Target="docProps/custom.xml"/>
        </Relationships>

    **Returns**::

        {
            "filename": [
                {
                    "Id": "rId3",
                    "Type": "http://schemas.../extended-properties",
                    "Target": "docProps/app.xml",
                },
                {
                    "Id": "rId2",
                    "Type": "http://schemas.../core-properties",
                    "Target": "docProps/core.xml",
                },
            ]
        }
    """
    path2rels: dict[str, list[dict[str, str]]] = {}
    for rels in (x for x in zipf.namelist() if x[-5:] == ".rels"):
        rels_elem = etree.fromstring(zipf.read(rels))
        path2rels[rels] = [
            {str(y): str(z) for y, z in x.attrib.items()} for x in rels_elem
        ]
        path2rels[rels].append(
            {
                "Id": "none",
                "Type": etree.QName(rels_elem.tag).namespace or "",
                "Target": rels,
            }
        )

    return path2rels


def collect_docProps(root: EtreeElement) -> dict[str, str | None]:
    """Get author, modified, etc. from core-properties (should be docProps/core.xml).

    :param root: root of the XML tree
    :return: document property names mapped to values

    **E.g., Given**::

        <cp:coreProperties xmlns:cp="http://schemas.openxmlformats...">
            <dc:title>SG-DOP-5009 - Operate ROMAR swarf unit
            </dc:title>
            <dc:creator>Shay Hill
            </dc:creator>
            <cp:lastModifiedBy>Shay Hill
            </cp:lastModifiedBy>
            <cp:revision>6
            </cp:revision>
            <cp:lastPrinted>2017-11-17T15:47:00Z
            </cp:lastPrinted>
            <dcterms:created xsi:type="dcterms:W3CDTF">2019-01-10T07:21:00Z
            </dcterms:created>
            <dcterms:modified xsi:type="dcterms:W3CDTF">2019-01-11T11:41:00Z
            </dcterms:modified>
        </cp:coreProperties>

    **E.g., Returns**::

        {
            "title": "SG-DOP-5009 - Operate ROMAR swarf unit",
            "creator": "Shay Hill",
            "lastModifiedBy": "Shay Hill",
            "revision": "6",
            ...
        }
    """
    return {get_localname(x): x.text for x in root}
