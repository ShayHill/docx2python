"""Test extracting comments.

User flyguy62n requested comment extraction. Extract comments as tuples (text,
author, date, comment).

:author: Shay Hill
:created: 2024-03-29
"""

import os
import sys

import pytest

project = os.path.abspath(os.path.join(__file__, "..", ".."))
sys.path.append(project)


from paragraphs import par

from docx2python import docx2python
from tests.conftest import RESOURCES


def test_comments() -> None:
    """Extract comments and some comment metadata."""
    pars = docx2python(RESOURCES / "comments.docx")
    comments = pars.comments

    pars.close()
    assert comments == [
        (
            par(
                """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
                eiusmod tempor incididunt ut labore et dolore magna aliqua."""
            ),
            "Randy Bartels",
            "2024-03-28T17:22:00Z",
            "COMMENT",
        ),
        (
            par(
                """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
                eiusmod tempor incididunt ut labore et dolore magna aliqua."""
            ),
            "Randy Bartels",
            "2024-03-28T17:22:00Z",
            "RESPONSE",
        ),
        (
            par(
                """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
                eiusmod tempor incididunt ut labore et dolore magna aliqua."""
            ),
            "Shay Hill",
            "2024-03-29T12:10:00Z",
            "Response from Shay Hill",
        ),
        (
            "tempor incididunt ut labore et dolore magna aliqua.",
            "Shay Hill",
            "2024-03-29T12:28:00Z",
            "Comment on subset starting with tempor",
        ),
        (
            par(
                """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
                eiusmod tempor incididunt ut labore et dolore magna aliqua."""
            ),
            "Randy Bartels",
            "2024-03-28T17:22:00Z",
            "COMMENT on par 5",
        ),
        (
            par(
                """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
                eiusmod tempor incididunt ut labore et dolore magna aliqua."""
            ),
            "Randy Bartels",
            "2024-03-28T17:22:00Z",
            "RESPONSE to comment on par 5",
        ),
        (
            par(
                """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
                eiusmod tempor incididunt ut labore et dolore magna aliqua."""
            ),
            "Shay Hill",
            "2024-03-29T12:10:00Z",
            "Response from Shay Hill on par 5",
        ),
        (
            "tempor incididunt ut labore et dolore magna aliqua.",
            "Shay Hill",
            "2024-03-29T12:28:00Z",
            "Comment on subset starting with tempor on par 5",
        ),
    ]


@pytest.fixture(scope="module")
def test_file_with_comments():
    test_file = RESOURCES / "test_file_with_comments.docx"
    pars = docx2python(test_file)
    yield pars.comments
    pars.close()


