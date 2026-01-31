"""Test GitHub Issue #93.

User ronwsg reports: When using the docx2python to parse Word documents, tables with
merged cells often trigger extraction errors Symptom: The parser fails with
"IndexError: list index out of range"

Submitted test file: `Weekly Schedule.docx`, a file on Google Drive.

The issue was caused by trying to copy a cell from a previous row when the previous row
did not have enough cells. This is not a recoverable issue, because Word destroys
table-geometry information when cells are merged or when tables are inserted into other
tables. Docx2Python makes a good guess at the original geometry, but that guess is not
100%. Addressed the issue by suppressing the IndexError if the guess is wrong. In the
test case, this did not lose any data, but it is conceivable some cell data would be
extracted but not copied into all positions in a shared cell.

:author: Shay Hill
:created: 2026-01-30
"""

from docx2python.main import docx2python
from tests.conftest import RESOURCES

test_file = RESOURCES / "Weekly Schedule.docx"


class TestIssue93:
    def test_explicit_close(self) -> None:
        """Closing DocxReader closes the zipfile."""
        content = docx2python(test_file)
        print(content.text)
