"""Top-level code.

:author: Shay Hill
:created: 7/2/2019
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from docx2python.docx_output import DocxContent
from docx2python.docx_reader import DocxReader

if TYPE_CHECKING:
    import os
    from io import BytesIO


def docx2python(
    docx_filename: str | os.PathLike[str] | BytesIO,
    image_folder: str | os.PathLike[str] | None = None,
    *,
    html: bool = False,
    duplicate_merged_cells: bool = True,
) -> DocxContent:
    """Unzip a docx file and extract contents.

    :param docx_filename: path to a docx file
    :param image_folder: optionally specify an image folder
        (images in docx will be copied to this folder)
    :param html: bool, extract some formatting as html
    :param duplicate_merged_cells: bool, duplicate merged cells to return a mxn
        nested list for each table (default True)
    :return: DocxContent object
    """
    docx_context = DocxReader(
        docx_filename, html=html, duplicate_merged_cells=duplicate_merged_cells
    )
    docx_content = DocxContent(docx_context, image_folder)
    if image_folder:
        _ = docx_content.images
    return docx_content
