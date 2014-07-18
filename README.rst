Mistune
=======

The fastest markdown parser in pure Python, inspired by marked_.

.. image:: https://travis-ci.org/lepture/mistune.png?branch=master
   :target: https://travis-ci.org/lepture/mistune
.. image:: https://coveralls.io/repos/lepture/mistune/badge.png?branch=master
   :target: https://coveralls.io/r/lepture/mistune


.. _marked: https://github.com/chjj/marked


Features
--------

* **Pure Python**. Tested in Python 2.6+, Python 3.3+ and PyPy.
* **Very Fast**. It is the fastest in all **pure Python** markdown parsers.
* **More Features**. Table, footnotes, autolink, fenced code etc.

View the `benchmark results <https://github.com/lepture/mistune/issues/1>`_.

Installation
------------

Installing mistune with pip::

    $ pip install mistune

If pip is not available, try easy_install::

    $ easy_install mistune

Cython Feature
~~~~~~~~~~~~~~

Mistune can be faster, if you compile with cython::

    $ pip install cython mistune


Basic Usage
-----------

A simple API that render a markdown formatted text::

    import mistune

    mistune.markdown('I am using **markdown**')
    # output: <p>I am using <strong>markdown</strong></p>

Mistune has all features by default. You don't have to configure anything.

Renderer
--------

Like misaka/sundown, you can influence the rendering by custom renderers.
All you need to do is subclassing a `Renderer` class.

Here is an example of code highlighting::

    import mistune
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name
    from pygments.formatters import HtmlFormatter

    class MyRenderer(mistune.Renderer):
        def block_code(self, code, lang):
            if not lang:
                return '\n<pre><code>%s</code></pre>\n' % \
                    mistune.escape(code)
            lexer = get_lexer_by_name(lang, stripall=True)
            formatter = HtmlFormatter()
            return highlight(code, lexer, formatter)

    renderer = MyRenderer()
    md = mistune.Markdown(renderer=renderer)
    print(md.render('Some Markdown text.'))


Block Level
~~~~~~~~~~~

Here is a list of block level renderer API::

    block_code(code, language=None)
    block_quote(text)
    block_html(html)
    header(text, level, raw=None)
    hrule()
    list(body, ordered=True)
    list_item(text)
    paragraph(text)
    table(header, body)
    table_row(content)
    table_cell(content, **flags)

The *flags* tells you whether it is header with ``flags['header']``. And it
also tells you the align with ``flags['align']``.


Span Level
~~~~~~~~~~

Here is a list of span level renderer API::

    autolink(link, is_email=False)
    codespan(text)
    double_emphasis(text)
    emphasis(text)
    image(src, title, alt_text)
    linebreak()
    link(link, title, content)
    raw_html(raw_html)
    strikethrough(text)
    text(text)


Options
-------

Here is a list of all options that will affect the rendering results::

    mistune.markdown(text, escape=True)

    md = mistune.Markdown(escape=True)
    md.render(text)

* **escape**: if set to *True*, all raw html tags will be escaped.
* **hard_wrap**: if set to *True*, it will has GFM line breaks feature.
* **use_xhtml**: if set to *True*, all tags will be in xhtml, for example: ``<hr />``.


Lexers
------

Sometimes you want to add your own rules to Markdown, such as GitHub Wiki
links. You can't archive this goal with renderers. You will need to deal
with the lexers, it would be a little difficult for the first time.

We will take an example for GitHub Wiki links: ``[[Page 2|Page 2]]``.
It is an inline grammar, which requires custom ``InlineGrammar`` and
``InlineLexer``::

    import copy

    class MyInlineGrammar(InlineGrammar):
        # it would take a while for creating the right regex
        wiki_link = re.compile(
            r'\[\['                   # [[
            r'([\s\S]+?\|[\s\S]+?)'   # Page 2|Page 2
            r'\]\]'(?!\])'            # ]]
        )


    class MyInlineLexer(InlineLexer):
        default_features = copy.copy(InlineLexer.default_features)

        # Add wiki_link parser to default features
        # you can insert it any place you like
        default_features.insert(3, 'wiki_link')

        def __init__(self, renderer, rules=None, **kwargs):
            if rules is None:
                # use the inline grammar
                rules = MyInlineLexer()

            super(MyInlineLexer, self).__init__(renderer, rules, **kwargs)

        def output_wiki_link(self, m):
            text = m.group(1)
            alt, link = text.split('|')
            # you can create an custom render
            # you can also return the html if you like
            return self.renderer.wiki_link(alt, link)

You should pass the inline lexer to ``Markdown`` parser::

    markdown = Markdown(inline=MyInlineLexer())
    markdown('[[Link Text|Wiki Link]]')

It is the same with block level lexer. It would take a while to understand
the whole mechanism. But you won't do the trick a lot.
