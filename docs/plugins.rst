.. _plugins:

Built-in Plugins
================

.. meta::
    :description: List of Mistune built-in plugins, their syntax and how to enable them.

Mistune offers many built-in plugins, including all the popular markups.

.. _strikethrough:

strikethrough
-------------

.. code-block:: text

    ~~here is the content~~

``mistune.html()`` has enabled strikethrough plugin by default. To create
a markdown instance your own::

    markdown = mistune.create_markdown(plugins=['strikethrough'])

Another way to create your own Markdown instance::

    from mistune.plugins.formatting import strikethrough

    renderer = mistune.HTMLRenderer()
    markdown = mistune.Markdown(renderer, plugins=[strikethrough])


footnotes
---------

.. code-block:: text

    content in paragraph with footnote[^1] markup.

    [^1]: footnote explain


``mistune.html()`` has enabled footnote plugin by default. To create
a markdown instance your own::

    markdown = mistune.create_markdown(plugins=['footnotes'])

Another way to create your own Markdown instance::

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
     Conent Cell |  Content Cell   | Content Cell


    | Left Header |  Center Header  | Right Header  |
    | :---------- | :-------------: | ------------: |
    | Conent Cell |  Content Cell   | Content Cell  |

``mistune.html()`` has enabled table plugin by default. To create
a markdown instance your own::

    markdown = mistune.create_markdown(plugins=['table'])

Another way to create your own Markdown instance::

    from mistune.plugins.table import table

    renderer = mistune.HTMLRenderer()
    markdown = mistune.Markdown(renderer, plugins=[table])


url
---

URL plugin enables creating link with raw URL by default:

.. code-block:: text

    For instance, https://typlog.com/

Will be converted into:

.. code-block:: html

    <p>For instance, <a href="https://typlog.com/>https://typlog.com/</a></p>

This plugin is **NOT ENABLED** by default in ``mistune.html()``. Mistune
values explicit, and we suggest writers to write links in:

.. code-block:: text

    <https://typlog.com/>

To enable **url** plugin with your own markdown instance::

    markdown = mistune.create_markdown(plugins=['url'])

Another way to create your own Markdown instance::

    from mistune.plugins.url import url

    renderer = mistune.HTMLRenderer()
    markdown = mistune.Markdown(renderer, plugins=[url])

task_lists
----------

Task lists plugin enables creating GitHub todo items:

.. code-block:: text

    - [x] item 1
    - [ ] item 2

Will be converted into:

.. code-block:: html

    <ul>
    <li class="task-list-item"><input class="task-list-item-checkbox" type="checkbox" disabled checked/>item 1</li>
    <li class="task-list-item"><input class="task-list-item-checkbox" type="checkbox" disabled/>item 2</li>
    </ul>


This plugin is **NOT ENABLED** by default in ``mistune.html()``. To enable
**task_lists** plugin with your own markdown instance::

    markdown = mistune.create_markdown(plugins=['task_lists'])

Another way to create your own Markdown instance::

    from mistune.plugins.task_lists import task_lists

    renderer = mistune.HTMLRenderer()
    markdown = mistune.Markdown(renderer, plugins=[task_lists])

def_list
--------

def_list plugin enables creating html definition lists:

.. code-block:: text

    First term
    : First definition
    : Second definition
    
    Second term
    : Third definition
    
Will be converted into:

.. code-block:: html

    <dl>
    <dt>First term</dt>
    <dd>First definition</dd>
    <dd>Second definition</dd>
    <dt>Second term</dt>
    <dd>Third definition</dd>
    </dl>


This plugin is **NOT ENABLED** by default in ``mistune.html()``. To enable
**def_list** plugin with your own markdown instance::

    markdown = mistune.create_markdown(plugins=['def_list'])

Another way to create your own Markdown instance::

    from mistune.plugins.def_list import def_list

    renderer = mistune.HTMLRenderer()
    markdown = mistune.Markdown(renderer, plugins=[def_list])

abbr
----

abbr plugin enables creating abbreviations:

.. code-block:: text

    The HTML specification
    is maintained by the W3C.

    *[HTML]: Hyper Text Markup Language
    *[W3C]: World Wide Web Consortium

Will be converted into:

.. code-block:: html

    The <abbr title="Hyper Text Markup Language">HTML</abbr> specification
    is maintained by the <abbr title="World Wide Web Consortium">W3C</abbr>.

This plugin is **NOT ENABLED** by default in ``mistune.html()``. To enable
**abbr** plugin with your own markdown instance::

    markdown = mistune.create_markdown(plugins=['abbr'])

Another way to create your own Markdown instance::

    from mistune.plugins.abbr import abbr

    renderer = mistune.HTMLRenderer()
    markdown = mistune.Markdown(renderer, plugins=[abbr])


mark
----

mark plugin adds the ability to insert ``<mark>`` tags. To mark some text, simply surround the text with ``==``:

.. code-block:: text

    ==mark me== ==mark with\=\=equal==

Will be converted into:

.. code-block:: html

    <mark>mark me</mark> <mark>mark with==equal</mark>

This plugin is **NOT ENABLED** by default in ``mistune.html()``. To enable
**mark** plugin with your own markdown instance::

    markdown = mistune.create_markdown(plugins=['mark'])

Another way to create your own Markdown instance::

    from mistune.plugins.formatting import mark

    renderer = mistune.HTMLRenderer()
    markdown = mistune.Markdown(renderer, plugins=[mark])


insert
------

insert plugin adds the ability to insert ``<ins>`` tags. To insert some text, simply surround the text with ``^^``:

