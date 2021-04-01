#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""Top-level code (and some other)

:author: Shay Hill
:created: 7/2/2019

Some private methods are here because I wanted to keep them with their tests.
"""
from typing import Optional

from .docx_output import DocxContent
from .globs import DocxContext


# TODO: raise FutureWarning for `extract_image` argument
def docx2python(
    docx_filename: str,
    image_folder: Optional[str] = None,
    html: bool = False,
    paragraph_styles: bool = False,
    extract_image: bool = True,
) -> DocxContent:
    """Unzip a docx file and extract contents.

    :param docx_filename: path to a docx file
    :param image_folder: optionally specify an image folder
        (images in docx will be copied to this folder)
    :param html: bool, extract some formatting as html
    :param paragraph_styles: prepend the paragraphs style (if any, else "") to each
        paragraph. This will only be useful with ``*_runs`` attributes.
    :param extract_image: bool, extract images from document (default True)
    :return: DocxContent object
    """
    docx_context = DocxContext(docx_filename, image_folder, html, paragraph_styles)
    docx_content = DocxContent(docx_context)
    if image_folder:
        _ = docx_content.images
    return docx_content
