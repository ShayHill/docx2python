.. _iterators:

iterators module
================

.. automodule:: iterators
   :undoc-members:
   :show-inheritance:

This allows for simple recipes like::

    from docx2python.iterators import enum_cells

    def remove_empty_paragraphs(tables):
        for (i, j, k), cell in enum_cells(tables):
            tables[i][j][k] = [x for x in cell if x]


>>> tables = [[[['a', 'b'], ['a', '', 'd', '']]]]
>>> remove_empty_paragraphs(tables)
    [[[['a', 'b'], ['a', 'd']]]]

::

    from docx2python.iterators import enum_at_depth

    def html_map(tables) -> str:
        """Create an HTML map of document contents.

        Render this in a browser to visually search for data.
        """
        tables = self.document

        # prepend index tuple to each paragraph
        for (i, j, k, l), paragraph in enum_at_depth(tables, 4):
            tables[i][j][k][l] = " ".join([str((i, j, k, l)), paragraph])

        # wrap each paragraph in <pre> tags
        for (i, j, k), cell in enum_at_depth(tables, 3):
            tables[i][j][k] = "".join([f"<pre>{x}</pre>" for x in cell])

        # wrap each cell in <td> tags
        for (i, j), row in enum_at_depth(tables, 2):
            tables[i][j] = "".join([f"<td>{x}</td>" for x in row])

        # wrap each row in <tr> tags
        for (i,), table in enum_at_depth(tables, 1):
            tables[i] = "".join(f"<tr>{x}</tr>" for x in table)

        # wrap each table in <table> tags
        tables = "".join([f'<table border="1">{x}</table>' for x in tables])

        return ["<html><body>"] + tables + ["</body></html>"]

>>> tables = [[[['a', 'b'], ['a', 'd']]]]
>>> html_toc(tables)
<html>
    <body>
        <table border="1">
            <tr>
                <td>
                    '(0, 0, 0, 0) a'
                    '(0, 0, 0, 1) b'
                </td>
                <td>
                    '(0, 0, 1, 0) a'
                    '(0, 0, 1, 1) d'
                </td>
            </tr>
        </table>
    </body>
</html>

.. autofunction:: iterators.enum_at_depth
.. autofunction:: iterators.iter_at_depth
.. autofunction:: iterators.enum_tables
.. autofunction:: iterators.enum_rows
.. autofunction:: iterators.enum_cells
.. autofunction:: iterators.enum_paragraphs
.. autofunction:: iterators.iter_tables
.. autofunction:: iterators.iter_rows
.. autofunction:: iterators.iter_cells
.. autofunction:: iterators.iter_paragraphs

