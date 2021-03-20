#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
""" Run styles converted to html

:author: Shay Hill
:created: 3/18/2021

TODO: Implement all and test against resources/run_styles.docx

<w:r><w:rPr><w:sz w:val="32"/><w:szCs w:val="32"/></w:rPr><w:t>16 point</w:t></w:r>
<w:r><w:rPr><w:color w:val="FF0000"/></w:rPr><w:t>Red</w:t></w:r>
<w:r><w:rPr><w:rFonts w:ascii="Courier New" w:hAnsi="Courier New" w:cs="Courier New"/>
    </w:rPr><w:t>Courier new</w:t></w:r>
<w:r><w:rPr><w:i/><w:iCs/></w:rPr><w:t>Italic</w:t></w:r>
<w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>Bold</w:t></w:r>
<w:r><w:rPr><w:u w:val="single"/></w:rPr><w:t>Underline</w:t></w:r>
<w:r><w:rPr><w:strike/></w:rPr><w:t>Strikethrough</w:t></w:r>
<w:r><w:rPr><w:dstrike/></w:rPr><w:t>Double Strikethrough</w:t></w:r>
<w:r><w:rPr><w:vertAlign w:val="superscript"/></w:rPr><w:t>Superscript</w:t></w:r>
<w:r><w:rPr><w:vertAlign w:val="subscript"/></w:rPr><w:t>Subscript</w:t></w:r>
<w:r><w:rPr><w:smallCaps/></w:rPr><w:t>Small Caps</w:t></w:r>
<w:r><w:rPr><w:caps/></w:rPr><w:t>All Caps</w:t></w:r>
<w:r><w:rPr><w:highlight w:val="yellow"/></w:rPr><w:t>Highlighted yellow</w:t></w:r>
<w:r><w:rPr><w:highlight w:val="green"/></w:rPr><w:t>Highlighted green</w:t></w:r>

<i> italic
<b> bold
<u> underline
<s> strike
<del> double strike
<sup> superscript
<sub> subscript
<font style="font-variant: small-caps">small caps
<font style="text-transform:uppercase">all caps
<span style="background-color: yellow">highlighted yellow
<span style="background-color: green">highlighted green
"""
