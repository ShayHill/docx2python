"""Test accessing SDT properties above a paragraph.

issue #81

User YashasviMantha requested a way to access Content Control Block properties. In
the xml, these are called Structured Document Tags (SDT). To allow this, I added two
features:

    1. Each Par instance now contains a pointer to the XML element from which it was
       created.
    2. Add a `tag` argument to `gather_Pr` that allows the caller to search up for
        the Pr of a parent element.

This is a simple test and an example. See `get_sdt_tag` example function for a
description of the sdt context in xml and how to access it.

:author: Shay Hill
:created: 2024-11-17
"""

from __future__ import annotations

from lxml.etree import _Element as EtreeElement  # type: ignore

from docx2python.attribute_register import Tags
from docx2python.iterators import iter_paragraphs
from docx2python.main import docx2python
from docx2python.text_runs import gather_Pr
from tests.conftest import RESOURCES

_DOCX = RESOURCES / "ControlTest.docx"


def get_sdt_tag(elem: EtreeElement) -> str | None:
    """If elem is or is inside a <w:sdt> element, try to find the sdt props tag value.

    :param elem: lxml.etree._Element object
    :return: tag value of sibling or parent sdtPr element or None
    ```
    <w:body>
        <w:sdt>
            <w:sdtPr>
                <w:tag w:val="my_tag"/>
            </w:sdtPr>
            <w:sdtContent>
                <w:p> </w:p>
                <w:p> </w:p>
            </w:sdtContent>
        </w:sdt>
    </w:body>
    ```
    """
    properties_dict = gather_Pr(elem, Tags.SDT)
    return properties_dict.get("tag")


class TestStructuredDocumentTags:

    def test_paragraphs_in_sdt_elements(self) -> None:
        """Get the SDT tag above a paragraph."""
        with docx2python(_DOCX) as extraction:
            pars = extraction.document_pars

        text_paragraphs: list[str] = []

        for paragraph in iter_paragraphs(pars):
            if paragraph.elem is None:
                par_tag = None
            else:
                par_tag = get_sdt_tag(paragraph.elem)
            par_text = "".join(paragraph.run_strings)
            text_paragraphs.append(f"[{par_tag}]: {par_text}")

        assert text_paragraphs == [
            "[Test_Control]: This is a test",
            "[Test_Control]: For a content control or content container in word. ",
        ]
