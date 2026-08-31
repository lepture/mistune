How to Use Mistune
==================

Use ``mistune.html()`` to convert Markdown text to HTML::

    import mistune

    mistune.html(YOUR_MARKDOWN_TEXT)

The ``mistune.html()`` function enables these features by default:

* It does not escape HTML tags.
* It uses the **strikethrough** plugin.
* It uses the **table** plugin.
* It uses the **footnote** plugin.


Customize Mistune
-----------------

Use ``create_markdown()`` to create a Markdown instance::

    import mistune

    markdown = mistune.create_markdown()

This function creates an escaped Markdown instance with no plugins::

    markdown('<div>hello</div>')
    # ==>
    '<p>&lt;div&gt;hello&lt;/div&gt;</p>'

Create a non-escaped instance::

    markdown = mistune.create_markdown(escape=False)
    markdown('<div>hello</div>')
    # ==>
    '<div>hello</div>'

Add plugins::

    markdown = mistune.create_markdown()
    markdown('~~s~~')
    # ==>
    '<p>~~s~~</p>'

    markdown = mistune.create_markdown(plugins=['strikethrough'])
    markdown('~~s~~')
    # ==>
    '<p><del>s</del></p>'

For the list of built-in plugins, see :ref:`plugins`.


Customize Renderer
------------------

Mistune lets you customize output with renderers. For example, this
renderer adds syntax highlighting to fenced code blocks::

    import mistune
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name
    from pygments.formatters import html


    class HighlightRenderer(mistune.HTMLRenderer):
        def block_code(self, code, info=None):
            if info:
                lexer = get_lexer_by_name(info, stripall=True)
                formatter = html.HtmlFormatter()
                return highlight(code, lexer, formatter)
            return '<pre><code>' + mistune.escape(code) + '</code></pre>'

    markdown = mistune.create_markdown(renderer=HighlightRenderer())

    print(markdown('```python\nassert 1 == 1\n```'))

This renderer uses Pygments to highlight fenced code blocks. For more
renderer details, see :ref:`renderers`.


.. _abstract-syntax-tree:

Abstract syntax tree
--------------------

Mistune can produce AST tokens without a renderer::

    markdown = mistune.create_markdown(renderer=None)

This ``markdown`` function returns a list of tokens instead of HTML::

    text = 'hello **world**'
    markdown(text)
    # ==>
    [
        {
            'type': 'paragraph',
            'children': [
                {'type': 'text', 'raw': 'hello '},
                {'type': 'strong', 'children': [{'type': 'text', 'raw': 'world'}]}
            ]
        }
    ]

You can also pass ``renderer='ast'`` when you create the Markdown instance::

    markdown = mistune.create_markdown(renderer='ast')

For details on how to parse these tokens, see :ref:`parsing-ast-tokens`.
