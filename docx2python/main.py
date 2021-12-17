#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""Top-level code

:author: Shay Hill
:created: 7/2/2019
"""
from pathlib import Path
from typing import Optional, Union
from warnings import warn

from .docx_output import DocxContent
from .docx_reader import DocxReader


def docx2python(
    docx_filename: Union[str, Path],
    image_folder: Optional[str] = None,
    html: bool = False,
    paragraph_styles: bool = False,
    extract_image: bool = None,
) -> DocxContent:
    """
    Unzip a docx file and extract contents.

    :param docx_filename: path to a docx file
    :param image_folder: optionally specify an image folder
        (images in docx will be copied to this folder)
    :param html: bool, extract some formatting as html
    :param paragraph_styles: prepend the paragraphs style (if any, else "") to each
        paragraph. This will only be useful with ``*_runs`` attributes.
    :param extract_image: bool, extract images from document (default True)
    :return: DocxContent object
    """
    if extract_image is not None:
        warn(
            "'extract_image' is no longer a valid argument for docx2python. If an "
            "image_folder is given as an argument to docx2python, images will be "
            "written to that folder. A folder can be provided later with "
            "``docx2python(filename).write_images(image_folder)``. Images files are "
            "available as before with ``docx2text(filename).images`` attribute."
        )
    docx_context = DocxReader(docx_filename, html, paragraph_styles)
    docx_content = DocxContent(docx_context, locals())
    if image_folder:
        _ = docx_content.images
    return docx_content
