#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
""" Test that consecutive links pointing to the same address are merged.

:author: Shay Hill
:created: 3/17/2021

Word will split runs to mark spell-check highlighting, revision dates, and other 
things that are not required for docx2python. This makes identifying headings, 
etc. problematic because the words are split. 

Such links will look like this (after removing proofErr, rsid, and other noise).

    <w:p>
        <w:rpr ... />
        <w:r>
            <w:t>some </w:t>
        </w:r>
        <w:prooferr ... />
        <w:r>
            <w:t>text</w:t>
        </w:r>
    </w:p>
    
Docx2python condenses these to 

    <w:p>
        <w:r>
            <w:t>some text</w:t>
        </w:r>
    </w:p>
"""

from docx2python.main import docx2python
import os


def test_merge_runs():
    """TODO: put some assertions. This just runs it so I can breakpoint and check the
    xml from within the docx_text module."""
    docx2python(os.path.join("resources", "merged_links.docx")).text