.. code-block:: text

    ^^insert me^^ ^^insert\^\^me^^

Will be converted into:

.. code-block:: html

    <ins>insert me</ins> <ins>insert^^me</ins>

This plugin is **NOT ENABLED** by default in ``mistune.html()``. To enable
**insert** plugin with your own markdown instance::

    markdown = mistune.create_markdown(plugins=['insert'])

Another way to create your own Markdown instance::

    from mistune.plugins.formatting import insert

    renderer = mistune.HTMLRenderer()
    markdown = mistune.Markdown(renderer, plugins=[insert])

superscript
-----------

superscript plugin adds the ability to insert ``<sup>`` tags. The syntax looks like:

.. code-block:: text

    Hello^superscript^

Will be converted into:

.. code-block:: html

    <p>Hello<sup>superscript</sup></p>

This plugin is **NOT ENABLED** by default in ``mistune.html()``. To enable
**superscript** plugin with your own markdown instance::

    markdown = mistune.create_markdown(plugins=['superscript'])

Another way to create your own Markdown instance::

    from mistune.plugins.formatting import superscript

    renderer = mistune.HTMLRenderer()
    markdown = mistune.Markdown(renderer, plugins=[superscript])

subscript
---------

subscript plugin adds the ability to insert ``<sub>`` tags. The syntax looks like:

.. code-block:: text

    Hello~subscript~

    CH~3~CH~2~OH

Will be converted into:

.. code-block:: html

    <p>Hello<sub>subscript</sub></p>
    <p>CH<sub>3</sub>CH<sub>2</sub>OH</p>

This plugin is **NOT ENABLED** by default in ``mistune.html()``. To enable
**subscript** plugin with your own markdown instance::

    markdown = mistune.create_markdown(plugins=['subscript'])

Another way to create your own Markdown instance::

    from mistune.plugins.formatting import subscript

    renderer = mistune.HTMLRenderer()
    markdown = mistune.Markdown(renderer, plugins=[subscript])

math
----

Math plugin wraps ``<div>`` for block level math syntax, and ``<span>`` for inline level
math syntax.

A block math is surrounded with ``$$``:

.. code-block:: text

    $$
    \operatorname{ker} f=\{g\in G:f(g)=e_{H}\}{\mbox{.}}
    $$

Will be converted into:

.. code-block:: html

    <div class="math">$$
    \operatorname{ker} f=\{g\in G:f(g)=e_{H}\}{\mbox{.}}
    $$</div>

An inline math is surrounded with ``$`` inline:

.. code-block:: text

    function $f$

Will be converted into:

.. code-block:: html

    <p>function <span class="math">$f$</span></p>

This plugin is **NOT ENABLED** by default in ``mistune.html()``. To enable
**math** plugin with your own markdown instance::

    markdown = mistune.create_markdown(plugins=['math'])

Another way to create your own Markdown instance::

    from mistune.plugins.math import math

    renderer = mistune.HTMLRenderer()
    markdown = mistune.Markdown(renderer, plugins=[math])

ruby
----

insert plugin adds the ability to insert ``<ruby>`` tags. Here are some examples for ruby syntax:

.. code-block:: text

    [漢字(ㄏㄢˋㄗˋ)]

    [link]: /url

    [漢字(ㄏㄢˋㄗˋ)][link]

    [漢字(ㄏㄢˋㄗˋ)](/url)

    [漢(ㄏㄢˋ)字(ㄗˋ)]

Will be converted into:

.. code-block:: html

    <p><ruby><rb>漢字</rb><rt>ㄏㄢˋㄗˋ</rt></ruby></p>
    <p><a href="/url"><ruby><rb>漢字</rb><rt>ㄏㄢˋㄗˋ</rt></ruby></a></p>
    <p><a href="/url"><ruby><rb>漢字</rb><rt>ㄏㄢˋㄗˋ</rt></ruby></a></p>
    <p><ruby><rb>漢</rb><rt>ㄏㄢˋ</rt></ruby><ruby><rb>字</rb><rt>ㄗˋ</rt></ruby></p>

This plugin is **NOT ENABLED** by default in ``mistune.html()``. To enable
**ruby** plugin with your own markdown instance::

    markdown = mistune.create_markdown(plugins=['ruby'])

Another way to create your own Markdown instance::

    from mistune.plugins.ruby import ruby

    renderer = mistune.HTMLRenderer()
    markdown = mistune.Markdown(renderer, plugins=[ruby])

Blog post: https://lepture.com/en/2022/markdown-ruby-markup


spoiler
-------

Spoiler plugin wraps ``<div class="spoiler">`` for block level syntax,
and ``<span class="spoiler">`` for inline level syntax.

A block level spoiler looks like block quote, but the marker is ``>!``:

.. code-block:: text

    >! here is the spoiler content
    >!
    >! it will be hidden

Will be converted into:

.. code-block:: html

    <div class="spoiler">
    <p>here is the spoiler content</p>
    <p>it will be hidden</p>
    </div>

An inline spoiler is surrounded with ``>!`` and ``!<``:

.. code-block:: text

    this is the >! hidden text !<

Will be converted into:

.. code-block:: html

    <p>this is the <span class="spoiler">hidden text</span></p>

This plugin is **NOT ENABLED** by default in ``mistune.html()``. To enable
**spoiler** plugin with your own markdown instance::

    markdown = mistune.create_markdown(plugins=['spoiler'])

Another way to create your own Markdown instance::

    from mistune.plugins.spoiler import spoiler

    renderer = mistune.HTMLRenderer()
    markdown = mistune.Markdown(renderer, plugins=[spoiler])
