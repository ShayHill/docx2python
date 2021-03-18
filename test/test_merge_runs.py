#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
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
import os


def test_merge_runs():
    """
    Merge duplicate, consecutive hyperlinks

    TODO: test text and run merging (see below)
    The output text would look the same whether run and text elements were merged.
    This test only verifies that hyperlink elements have been merged, else the output
    text would contain something closer to ``<a>hy</a><a>per</a><a>link</a>``
    """
    assert (
        '<a href="https://www.shayallenhill.com">hyperlink</a>'
        in docx2python(os.path.join("resources", "merged_links.docx")).text
    )
