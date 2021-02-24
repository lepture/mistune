Advanced Guide of Mistune
=========================


.. _renderers:

Use renderers
-------------

You can customize HTML output with your own renderers. Create a subclass
of ``mistune.HTMLRenderer``::


    class MyRenderer(mistune.HTMLRenderer):
        def codespan(self, text):
            if text.startswith('$') and text.endswith('$'):
                return '<span class="math">' + escape(text) + '</span>'
            return '<code>' + escape(text) + '</code>'

    # use customized renderer
    markdown = mistune.create_markdown(renderer=MyRenderer())
    print(markdown('hi `$a^2=4$`'))

Here is a a list of available renderer functions::

    # inline level
    text(self, text)
    link(self, link, text=None, title=None)
    image(self, src, alt="", title=None)
    emphasis(self, text)
    strong(self, text)
    codespan(self, text)
    linebreak(self)
    newline(self)
    inline_html(self, html)

    # block level
    paragraph(self, text)
    heading(self, text, level)
    thematic_break(self)
    block_text(self, text)
    block_code(self, code, info=None)
    block_quote(self, text)
    block_html(self, html)
    block_error(self, html)
    list(self, text, ordered, level, start=None)
    list_item(self, text, level)

    # provided by strikethrough plugin
    strikethrough(self, text)

    # provide by table plugin
    table(self, text)
    table_head(self, text)
    table_body(self, text)
    table_row(self, text)
    table_cell(self, text, align=None, is_head=False)

    # provided by footnotes plugin
    footnote_ref(self, key, index)
    footnotes(self, text)
    footnote_item(self, text, key, index)

    # Finalize rendered content (define output)
    finalize(self, data)


.. _plugins:

Create plugins
--------------

Mistune has some built-in plugins, you can take a look at the source code
in ``mistune/plugins`` to find out how to write a plugin. Let's take an
example for GitHub Wiki links: ``[[Page 2|Page 2]]``.

A mistune plugin usually looks like::

    # define regex for Wiki links
    WIKI_PATTERN = (
        r'\[\['                   # [[
        r'([\s\S]+?\|[\s\S]+?)'   # Page 2|Page 2
        r'\]\](?!\])'             # ]]
    )

    # define how to parse matched item
    def parse_wiki(inline, m, state):
        # ``inline`` is ``md.inline``, see below
        # ``m`` is matched regex item
        text = m.group(1)
        title, link = text.split('|')
        return 'wiki', link, title

    # define how to render HTML
    def render_html_wiki(link, title):
        return f'<a href="{link}">{title}</a>'

    def plugin_wiki(md):
        # this is an inline grammar, so we register wiki rule into md.inline
        md.inline.register_rule('wiki', WIKI_PATTERN, parse_wiki)

        # add wiki rule into active rules
        md.inline.rules.append('wiki')

        # add HTML renderer
        if md.renderer.NAME == 'html':
            md.renderer.register('wiki', render_html_wiki)

    # use this plugin
    markdown = mistune.create_markdown(plugins=[plugin_wiki])

Get more examples in ``mistune/plugins``.

.. _directives:

Write directives
----------------
