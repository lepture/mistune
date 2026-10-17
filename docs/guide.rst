How to Use Mistune
==================

Create a reusable parser to convert untrusted Markdown text to HTML safely::

    import mistune

    markdown = mistune.create_markdown()
    markdown(YOUR_MARKDOWN_TEXT)

``create_markdown()`` escapes raw HTML and rejects unsafe URL schemes by
default. See :doc:`security` for the complete trust model.

Legacy convenience parser
-------------------------

The ``mistune.html()`` compatibility helper enables these features by default:

* It does not escape HTML tags.
* It uses the **strikethrough** plugin.
* It uses the **table** plugin.
* It uses the **footnote** plugin.

Use it only for trusted Markdown or when an external HTML sanitizer processes
the result::

    mistune.html(TRUSTED_MARKDOWN_TEXT)


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

Per-document renderer context
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use ``state.env`` to pass context for one document. The HTML rendering methods
receive text and token attributes, rather than the state itself. Override
``render_token`` to read the context before delegating to the HTML renderer.
For example, this renderer prefixes image URLs for each document::

    class ImagePrefixRenderer(mistune.HTMLRenderer):
        def render_token(self, token, state):
            if token['type'] == 'image':
                attrs = dict(token['attrs'])
                attrs['url'] = state.env.get('image_prefix', '') + attrs['url']
                token = dict(token, attrs=attrs)
            return super().render_token(token, state)

    markdown = mistune.create_markdown(renderer=ImagePrefixRenderer())
    state = markdown.block.state_cls()
    state.env['image_prefix'] = '/assets/'
    html, state = markdown.parse('![Logo](logo.png)', state=state)
    print(html.strip())
    # <p><img src="/assets/logo.png" alt="Logo" /></p>

Create a fresh state for each document. This keeps the context out of mutable
renderer attributes. Copying the image token and its attributes also leaves
the original parsed URL intact. Delegating to ``HTMLRenderer`` retains its
normal escaping and URL-scheme checks.


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
