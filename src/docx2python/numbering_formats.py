"""Numbering formats for converted XML lists.

:author: Shay Hill
:created: 6/26/2019

I don't want to add non-ascii text to a potentially ascii-only file, so all bullets
are '--' and Roman numerals stop at 3999.

Doesn't capture formatting like 1.1.1 or b) or (ii). Only the six basic formats are
covered::

    -- bullet
    1  decimal
    a  lowerLetter
    A  upperLetter
    i  lowerRoman
    I  upperRoman
"""

from string import ascii_lowercase

# Subs to convert any number of i's to a proper Roman numeral
# fmt=off
ROMAN_SUBS = [
    ("iiiii", "v"),  # 1+1+1+1+1 -> 5
    ("vv", "x"),  # 5+5 -> 10
    ("xxxxx", "l"),  # 10+10+10+10 -> 50
    ("ll", "c"),  # 50+50 -> 100
    ("ccccc", "d"),  # 100+100+100+100+100 -> 500
    ("dd", "m"),  # 500+500 -> 1000
    ("iiii", "iv"),  # 1+1+1+1 -> 4
    ("viv", "ix"),  # 5+4 -> 9
    ("xxxx", "xl"),  # 10+10+10+10 -> 40
    ("lxl", "xc"),  # 50+40 -> 90
    ("cccc", "cd"),  # 100+100+100+100 -> 40
    ("dcd", "cm"),  # 500+400 -> 900
]
# fmt=on


def lower_letter(n: int) -> str:
    """Convert a positive integer to a string of letters representing base 26.

    :param n: any positive integer
    :return: the kind of "numbering" used for numbered lists and excel columns.
        (a, b, c ... aa, ab ...) Zero is undefined.
    :raise ValueError: if n is not a positive integer

        >>> lower_letter(1)
        'a'
        >>> lower_letter(26)
        'z'
        >>> lower_letter(27)
        'aa'
    """
    if n < 1:
        msg = f"0 and <1 are not defined for this numbering: {n}"
        raise ValueError(msg)
    result = ""
    while n:
        n, remainder = divmod(n - 1, 26)
        result = ascii_lowercase[remainder] + result
    return result


def upper_letter(n: int) -> str:
    """Get int as an upprecase letter.

    :param n: any positive integer
    :return: the kind of "numbering" used for numbered lists and excel columns.
    """
    return lower_letter(n).upper()


def lower_roman(n: int) -> str:
    """Convert a positive integer to a lowercase Roman numeral.

    :param n: any positive integer
    :return: Roman number equivalent of n
    :raise ValueError: if n is not a positive integer

        >>> lower_roman(1)
        'i'
        >>> lower_roman(9)
        'ix'
        >>> lower_roman(44)
        'xliv'

    Numbers greater than 3999 can be expressed with a bar over the number. The bar
    means "times 1000" (e.g., iv with a bar over it would be 4000).

    It'll never happen in this project, and I don't want to add non-ascii to what
    might be a pure ascii file, so this function will keep adding 'm' to as many
    thousand as you'd like.

        >>> lower_roman(10000)
        'mmmmmmmmmm'
    """
    if n < 1:
        msg = f"the Romans hadn't figured out {n}"
        raise ValueError(msg)
    result = "i" * n
    for pattern, replacement in ROMAN_SUBS:
        result = result.replace(pattern, replacement)
    return result


def upper_roman(n: int) -> str:
    """Get int as an uppercase Roman numeral.

    :param n: any positive integer
    :return: Roman number equivalent of n
    """
    return lower_roman(n).upper()


def decimal(n: int) -> str:
    """Get int as a decimal number string.

    :param n: any integer
    :return: string such that int(decimal(n)) == n
    """
    return str(n)


def bullet(_: int = 0) -> str:
    """Get the string we're using to replace bullets.

    :return: the string we're using to replace bullets.
    """
    return "--"
