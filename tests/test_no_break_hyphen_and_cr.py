"""Test run content elements ``<w:noBreakHyphen/>``, ``<w:cr/>`` and ``<w:softHyphen/>``.

Docx2Python previously dropped all three, so "well<noBreakHyphen/>known" was extracted
as "wellknown" and the text on either side of a ``<w:cr/>`` was joined.

* ``<w:noBreakHyphen/>`` is extracted as a hyphen-minus ("-").
* ``<w:cr/>`` is extracted as a line break ("\\n"), like ``<w:br/>``.
* ``<w:softHyphen/>`` is an optional hyphen with zero width unless the line breaks
  there. It is not extracted, so "co<softHyphen/>operate" is "cooperate".

The test file has four paragraphs:

    1. well<noBreakHyphen/>known (one run)
    2. one<noBreakHyphen/>two (three runs, hyphen in its own bold run)
    3. line one<cr/>line two
    4. co<softHyphen/>operate
"""

from docx2python.main import docx2python
from tests.conftest import RESOURCES

_DOCX = RESOURCES / "no_break_hyphen_and_cr.docx"


def test_no_break_hyphen() -> None:
    """Extract a non-breaking hyphen as a hyphen-minus."""
    with docx2python(_DOCX) as content:
        pars = content.text.split("\n\n")
    assert pars[0] == "well-known"
    assert pars[1] == "one-two"


def test_cr() -> None:
    """Extract a carriage return as a line break."""
    with docx2python(_DOCX) as content:
        pars = content.text.split("\n\n")
    assert pars[2] == "line one\nline two"


def test_soft_hyphen() -> None:
    """Do not extract an optional hyphen."""
    with docx2python(_DOCX) as content:
        pars = content.text.split("\n\n")
    assert pars[3] == "cooperate"


def test_html_true() -> None:
    """Hyphen in its own bold run is wrapped like any other bold text."""
    with docx2python(_DOCX, html=True) as content:
        pars = content.text.split("\n\n")
    assert pars[0] == "well-known"
    assert pars[1] == "one<b>-</b>two"
    assert pars[2] == "line one\nline two"
    assert pars[3] == "cooperate"
