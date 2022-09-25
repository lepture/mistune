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

    # provide by table plugin
    table(self, text)
    table_head(self, text)
    table_body(self, text)
    table_row(self, text)
    table_cell(self, text, align=None, head=False)

    # provided by footnotes plugin
    footnote_ref(self, key, index)
    footnotes(self, text)
    footnote_item(self, text, key, index)

    # provide by def_list plugin
    def_list(self, text)
    def_list_head(self, text)
    def_list_item(self, text)

    # provide by math plugin
    block_math(self, text)
    inline_math(self, text)


.. _plugins:

Create plugins
--------------

Mistune has some built-in plugins, you can take a look at the source code
in ``mistune/plugins`` to find out how to write a plugin.

.. _directives:

Write directives
----------------

Mistune has some built-in directives that have been presented in
the directives part of the documentation. These are defined in the
``mistune/directives``, and these can help writing a new directive.

Let's try to write a "spoiler" directive, which takes a hint::

    from mistune.directives import Directive, parse_options

    class Spoiler(Directive):
        def parse(self, block, m, state):
            if options:
                return {
                    'type': 'block_error',
                    'raw': 'Spoiler has no options'
                }

            hint = m.group('value')
            attrs = {'hint': hint}
            children = parse_children(block, m, state)
            return {
                'type': 'spoiler',
                'children': children,
                'attrs': attrs,
            }

        def __call__(self, md):
            self.register_directive(md, 'spoiler')

            if md.renderer.NAME == 'html':
                md.renderer.register('spoiler', render_html_spoiler)


    def render_html_spoiler(text, name, hint="Spoiler"):
        html = '<section class="spoiler">\n'
        html += '<p class="spoiler-hint">' + hint + '</p>\n'
        if text:
            html += '<div class="spoiler-text">' + text + '</div>\n'
        return html + '</section>\n'


Some design functionalities would be required to make the
HTML rendering actually output a spoiler block.
