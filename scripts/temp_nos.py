"""Print some consecutive letter strings to help create a test docx

:author: Shay Hill
:created: 11/12/2021
"""

from string import ascii_lowercase

for a in ascii_lowercase:
    for b in ascii_lowercase:
        for c in ascii_lowercase:
            print(f"{a}{b}{c}", end=" ")
