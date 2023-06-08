How to Use Mistune
==================

Mistune is super easy to use. Here is how you can convert Markdown formatted
text into HTML::

    import mistune

    mistune.html(YOUR_MARKDOWN_TEXT)

The ``.html()`` methods has enabled all the features you might want
by default:

* No escape of HTML tags
* With **strikethrough** plugin
* With **table** plugin
* With **footnote** plugin


Customize Mistune
-----------------

Mistune provides a function to create Markdown instance easily::

    import mistune

    markdown = mistune.create_markdown()

This method will create a "escaped" Markdown instance without any plugins,
which means::

    markdown('<div>hello</div>')
    # ==>
    '<p>&lt;div&gt;hello&lt;/div&gt;</p>'

Non escaped version::

    markdown = mistune.create_markdown(escape=False)
    markdown('<div>hello</div>')
    # ==>
    '<div>hello</div>'

Adding plugins::

    markdown = mistune.create_markdown()
    markdown('~~s~~')
    # ==>
    '<p>~~s~~</p>'

    markdown = mistune.create_markdown(plugins=['strikethrough'])
    markdown('~~s~~')
    # ==>
    '<p><del>s</del></p>'

Find out what plugins mistune has built-in in :ref:`plugins` sections.


Customize Renderer
------------------

Mistune supports renderer feature which enables developers to customize
the output. For instance, to add code syntax highlight::

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

In this way, we can use Pygments to highlight the fenced code. Learn more
at :ref:`renderers`.


Abstract syntax tree
--------------------

Mistune can produce AST by default without any renderer::

    markdown = mistune.create_markdown(renderer=None)

This ``markdown`` function will generate a list of tokens instead of HTML::

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

It is also possible to pass ``renderer='ast'`` to create the markdown instance::

    markdown = mistune.create_markdown(renderer='ast')
