API Reference
=============

.. module:: mistune

Basic
-----

.. function:: html(text)

    :param text: markdown formatted text

    Turn markdown text into HTML without escaping. For instance::

        text = '**hello** <span>world</span>'
        mistune.html(text)

        # =>
        '<p><strong>hello</strong> <span>world</span></p>'

.. autofunction:: create_markdown

Utilities
---------

.. autofunction:: escape

.. autofunction:: escape_url

.. autofunction:: safe_entity

.. autofunction:: unikey

Advanced
--------

.. autoclass:: Markdown

.. autoclass:: BlockState

.. autoclass:: InlineState
