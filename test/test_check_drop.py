#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""Test checkbox exports from a user-submitted and my own checkbox files.

:author: Shay Hill
:created: 6/17/2020

List items from the user-submitted docx were listed B then A. Confusing for the test,
but I didn't want to alter it in my version of Word.
"""

import os

from docx2python.main import docx2python


class TestCheckboxToHtml:
    def test_user_checked_dropdown0(self) -> None:
        """Get checked-out box glyph and second dd entry"""
        extraction = docx2python(os.path.join("resources", "checked_drop1.docx"))
        assert extraction.text == "☒ \n\n\n\n\n\nPIlihan A"

    def test_user_unchecked_dropdown1(self) -> None:
        """Get unchecked box glyph and first dd entry"""
        extraction = docx2python(os.path.join("resources", "unchecked_drop0.docx"))
        assert extraction.text == "☐ \n\n\n\n\n\nPiihan B"

    def test_my_checkbox(self) -> None:
        """A good selection of checked and unchecked boxes, and several dropdowns"""
        extraction = docx2python(os.path.join("resources", "check_drop_my.docx"))
        assert extraction.body == [
            [
                [
                    [
                        "[user unchecked]☐[user unchecked]",
                        "",
                        "[user checked]☒[user checked]",
                        "",
                        "[my unchecked]☐[my unchecked]",
                        "",
                        "[my checked]☒[my checked]",
                        "",
                        "User dropdown (Piihan B)",
                        "Piihan B",
                        "",
                        "My dropdown (no choice)",
                        "Choose an item.",
                        "",
                        "My dropdown (chose A)",
                        "my_item_A",
                        "",
                        "My dropdown (chose B)",
                        "my_item_B",
                    ]
                ]
            ]
        ]
