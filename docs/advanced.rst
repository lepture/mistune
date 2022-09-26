Advanced Guide
==============

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

Mistune has many built-in plugins, you can take a look at the source code
in ``mistune/plugins`` to find out how to write a plugin. In this documentation,
I'll guide you with an example, let's take a look at the math plugin
(located at ``mistune/plugins/math.py``):

.. code-block:: python

    def math(md):
        md.block.register('block_math', BLOCK_MATH_PATTERN, parse_block_math, before='list')
        md.inline.register('inline_math', INLINE_MATH_PATTERN, parse_inline_math, before='link')
        if md.renderer and md.renderer.NAME == 'html':
            md.renderer.register('block_math', render_block_math)
            md.renderer.register('inline_math', render_inline_math)

The parameter ``md`` is the instance of :class:`Markdown`. In our example, we have registered
a block level math plugin and an inline level math plugin.

Block level plugin
~~~~~~~~~~~~~~~~~~

Function ``md.block.register`` will register a block level plugin. In the math example:

.. code-block:: text

    $$
    \operatorname{ker} f=\{g\in G:f(g)=e_{H}\}{\mbox{.}}
    $$

This is how a block level math syntax looks like. Our ``BLOCK_MATH_PATTERN`` is:

.. code-block:: python

    # block level pattern MUST startswith ^
    BLOCK_MATH_PATTERN = r'^ {0,3}\$\$[ \t]*\n(?P<math_text>.+?)\n\$\$[ \t]*$'

    # regex represents:
    BLOCK_MATH_PATTERN = (
      r'^ {0,3}'  # line can startswith 0~3 spaces just like other block elements defined in commonmark
      r'\$\$'  # followed by $$
      r'[ \t]*\n'  # this line can contain extra spaces and tabs
      r'(?P<math_text>.+?)'  # this is the math content, MUST use named group
      r'\n\$\$[ \t]*$'  # endswith $$ + extra spaces and tabs
    )

    # if you want to make the math pattern more strictly, it could be like:
    BLOCK_MATH_PATTERN = r'^\$\$\n(?P<math_text>.+?)\n\$\$$'

Then the block parsing function:

.. code-block:: python

    def parse_block_math(block, m, state):
        text = m.group('math_text')
        # use ``state.append_token`` to save parsed block math token
        state.append_token({'type': 'block_math', 'raw': text})
        # return the end position of parsed text
        # since python doesn't count ``$``, we have to +1
        # if the pattern is not ended with `$`, we can't +1
        return m.end() + 1

The ``token`` MUST contain ``type``, others are optional. Here are some examples:

.. code-block:: python

    {'type': 'thematic_break'}  # <hr>
    {'type': 'paragraph', 'text': text}
    {'type': 'block_code', 'raw': code}
    {'type': 'heading', 'text': text, 'attrs': {'level': level}}

- **text**: inline parser will parse text
- **raw**: inline parser WILL NOT parse the content
- **attrs**: extra information saved here, renderer will use attrs

Inline level plugin
~~~~~~~~~~~~~~~~~~~

Function ``md.inline.register`` will register an inline level plugin. In the math example:

.. code-block:: text

    function $f$

This is how an inline level math syntax looks like. Our ``INLINE_MATH_PATTERN`` is:

.. code-block:: python

    INLINE_MATH_PATTERN = r'\$(?!\s)(?P<math_text>.+?)(?!\s)\$'

    # regex represents:
    INLINE_MATH_PATTERN = (
      r'\$'  # startswith $
      r'(?!\s)'  # not whitespace
      r'(?P<math_text>.+?)'  # content between `$`, MUST use named group
      r'(?!\s)'  # not whitespace
      r'\$'  # endswith $
    )

Then the inline parsing function:

.. code-block:: python

    def parse_inline_math(inline, m, state):
        text = m.group('math_text')
        # use ``state.append_token`` to save parsed inline math token
        state.append_token({'type': 'inline_math', 'raw': text})
        # return the end position of parsed text
        return m.end()

The inline token value looks the same with block token. Available keys:
``type``, ``raw``, ``text``, ``attrs``.

Plugin renderers
~~~~~~~~~~~~~~~~

It is suggested to add default HTML renderers for your plugin. A renderer function
looks like:

.. code-block:: python

    def render_hr(renderer):
        # token with only type, like:
        # {'type': 'hr'}
        return '<hr>'

    def render_math(renderer, text):
        # token with type and (text or raw), e.g.:
        # {'type': 'block_math', 'raw': 'a^b'}
        return '<div class="math">$$' + text + '$$</div>'

    def render_link(renderer, text, **attrs):
        # token with type, text or raw, and attrs
        href = attrs['href']
        return f'<a href="{href}">{text}</a>'

If current markdown instance is using HTML renderer, developers can register
the plugin renderer for converting markdown to HTML.

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
