"""Test the lineage attribute of Par instances.

:author: Shay Hill
:created: 2024-07-14
"""

from docx2python.iterators import (
    is_tbl,
    is_tc,
    is_tr,
    iter_cells,
    iter_paragraphs,
    iter_rows,
    iter_tables,
)
from docx2python.main import docx2python

from .conftest import RESOURCES


class TestLineage:
    """Are lineage tags correct for Par instances?"""

    def test_explicit(self):
        """Output matches expected lineage."""
        with docx2python(RESOURCES / "paragraphs_and_tables.docx") as extraction:
            pars = extraction.document_pars
        lineages = [par.lineage for par in iter_paragraphs(pars)]
        assert lineages == [
            ("document", None, None, None, "p"),
            ("document", "tbl", "tr", "tc", "p"),
            ("document", "tbl", "tr", "tc", "p"),
            ("document", "tbl", "tr", "tc", "p"),
            ("document", "tbl", "tr", "tc", "p"),
            ("document", "tbl", "tr", "tc", "p"),
            ("document", "tbl", "tr", "tc", "p"),
            ("document", None, None, None, "p"),
            ("document", None, None, None, "p"),
            ("document", "tbl", "tr", "tc", "p"),
            ("document", "tbl", "tr", "tc", "p"),
            ("document", "tbl", "tr", "tc", "p"),
            ("document", "tbl", "tr", "tc", "p"),
            ("document", None, None, None, "p"),
        ]


class TestTableIdentification:
    """Are tables identified correctly?"""

    def test_is_tbl(self):
        """Tables are identified correctly."""
        with docx2python(RESOURCES / "paragraphs_and_tables.docx") as extraction:
            pars = extraction.document_pars
        assert [is_tbl(tbl) for tbl in iter_tables(pars)] == [
            False,
            True,
            False,
            True,
            False,
        ]

    def test_is_tr(self):
        """Tables are identified correctly."""
        with docx2python(RESOURCES / "paragraphs_and_tables.docx") as extraction:
            pars = extraction.document_pars
        assert [is_tr(tr) for tr in iter_rows(pars)] == [
            False,
            True,
            True,
            True,
            False,
            True,
            True,
            True,
            True,
            False,
        ]

    def test_is_tc(self):
        """Tables are identified correctly."""
        with docx2python(RESOURCES / "paragraphs_and_tables.docx") as extraction:
            pars = extraction.document_pars
        assert [is_tc(tc) for tc in iter_cells(pars)] == [
            False,
            True,
            True,
            True,
            True,
            True,
            True,
            False,
            True,
            True,
            True,
            True,
            False,
        ]
