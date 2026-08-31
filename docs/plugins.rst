.. _plugins:

Built-in Plugins
================

.. meta::
    :description: List of Mistune built-in plugins, their syntax and how to enable them.

Mistune includes many built-in plugins, including common markup extensions.

.. note::

    Mistune keeps the historical ``speedup`` plugin only for compatibility.
    The core parsers now include its paragraph and inline text fast paths.
    Thus, Mistune accepts ``plugins=['speedup']`` but ignores it.

.. _strikethrough:

strikethrough
-------------

.. code-block:: text

    ~~here is the content~~

``mistune.html()`` enables the strikethrough plugin by default. To create
a Markdown instance with this plugin::

    markdown = mistune.create_markdown(plugins=['strikethrough'])

You can also pass the plugin function directly::

    from mistune.plugins.formatting import strikethrough

    renderer = mistune.HTMLRenderer()
    markdown = mistune.Markdown(renderer, plugins=[strikethrough])


footnotes
---------

.. code-block:: text

    content in paragraph with footnote[^1] markup.

    [^1]: footnote explain


``mistune.html()`` enables the footnotes plugin by default. To create
a Markdown instance with this plugin::

    markdown = mistune.create_markdown(plugins=['footnotes'])

You can also pass the plugin function directly::

    from mistune.plugins.footnotes import footnotes

    renderer = mistune.HTMLRenderer()
    markdown = mistune.Markdown(renderer, plugins=[footnotes])


table
-----

Simple formatted table:

.. code-block:: text

    First Header  | Second Header
    ------------- | -------------
    Content Cell  | Content Cell
    Content Cell  | Content Cell
    
Complex formatted table:

.. code-block:: text

    | First Header  | Second Header |
    | ------------- | ------------- |
    | Content Cell  | Content Cell  |
    | Content Cell  | Content Cell  |

Align formatted table:

.. code-block:: text

     Left Header |  Center Header  | Right Header
    :----------- | :-------------: | ------------:
     Content Cell |  Content Cell   | Content Cell


    | Left Header |  Center Header  | Right Header  |
    | :---------- | :-------------: | ------------: |
    | Content Cell |  Content Cell   | Content Cell  |

``mistune.html()`` enables the table plugin by default. To create
a Markdown instance with this plugin::

    markdown = mistune.create_markdown(plugins=['table'])

You can also pass the plugin function directly::

    from mistune.plugins.table import table

    renderer = mistune.HTMLRenderer()
    markdown = mistune.Markdown(renderer, plugins=[table])


url
---

The URL plugin creates links from raw URLs:

.. code-block:: text

    For instance, https://typlog.com/

This input produces:

.. code-block:: html

    <p>For instance, <a href="https://typlog.com/">https://typlog.com/</a></p>

``mistune.html()`` does not enable this plugin by default. Mistune keeps
raw URLs explicit. We suggest that writers use this link syntax:

.. code-block:: text

    <https://typlog.com/>

To enable the **url** plugin with your Markdown instance::

    markdown = mistune.create_markdown(plugins=['url'])

You can also pass the plugin function directly::

    from mistune.plugins.url import url

    renderer = mistune.HTMLRenderer()
    markdown = mistune.Markdown(renderer, plugins=[url])

task_lists
----------

The task lists plugin creates GitHub-style task list items:

.. code-block:: text

    - [x] item 1
    - [ ] item 2

This input produces:

.. code-block:: html

    <ul>
    <li class="task-list-item"><input class="task-list-item-checkbox" type="checkbox" disabled checked/>item 1</li>
    <li class="task-list-item"><input class="task-list-item-checkbox" type="checkbox" disabled/>item 2</li>
    </ul>


``mistune.html()`` does not enable this plugin by default. To enable
the **task_lists** plugin with your Markdown instance::

    markdown = mistune.create_markdown(plugins=['task_lists'])

