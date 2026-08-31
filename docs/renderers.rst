.. _renderers:

Renderers
=========

Mistune has several built-in renderers, including:

- :class:`mistune.renderers.html.HTMLRenderer`
- :class:`mistune.renderers.markdown.MarkdownRenderer`
- :class:`mistune.renderers.rst.RSTRenderer`

You can add more renderers.

Customize HTMLRenderer
----------------------

Create a renderer subclass to customize HTML output. This example adds
inline math syntax:

.. code::

    `$a^2=4$`

To render this syntax, create a subclass of ``mistune.HTMLRenderer``:

.. code-block:: python

    from mistune import HTMLRenderer

    class MyRenderer(HTMLRenderer):
        def codespan(self, text):
            if text.startswith('$') and text.endswith('$'):
                return '<span class="math">' + escape(text) + '</span>'
            return '<code>' + escape(text) + '</code>'

    # use the custom renderer
    markdown = mistune.create_markdown(renderer=MyRenderer())
    print(markdown('hi `$a^2=4$`'))

Available methods
~~~~~~~~~~~~~~~~~

This list shows the renderer methods for ``HTMLRenderer``. It also includes
methods from plugins:

.. code-block::

    # inline level
    text(self, text)
    link(self, text, url, title=None)
    image(self, alt, url, title=None)
    emphasis(self, text)
    strong(self, text)
    codespan(self, text)
    linebreak(self)
    softbreak(self)
    inline_html(self, html)

    # block level
    paragraph(self, text)
    heading(self, text, level, **attrs)
    blank_line(self)
    thematic_break(self)
    block_text(self, text)
    block_code(self, code, info=None)
    block_quote(self, text)
    block_html(self, html)
    block_error(self, html)
    list(self, text, ordered, **attrs)
    list_item(self, text, **attrs)

    # provided by strikethrough plugin
    strikethrough(self, text)

    # provided by mark plugin
    mark(self, text)

    # provided by insert plugin
    insert(self, text)

    # provided by subscript plugin
    subscript(self, text)

    # provided by abbr plugin
    abbr(self, text, title)

    # provided by ruby plugin
    ruby(self, text, rt)

    # provided by task_lists plugin
    task_list_item(self, text, checked=False, **attrs)

    # provided by table plugin
    table(self, text)
    table_head(self, text)
    table_body(self, text)
    table_row(self, text)
    table_cell(self, text, align=None, head=False)

    # provided by footnotes plugin
    footnote_ref(self, key, index)
    footnotes(self, text)
    footnote_item(self, text, key, index)

    # provided by def_list plugin
    def_list(self, text)
    def_list_head(self, text)
    def_list_item(self, text)

    # provided by math plugin
    block_math(self, text)
    inline_math(self, text)


reStructuredText Renderer
-------------------------

Use ``RSTRenderer`` to convert Markdown text to reStructuredText.

.. code-block:: python

    from mistune.renderers.rst import RSTRenderer

    convert_rst = mistune.create_markdown(renderer=RSTRenderer())
    convert_rst(your_markdown_text)


Markdown Renderer
-----------------

Use ``MarkdownRenderer`` to reformat Markdown text.

.. code-block:: python

    from mistune.renderers.markdown import MarkdownRenderer

    format_markdown = mistune.create_markdown(renderer=MarkdownRenderer())
    format_markdown(your_markdown_text)

With plugins
~~~~~~~~~~~~

The default ``MarkdownRenderer`` renders only basic Markdown syntax.
If you use plugins, add render methods for the plugin tokens. This example
adds the :ref:`strikethrough` plugin:

.. code-block:: python

    from mistune.renderers.markdown import MarkdownRenderer

    class MyRenderer(MarkdownRenderer):
        def strikethrough(self, token, state):
            return '~~' + self.render_children(token, state) + '~~'

    format_markdown = mistune.create_markdown(renderer=MarkdownRenderer(), plugins=['strikethrough'])
    format_markdown(your_markdown_text)

Default methods
~~~~~~~~~~~~~~~

This list shows the default renderer methods for ``MarkdownRenderer``:

.. code-block::

    # inline level
    text(self, token, state)
    link(self, token, state)
    image(self, token, state)
    emphasis(self, token, state)
    strong(self, token, state)
    codespan(self, token, state)
    linebreak(self, token, state)
    softbreak(self, token, state)
    inline_html(self, token, state)

    # block level
    paragraph(self, token, state)
    heading(self, token, state)
    blank_line(self, token, state)
    thematic_break(self, token, state)
    block_text(self, token, state)
    block_code(self, token, state)
    block_quote(self, token, state)
    block_html(self, token, state)
    block_error(self, token, state)
    list(self, token, state)
