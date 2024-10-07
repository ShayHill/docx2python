"""Test the dropdown selector in a table.

Issue: [https://github.com/ShayHill/docx2python/issues/73]

User iamahcy reports that a ContentControl dropdown selector in a table raises an
error.

The issue is that dropdown selectors are a nested table, and the first row of that
table requests a vMerge. The fix was to reject any vMerge (copy the cell above)
request in the first row of any table.

:author: Shay Hill
:created: 2024-09-26
"""

from docx2python import docx2python
from tests.conftest import RESOURCES

test_file = RESOURCES / "list_index_a.docx"


class TestContentControlDropdownSelectorInTable:
    def test_content_control_dropdown_selector_in_table(self):
        """Test the dropdown selector in a table."""
        with docx2python(test_file) as docx_content:
            content_runs = docx_content.document

        # fmt: off
        assert content_runs == [
            [
                [
                    [""], [""], [""], [""], ["", ""]
                ],
                [
                    [""], [""], [""], [""], ["", ""]
                ],
                [
                    [""], [""], [""], [""], ["", ""]
                ],
                [
                    [""], [""], [""], [""], ["", ""]
                ],
                [
                    [""], [""], [""], [""], ["", ""]
                ],
                [
                    [""]
                ],
            ],
            [
                [
                    ["Silver"]
                ]
            ],
            [
                [
                    [""], [""], [""]
                ],
                [
                    ["", ""], ["", ""], ["", ""], ["", ""], ["", ""]
                ]
            ],
            [
                [
                    [""]
                ]
            ],
            [
                [
                    [""], [""]
                ]
            ],
            [
                [
                    [""], [""]
                ]
            ],
        ]
        # fmt: on