You can also pass the plugin function directly::

    from mistune.plugins.task_lists import task_lists

    renderer = mistune.HTMLRenderer()
    markdown = mistune.Markdown(renderer, plugins=[task_lists])

def_list
--------

The def_list plugin creates HTML definition lists:

.. code-block:: text

    First term
    : First definition
    : Second definition
    
    Second term
    : Third definition
    
This input produces:

.. code-block:: html

    <dl>
    <dt>First term</dt>
    <dd>First definition</dd>
    <dd>Second definition</dd>
    <dt>Second term</dt>
    <dd>Third definition</dd>
    </dl>


``mistune.html()`` does not enable this plugin by default. To enable
the **def_list** plugin with your Markdown instance::

    markdown = mistune.create_markdown(plugins=['def_list'])

You can also pass the plugin function directly::

    from mistune.plugins.def_list import def_list

    renderer = mistune.HTMLRenderer()
    markdown = mistune.Markdown(renderer, plugins=[def_list])

abbr
----

The abbr plugin creates abbreviations:

.. code-block:: text

    The HTML specification
    is maintained by the W3C.

    *[HTML]: Hyper Text Markup Language
    *[W3C]: World Wide Web Consortium

This input produces:

.. code-block:: html

    The <abbr title="Hyper Text Markup Language">HTML</abbr> specification
    is maintained by the <abbr title="World Wide Web Consortium">W3C</abbr>.

``mistune.html()`` does not enable this plugin by default. To enable
the **abbr** plugin with your Markdown instance::

    markdown = mistune.create_markdown(plugins=['abbr'])

You can also pass the plugin function directly::

    from mistune.plugins.abbr import abbr

    renderer = mistune.HTMLRenderer()
    markdown = mistune.Markdown(renderer, plugins=[abbr])


mark
----

The mark plugin adds ``<mark>`` tags. To mark text, surround it with ``==``:

.. code-block:: text

    ==mark me== ==mark with\=\=equal==

This input produces:

.. code-block:: html

    <mark>mark me</mark> <mark>mark with==equal</mark>

``mistune.html()`` does not enable this plugin by default. To enable
the **mark** plugin with your Markdown instance::

    markdown = mistune.create_markdown(plugins=['mark'])

You can also pass the plugin function directly::

    from mistune.plugins.formatting import mark

    renderer = mistune.HTMLRenderer()
    markdown = mistune.Markdown(renderer, plugins=[mark])


insert
------

The insert plugin adds ``<ins>`` tags. To insert text, surround it with ``^^``:

.. code-block:: text

    ^^insert me^^ ^^insert\^\^me^^

This input produces:

.. code-block:: html

    <ins>insert me</ins> <ins>insert^^me</ins>

``mistune.html()`` does not enable this plugin by default. To enable
the **insert** plugin with your Markdown instance::

    markdown = mistune.create_markdown(plugins=['insert'])

You can also pass the plugin function directly::

    from mistune.plugins.formatting import insert

    renderer = mistune.HTMLRenderer()
    markdown = mistune.Markdown(renderer, plugins=[insert])

superscript
-----------

The superscript plugin adds ``<sup>`` tags. The syntax is:

.. code-block:: text

    Hello^superscript^

This input produces:

.. code-block:: html

    <p>Hello<sup>superscript</sup></p>

``mistune.html()`` does not enable this plugin by default. To enable
the **superscript** plugin with your Markdown instance::

    markdown = mistune.create_markdown(plugins=['superscript'])

You can also pass the plugin function directly::

    from mistune.plugins.formatting import superscript

    renderer = mistune.HTMLRenderer()
    markdown = mistune.Markdown(renderer, plugins=[superscript])

subscript
---------

The subscript plugin adds ``<sub>`` tags. The syntax is:

.. code-block:: text

    Hello~subscript~

    CH~3~CH~2~OH

This input produces:

.. code-block:: html

    <p>Hello<sub>subscript</sub></p>
    <p>CH<sub>3</sub>CH<sub>2</sub>OH</p>