class TestAdditionalComments:
    test_file = RESOURCES / "test_file_with_comments.docx"

    def test_comment_1(
        self, test_file_with_comments: "list[tuple[str, str, str, str]]"
    ) -> None:
        """Extract the first comment."""
        comment = test_file_with_comments[0]
        assert comment == (
            "magna ",
            "Randy Bartels",
            "2024-04-02T16:57:00Z",
            "Comment 1",
        )

    def test_comment_2(
        self, test_file_with_comments: "list[tuple[str, str, str, str]]"
    ) -> None:
        """Extract the first comment."""
        comment = test_file_with_comments[1]
        assert comment == (
            "quis ",
            "Randy Bartels",
            "2024-04-02T16:58:00Z",
            "Comment 2",
        )

    def test_comment_3(
        self, test_file_with_comments: "list[tuple[str, str, str, str]]"
    ) -> None:
        """Extract the first comment."""
        comment = test_file_with_comments[2]
        assert comment == (
            "Bibendum",
            "Randy Bartels",
            "2024-04-02T16:58:00Z",
            "Comment 3",
        )

    def test_comment_with_hyperlink(
        self, test_file_with_comments: "list[tuple[str, str, str, str]]"
    ) -> None:
        """Extract the first comment."""
        comment = test_file_with_comments[3]
        assert comment == (
            "dolor ",
            "Randy Bartels",
            "2024-04-02T16:58:00Z",
            'Comment 4 with <a href="http://www.google.com">hyperlink</a>',
        )

    def test_comment_5(
        self, test_file_with_comments: "list[tuple[str, str, str, str]]"
    ) -> None:
        """Extract the first comment."""
        comment = test_file_with_comments[4]
        assert comment == (
            "suspendisse ",
            "Randy Bartels",
            "2024-04-02T16:59:00Z",
            "Comment 5",
        )

    def test_comment_with_a_response(
        self, test_file_with_comments: "list[tuple[str, str, str, str]]"
    ) -> None:
        """Extract the first comment."""
        comment = test_file_with_comments[5]
        assert comment == (
            "suspendisse ",
            "Randy Bartels",
            "2024-04-02T16:59:00Z",
            "With a response",
        )

    def test_long_comment(
        self, test_file_with_comments: "list[tuple[str, str, str, str]]"
    ) -> None:
        """Extract the first comment."""
        comment = test_file_with_comments[6]
        assert comment == (
            "Amet ",
            "Randy Bartels",
            "2024-04-02T17:00:00Z",
            par(
                """Comment 6 with a long comment.\n\nmagna fringilla urna porttitor
                rhoncus dolor purus non enim praesent elementum facilisis leo vel
                fringilla est ullamcorper eget nulla facilisi etiam dignissim diam
                quis enim lobortis scelerisque fermentum dui faucibus in ornare quam
                viverra orci sagittis eu volutpat odio facilisis mauris\n\nsit amet
                massa vitae tortor condimentum lacinia quis vel eros donec ac odio
                tempor orci dapibus ultrices in iaculis nunc sed augue lacus viverra
                vitae congue eu consequat ac felis donec et odio pellentesque diam
                volutpat commodo sed egestas egestas fringilla phasellus faucibus
                scelerisque eleifend donec pretium vulputate sapien nec sagittis
                aliquam malesuada bibendum"""
            ),
        )

    def test_comment_7(
        self, test_file_with_comments: "list[tuple[str, str, str, str]]"
    ) -> None:
        """Extract the first comment."""
        comment = test_file_with_comments[7]
        assert comment == (
            "suspendisse ",
            "Randy Bartels",
            "2024-04-02T17:00:00Z",
            "Comment 7 with a long response",
        )

    def test_long_response(
        self, test_file_with_comments: "list[tuple[str, str, str, str]]"
    ) -> None:
        """Extract the first comment."""
        comment = test_file_with_comments[8]
        assert comment == (
            "suspendisse ",
            "Randy Bartels",
            "2024-04-02T17:00:00Z",
            par(
                """Long response: magna fringilla urna porttitor rhoncus dolor purus
                non enim praesent elementum facilisis leo vel fringilla est
                ullamcorper eget nulla facilisi etiam dignissim diam quis enim
                lobortis scelerisque fermentum dui faucibus in ornare quam viverra
                orci sagittis eu volutpat odio facilisis mauris\n\nsit amet massa
                vitae tortor condimentum lacinia quis vel eros donec ac odio tempor
                orci dapibus ultrices in iaculis nunc sed augue lacus viverra vitae
                congue eu consequat ac felis donec et odio pellentesque diam volutpat
                commodo sed egestas egestas fringilla phasellus faucibus scelerisque
                eleifend donec pretium vulputate sapien nec sagittis aliquam
                malesuada bibendum"""
            ),
        )

    def comment_8(
        self, test_file_with_comments: "list[tuple[str, str, str, str]]"
    ) -> None:
        """Extract the first comment."""
        comment = test_file_with_comments[9]
        assert comment == (
            "Magnis ",
            "Randy Bartels",
            "2024-04-02T17:04:00Z",
            "Comment 8 - marked Resolved",
        )

    def comment_in_a_table(
        self, test_file_with_comments: "list[tuple[str, str, str, str]]"
    ) -> None:
        """Extract the first comment."""
        comment = test_file_with_comments[10]
        assert comment == (
            "R1C1",
            "Randy Bartels",
            "2024-04-02T17:07:00Z",
            "Comment in a table",
        )

    def comment_on_a_picture(
        self, test_file_with_comments: "list[tuple[str, str, str, str]]"
    ) -> None:
        """Extract the first comment."""
        comment = test_file_with_comments[11]
        assert comment == (
            "",
            "Randy Bartels",
            "2024-04-02T17:08:00Z",
            "Comment on a picture",
        )


def test_no_comments() -> None:
    """Return an empty list when no comments are present."""
    pars = docx2python(RESOURCES / "apples_and_pears.docx")
    comments = pars.comments
    pars.close()
    assert comments == []
