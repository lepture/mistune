API Reference
=============

Here are the list of API reference; it might be helpful for developers.

.. module:: mistune

Basic
-----

.. function:: html(text: str)

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
    :inherited-members:

.. autoclass:: InlineState
    :inherited-members:

.. autoclass:: BlockParser
    :inherited-members: register

.. autoclass:: InlineParser
    :inherited-members: register

Plugins
-------

.. module:: mistune.plugins.footnotes

.. autofunction:: footnotes

.. module:: mistune.plugins.task_lists

.. autofunction:: task_lists

.. module:: mistune.plugins.abbr

.. autofunction:: abbr

.. module:: mistune.plugins.def_list

.. autofunction:: def_list

.. module:: mistune.plugins.table

.. autofunction:: table

.. autofunction:: table_in_quote

.. autofunction:: table_in_list

.. module:: mistune.plugins.math

.. autofunction:: math

.. autofunction:: math_in_quote

.. autofunction:: math_in_list

.. module:: mistune.plugins.ruby

.. autofunction:: ruby

.. module:: mistune.plugins.formatting

.. autofunction:: strikethrough

.. autofunction:: mark

.. autofunction:: insert

.. autofunction:: superscript

.. autofunction:: subscript

.. module:: mistune.plugins.spoiler

.. autofunction:: spoiler

Renderers
---------

.. module:: mistune.renderers.html

.. autoclass:: HTMLRenderer

.. module:: mistune.renderers.markdown

.. autoclass:: MarkdownRenderer

.. module:: mistune.renderers.rst

.. autoclass:: RSTRenderer

TOC hook
--------

.. module:: mistune.toc

.. autofunction:: add_toc_hook

.. autofunction:: render_toc_ul


Directives
----------

.. module:: mistune.directives

.. autoclass:: RSTDirective

.. autoclass:: FencedDirective
