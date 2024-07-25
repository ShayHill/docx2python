""" Fix bullets in pages created in Pages

:author: Shay Hill
:created: 10/5/2020

Issue 11:

I have seen this happening for files created in Pages but not in files created in
MSWord.

How to reproduce:
    Use Pages (MacOS app) to write a document
    save the document as docx
    attempt to extract using docx2python

It seems Pages is adding abstractNum nodes that don't contain w:lvl nodes. For example:
        <w:multiLevelType w:val="hybridMultilevel"/>
        <w:numStyleLink w:val="Numbered"/>
    </w:abstractNum>

collect_numFmts (from docx_context.py) then reads and stores these in the context as [].
This context is then passed down to _get_bullet_string (from docx_text.py). Then the
IndexError when we try to get the number format from context.

User Raiyan provided two docx files created in pages:
    * created-in-pages-paragraphs-only.docx should work now (v 1.25)
    * created-in-pages-bulleted-lists.docx should fail (v 1.25) with above-described
    error.
"""

from docx2python.main import docx2python
from tests.conftest import RESOURCES


class TestParagraphsOnly:
    """Confirming this works with v1.25"""

    def test_paragraphs_only(self) -> None:
        """Run without issue"""
        pars = docx2python(RESOURCES / "created-in-pages-paragraphs-only.docx")
        assert pars.text == (
            "\n\nThis is a document for testing docx2python module.\n\n\n\nThis "
            "document contains paragraphs.\n\n\n\nThis document does not contain any "
            "bulleted lists.\n\n"
        )
        pars.close()


class TestBulletedLists:
    """Replace numbering format with bullet (--) when format cannot be determined"""

    def test_bulleted_lists(self) -> None:
        pars = docx2python(RESOURCES / "created-in-pages-bulleted-lists.docx")
        assert pars.text == (
            "\n\nThis is a document for testing docx2python module.\n\n\n\n"
            "--\tWhy did the chicken cross the road?\n\n"
            "\t--\tJust because\n\n"
            "\t--\tDon't know\n\n"
            "\t--\tTo get to the other side\n\n"
            "--\tWhat's the meaning of life, universe and everything?\n\n"
            "\t--\t42\n\n"
            "\t--\t0\n\n"
            "\t--\t-1\n\n"
        )
        pars.close()
