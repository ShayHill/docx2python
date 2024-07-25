""" Test that consecutive links pointing to the same address are merged.

:author: Shay Hill
:created: 3/17/2021

Such links will look like this (after removing proofErr, rsid, and other noise).

    <w:p>
        <w:hyperlink r:id="rId7">  <!-- points to http://www.shayallenhill.com -->
            <w:r>
                <w:t>hy</w:t>
            </w:r>
        </w:hyperlink>
        <w:hyperlink r:id="rId8">  <!-- points to http://www.shayallenhill.com -->
            <w:r>
                <w:t>per</w:t>
            </w:r>
        </w:hyperlink>
        <w:hyperlink r:id="rId9">  <!-- points to http://www.shayallenhill.com -->
            <w:r>
                <w:t>link</w:t>
            </w:r>
        </w:hyperlink>
    </w:p>

Docx2python condenses these to

    <w:p>
        <w:hyperlink r:id="rId7">  <!-- points to http://www.shayallenhill.com -->
            <w:r>
                <w:t>hy</w:t>
            </w:r>
            <w:r>
                <w:t>per</w:t>
            </w:r>
            <w:r>
                <w:t>link</w:t>
            </w:r>
        </w:hyperlink>
    </w:p>

Then to

    <w:p>
        <w:hyperlink r:id="rId7">  <!-- points to http://www.shayallenhill.com -->
            <w:r>
                <w:t>hyperlink</w:t>
            </w:r>
        </w:hyperlink>
    </w:p>

This module tests the final result.
"""

from docx2python.main import docx2python
from tests.conftest import RESOURCES


class TestHyperlink:
    def test_prints(self) -> None:
        """Consecutive hyperlinks referencing same target are joined"""
        with docx2python(RESOURCES / "hyperlink.docx") as extraction:
            assert extraction.body_runs == [
                [
                    [
                        [
                            [
                                "This is a link to ",
                                '<a href="http://www.shayallenhill.com/">'
                                + "my website</a>",
                                ".",
                            ]
                        ]
                    ]
                ]
            ]