``mistune.html()`` does not enable this plugin by default. To enable
the **subscript** plugin with your Markdown instance::

    markdown = mistune.create_markdown(plugins=['subscript'])

You can also pass the plugin function directly::

    from mistune.plugins.formatting import subscript

    renderer = mistune.HTMLRenderer()
    markdown = mistune.Markdown(renderer, plugins=[subscript])

math
----

The math plugin wraps block-level math syntax in ``<div>``. It wraps
inline-level math syntax in ``<span>``.

Block math uses ``$$`` markers:

.. code-block:: text

    $$
    \operatorname{ker} f=\{g\in G:f(g)=e_{H}\}{\mbox{.}}
    $$

This input produces:

.. code-block:: html

    <div class="math">$$
    \operatorname{ker} f=\{g\in G:f(g)=e_{H}\}{\mbox{.}}
    $$</div>

Inline math uses ``$`` markers:

.. code-block:: text

    function $f$

This input produces:

.. code-block:: html

    <p>function <span class="math">$f$</span></p>

``mistune.html()`` does not enable this plugin by default. To enable
the **math** plugin with your Markdown instance::

    markdown = mistune.create_markdown(plugins=['math'])

You can also pass the plugin function directly::

    from mistune.plugins.math import math

    renderer = mistune.HTMLRenderer()
    markdown = mistune.Markdown(renderer, plugins=[math])

ruby
----

The ruby plugin adds ``<ruby>`` tags. These examples show ruby syntax:

.. code-block:: text

    [漢字(ㄏㄢˋㄗˋ)]

    [link]: /url

    [漢字(ㄏㄢˋㄗˋ)][link]

    [漢字(ㄏㄢˋㄗˋ)](/url)

    [漢(ㄏㄢˋ)字(ㄗˋ)]

This input produces:

.. code-block:: html

    <p><ruby><rb>漢字</rb><rt>ㄏㄢˋㄗˋ</rt></ruby></p>
    <p><a href="/url"><ruby><rb>漢字</rb><rt>ㄏㄢˋㄗˋ</rt></ruby></a></p>
    <p><a href="/url"><ruby><rb>漢字</rb><rt>ㄏㄢˋㄗˋ</rt></ruby></a></p>
    <p><ruby><rb>漢</rb><rt>ㄏㄢˋ</rt></ruby><ruby><rb>字</rb><rt>ㄗˋ</rt></ruby></p>

``mistune.html()`` does not enable this plugin by default. To enable
the **ruby** plugin with your Markdown instance::

    markdown = mistune.create_markdown(plugins=['ruby'])

You can also pass the plugin function directly::

    from mistune.plugins.ruby import ruby

    renderer = mistune.HTMLRenderer()
    markdown = mistune.Markdown(renderer, plugins=[ruby])

Blog post: https://lepture.com/en/2022/markdown-ruby-markup


spoiler
-------

The spoiler plugin wraps block-level syntax in ``<div class="spoiler">``.
It wraps inline-level syntax in ``<span class="spoiler">``.

A block-level spoiler is like a block quote, but it uses the ``>!`` marker:

.. code-block:: text

    >! here is the spoiler content
    >!
    >! it will be hidden

This input produces:

.. code-block:: html

    <div class="spoiler">
    <p>here is the spoiler content</p>
    <p>it will be hidden</p>
    </div>

An inline spoiler is surrounded with ``>!`` and ``!<``:

.. code-block:: text

    this is the >! hidden text !<

This input produces:

.. code-block:: html

    <p>this is the <span class="spoiler">hidden text</span></p>

``mistune.html()`` does not enable this plugin by default. To enable
the **spoiler** plugin with your Markdown instance::

    markdown = mistune.create_markdown(plugins=['spoiler'])

You can also pass the plugin function directly::

    from mistune.plugins.spoiler import spoiler

    renderer = mistune.HTMLRenderer()
    markdown = mistune.Markdown(renderer, plugins=[spoiler])
