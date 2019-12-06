API Reference
=============

.. module:: mistune


.. function:: html(text)

    :param text: markdown formatted text

    Turn markdown text into HTML without escaping. For instance::

        text = '**hello** <span>world</span>'
        mistune.html(text)

        # =>
        '<p><strong>hello</strong> <span>world</span></p>'

.. autofunction:: create_markdown
