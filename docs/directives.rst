.. _directives:

Directives
==========

A directive is an explicit markup block. It is extensible. Mistune v3
supports two directive styles:

1. reStructuredText style
2. fenced style

.. versionchanged:: 3.0

    Fenced-style directives were added in 3.0. Mistune v3 supports
    multiple directive styles. Thus, do not add each directive directly
    to the ``plugins`` parameter of ``mistune.create_markdown``. Wrap
    each directive in a directive style object instead::

        import mistune
        from mistune.directives import FencedDirective, RSTDirective
        from mistune.directives import Admonition, TableOfContents

        markdown = mistune.create_markdown(plugins=[
            'math',
            'footnotes',
            # ...
            FencedDirective([
                Admonition(),
                TableOfContents(),
            ]),
        ])

        markdown = mistune.create_markdown(plugins=[
            'math',
            'footnotes',
            # ...
            RSTDirective([
                Admonition(),
                TableOfContents(),
            ]),
        ])

A **reStructuredText** directive uses syntax from reStructuredText_:

.. code-block:: text

    .. directive-type:: title
       :option-key: option value
       :option-key: option value

       content text here


A **fenced** directive looks like a fenced code block. It uses syntax
from `markdown-it-docutils`_:

.. code-block:: text

    ```{directive-type} title
    :option-key: option value
    :option-key: option value

    content text here
    ```

.. _reStructuredText: https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#directives

.. _`markdown-it-docutils`: https://executablebooks.github.io/markdown-it-docutils/


Choose the directive style that is best for your project.

Admonitions
-----------

The reStructuredText style syntax:

.. code-block:: text

    .. warning::

       You are looking at the **dev** documentation. Check out our
       [stable](/stable/) documentation instead.

The fenced style syntax:

.. code-block:: text

    ```{warning}
    You are looking at the **dev** documentation. Check out our
    [stable](/stable/) documentation instead.
    ```

Admonitions support these ``directive-name`` values:

.. code-block:: text

    attention  caution  danger  error
    hint  important  note  tip  warning

To enable admonitions::

    import mistune
    from mistune.directives import Admonition

    markdown = mistune.create_markdown(
        plugins=[
            ...
            RSTDirective([Admonition()]),
            # FencedDirective([Admonition()]),
        ]
    )


Table of Contents
-----------------

.. code-block:: text

    .. toc:: Table of Contents
       :max-level: 3

The TOC plugin is a directive. It adds a table of contents to the
document. This example puts the TOC before the headings:

.. code-block:: text

   Here is the first paragraph, and we put TOC below.

   .. toc::

   # H1 title

   ## H2 title

   # H1 title

The rendered HTML contains the TOC at the ``.. toc::`` position. To enable
the TOC plugin::

    import mistune
    from mistune.directives import RSTDirective, TableOfContents

    markdown = mistune.create_markdown(
        plugins=[
            # ...
            RSTDirective([TableOfContents()]),
        ]
    )

Include
-------

.. code-block:: text

    .. include:: hello.md

The ``include`` plugin embeds content from other files. Use it for
documentation generators.


Image
-----

.. code-block:: text

    ```{image} https://domain/path.png
    :alt: alt text
    :width: 800
    :height: 500
    ```

Figure
------

.. code-block:: text

    ```{figure} https://domain/path.png
    :alt: alt text
    :width: 800
    :height: 500
    ```
