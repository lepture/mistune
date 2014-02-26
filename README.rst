Mistune (WIP)
=============

Yet another markdown parser, inspired by marked_ in JavaScript.

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
        def block_code(code, lang):
            if not lang:
                return '\n<pre><code>%s</code></pre>\n' % \
                    mistune.escape(code)
            lexer = get_lexer_by_name(lang, stripall=True)
            formatter = HtmlFormatter()
            return highlight(text, lexer, formatter)

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


Options
-------

Here is a list of all options that will affect the rendering results::

    mistune.markdown(text, escape=True)

    md = mistune.Markdown(escape=True)
    md.render(text)

* **escape**: if set to *True*, all raw html tags will be escaped.
* **use_xhtml**: if set to *True*, all tags will be in xhtml, for example: ``<hr />``.
