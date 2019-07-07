#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""Content from files that aren't ``word/document.xml``

:author: Shay Hill
:created: 6/26/2019

Most of the "meat" in a docx file is in ``word/document.xml``. These functions retrieve
numbering formats, images, and font styles from *other* files in a decompressed docx.

Several functions here take a bytes-format document from a decompressed docx.file.
Create such with::

            import zipfile

            zipf = zipfile.ZipFile("docx_filename.docx")
            xml = zipf.read("trash/numbering.xml")
"""
import os
import pathlib
import re
import zipfile
from collections import defaultdict
from typing import Any, Dict, List, Optional
from xml.etree import ElementTree

# namespace map. see qn
from docx2python.namespace import qn


# noinspection PyPep8Naming
def collect_numFmts(xml: bytes) -> Dict[str, List[str]]:
    """
    Collect abstractNum bullet formats into a dictionary

    :param xml: ``trash/numbering.xml`` from a decompressed docx file

    :returns: numId mapped to numFmts (by ilvl)

    :background:

    ``trash/numbering.xml`` will have two sections.

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
            "1": ["decimal", "lowerLetter", ...],
            "2": ...
        }
    """
    abstractNumId2numFmts = {}

    root = ElementTree.fromstring(xml)
    for abstractNum in root.findall(qn("w:abstractNum")):
        id_ = abstractNum.attrib[qn("w:abstractNumId")]
        abstractNumId2numFmts[id_] = []
        for lvl in abstractNum.findall(qn("w:lvl")):
            numFmt = lvl.find(qn("w:numFmt"))
            abstractNumId2numFmts[id_].append(numFmt.attrib[qn("w:val")])

    numId2numFmts = {}
    for num in root.findall(qn("w:num")):
        numId = num.attrib[qn("w:numId")]
        abstractNumId = num.find(qn("w:abstractNumId")).attrib[qn("w:val")]
        numId2numFmts[numId] = abstractNumId2numFmts[abstractNumId]

    return numId2numFmts


# noinspection PyPep8Naming
def collect_image_rels(xml: bytes) -> Dict[str, str]:
    """Collect relId with images

    :param xml: ``word/_rels/document.xml.rels`` from a decompressed docx file
    :returns: ``relId`` mapped to ``Target``.

    **E.g, Given**::

        <Relationships>
            <Relationship Id="rId8" Target="webSettings.xml"/>  # ignore this one
            <Relationship Id="rId13" Target="media/image5.jpeg"/>  # map Id to Target
        <Relationships>

    **E.g., Returns**::

        {"rId13": "image5.jpg"}
    """
    Id2Target = {}
    root = ElementTree.fromstring(xml)
    for rel in root:
        image = re.search(r"media/(image\d+\.\w+)", rel.attrib["Target"])
        if image:
            Id2Target[rel.attrib["Id"]] = image.group(1)
    return Id2Target


# noinspection PyPep8Naming
def collect_docProps(xml: bytes) -> Dict[str, str]:
    # noinspection SpellCheckingInspection
    """ Get author, modified, etc. from docProps

        :param xml: ``DocProps/core.xml`` from a decompressed docx file
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
    docProp2text = {}
    root = ElementTree.fromstring(xml)
    for dc in root:
        docProp2text[re.match(r"{.+}(\w+)", dc.tag).group(1)] = dc.text
    return docProp2text


# noinspection PyPep8Naming
def get_context(zipf: zipfile.ZipFile) -> Dict[str, Any]:
    """
    Collect context information from docProps, rels etc.

    :param zipf: created by ``zipfile.ZipFile("docx_filename")``
    :return: dictionaries

        * rId2Target - rel Id mapped to image files
        * docProp2text - document properties like 'modified' and 'created'
        * numId2numFmts - paragraph IDs mapped to number and bullet formats
        * numIdcount - a counter starting at 0 for each ilvl of each numbered list

        The last two will only be present in documents with bulleted or numbered lists.
    """
    context = {
        "rId2Target": collect_image_rels(zipf.read("word/_rels/document.xml.rels")),
        "docProp2text": collect_docProps(zipf.read("docProps/core.xml")),
    }
    try:
        numId2numFmts = collect_numFmts(zipf.read("word/numbering.xml"))
        context["numId2numFmts"] = numId2numFmts
        context["numId2count"] = {
            x: defaultdict(lambda: 0) for x in numId2numFmts.keys()
        }
    except KeyError:
        # no bullets or numbered paragraphs in file
        pass
    return context


def pull_image_files(
    zipf: zipfile.ZipFile, image_directory: Optional[str] = None
) -> Dict[str, bytes]:
    """
    Copy images from zip file.

    :param zipf: created by ``zipfile.ZipFile(docx_filename)``
    :param image_directory: optional destination for copied images
    :return: Image names mapped to images in binary format.

        To write these to disc::

            with open(key, 'wb') as file:
                file.write(value)

    :side effects: Given an optional image_directory, will write the images out to file.
    """
    images = {
        os.path.basename(x): zipf.read(x)
        for x in zipf.namelist()
        if re.match(r"word/media/image\d+", x)
    }
    if image_directory is not None:
        pathlib.Path(image_directory).mkdir(parents=True, exist_ok=True)
        for file, image in images.items():
            with open(os.path.join(image_directory, file), "wb") as image_copy:
                image_copy.write(image)
    return images
