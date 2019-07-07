#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""Top-level code (and some other)

:author: Shay Hill
:created: 7/2/2019

Some private methods are here because I wanted to keep them with their tests.
"""
import re
import zipfile
from typing import Optional

from docx2python.docx_context import get_context, pull_image_files
from docx2python.docx_output import DocxContent
from docx2python.docx_text import get_text


def docx2python(
    docx_filename: str, image_folder: Optional[str] = None, html: bool = False
) -> DocxContent:
    """Unzip a docx file and extract contents."""
    zipf = zipfile.ZipFile(docx_filename)
    context = get_context(zipf)
    context["do_html"] = html

    xml_files = zipf.namelist()

    header = []
    for filename in (x for x in xml_files if re.match("word/header[0-9]*.xml", x)):
        header += get_text(zipf.read(filename), context)

    body = get_text(zipf.read("word/document.xml"), context)

    footer = []
    for filename in (x for x in xml_files if re.match("word/footer[0-9]*.xml", x)):
        footer += get_text(zipf.read(filename), context)

    images = pull_image_files(zipf, image_folder)

    zipf.close()
    return DocxContent(
        header=header,
        body=body,
        footer=footer,
        images=images,
        properties=context["docProp2text"],
    )
