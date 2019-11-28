How to Use Mistune
==================

Mistune is super easy to use. Here is how you can convert Markdown formatted
text into HTML::

    import mistune

    mistune.html(YOUR_MARKDOWN_TEXT)

The ``.html()`` methods has enabled all the features you might want
by default:

* No escape of HTML tags
* With **strikethough** plugin
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

    markdown = mistune.create_markdown(plugins=['strikethough'])
    markdown('~~s~~')
    # ==>
    '<p><del>s</del></p>'

Find out what plugins mistune has built-in in :ref:`plugins` sections.

Customize Renderer
------------------

Mistune supports renderer feature which enables developers to customize
the output.
