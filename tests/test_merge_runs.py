""" Test that consecutive links pointing to the same address are merged.

:author: Shay Hill
:created: 3/17/2021

There are a few ways consecutive elements can be "identical":
    * same link
    * same style

Often, consecutive, "identical" elements are written as separate elements,
because they aren't identical to Word. Work keeps track of revision history,
spelling errors, etc., which are meaningless to docx2python.

<w:p>
    <w:hyperlink r:id="rId7">  <!-- points to http://www.shayallenhill.com -->
        <w:r>
            <w:t>hy</w:t>
        </w:r>
    </w:hyperlink>
    <w:proofErr/>  <!-- docx2python will ignore this proofErr -->
    <w:hyperlink r:id="rId8">  <!-- points to http://www.shayallenhill.com -->
        <w:r>
            <w:t>per</w:t>
        </w:r>
    </w:hyperlink>
    <w:hyperlink r:id="rId9">  <!-- points to http://www.shayallenhill.com -->
        <w:r w:rsid="asdfas">  <!-- docx2python will ignore this rsid -->
            <w:t>link</w:t>
        </w:r>
    </w:hyperlink>
</w:p>

Docx2python condenses the above to (by merging links)

<w:p>
    <w:hyperlink r:id="rId7">  <!-- points to http://www.shayallenhill.com -->
        <w:r>
            <w:t>hy</w:t>
        </w:r>
        <w:r>
            <w:t>per</w:t>
        </w:r>
        <w:r w:rsid="asdfas">  <!-- docx2python will ignore this rsid -->
            <w:t>link</w:t>
        </w:r>
    </w:hyperlink>
</w:p>

Then to (by merging runs)

<w:p>
    <w:hyperlink r:id="rId7">  <!-- points to http://www.shayallenhill.com -->
        <w:r>
            <w:t>hy</w:t>
            <w:t>per</w:t>
            <w:t>link</w:t>
        </w:r>
    </w:hyperlink>
</w:p>

Then finally to (by merging text)

<w:p>
    <w:hyperlink r:id="rId7">  <!-- points to http://www.shayallenhill.com -->
        <w:r>
            <w:t>hyperlink</w:t>
        </w:r>
    </w:hyperlink>
</w:p>
"""

from docx2python.main import docx2python
from tests.conftest import RESOURCES


def test_merge_runs():
    """
    Merge duplicate, consecutive hyperlinks

    The output text would look the same whether run and text elements were merged.
    This test only verifies that hyperlink elements have been merged, else the output
    text would contain something closer to ``<a>hy</a><a>per</a><a>link</a>``
    """
    extraction = docx2python(RESOURCES / "merged_links.docx")
    assert extraction.body_runs == [
        [
            [
                [
                    [
                        "This page created by putting three links to the same address "
                        + "in three different paragraphs (as below) …"
                    ],
                    ['<a href="https://www.shayallenhill.com">hy</a>'],
                    ['<a href="https://www.shayallenhill.com">per</a>'],
                    ['<a href="https://www.shayallenhill.com">link</a>'],
                    ["Then removing the endlines to create a single link."],
                    ['<a href="https://www.shayallenhill.com">hyperlink</a>'],
                    [
                        "Internally, the XML records the joined paragraphs as "
                        + "three consecutive links, each with a different r:id, "
                        + "all r:ids referencing the same address. Docx2python v2+ "
                        + "should re-join these consecutive links."
                    ],
                    [],
                    [],
                ]
            ]
        ]
    ]
    extraction.close()
