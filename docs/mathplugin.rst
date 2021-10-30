.. _mathplugin:

Mistune Markdown Math Plugin
============================


Overview
--------

The math plugin supports the very common $..$ and $$..$$ extended syntax for latex math inclusion in markdown. Certain pacakage parameters are modifiable to reflect specific markdown parser flavors.

The plugin works a little bit differently than others because html obviously does not have built-in LaTeX math tags. It was originally developed primarily for the AST functionality, and so the HTML options require the mistune user to include the appropriate Math Rendering options in their use.

Note also that there are several different math syntaxes and notations, and different html -> math renderers do not process them the same way (even KaTeX and MathJax, which are both described below, have different default notation support). The mathtex plugin does not attempt to validate whether the contents are valid - only that they are defined in the source markdown content by $..$ or $$..$$

Usage
-----

The mathtex plugin actually creates three plugin options:

* 'mathblock', which is a plugin that renders the $$..$$ math syntax that (usually) is rendered as a block display.
* 'mathspan', which is a plugin that renders the $..$ math syntax that (usually) is rendered as an inline display.
* 'math' is just a shortcut that consumes both 'mathspan' and 'mathblock' plugins.

For the AST renderer:

* Block math is rendered as ``{'type': 'mathblock', 'expression': '..'}``
* Inline math is rendered as ``{'type': 'mathspan', 'expression': '..'}``
* The expression will have the '$$' removed and will be stripped of any preceeding/following space.

For the HTML renderer:

* Block math is rendered as ``<div class="mathexpr">..</div>``
* Inline math is rendered as ``<span class="mathexpr">..</span>``
* The expression will have the '$' removed and will be stripped of any preceeding/following space.

Features and Implementation Notes 
---------------------------------

* block $$..$$ tokens may be space-padded by exacltly one space, e.g. ``$$ \\alpha $$``, which is often supported by not universally (dillinger.io does not support it). There are examples of the $$ token being able to be on a line by itself, but this does not appear common and since it can lead to over-identification, it is not supported here.
* inline $..$ tokens **may not** be space padded as it creates syntax conflicts too readily with currency usage (and no surveyed parser supports this).
* The plugin supports multiline equations so long as each consecutive line between the open and close tokens have text. Multiline support does not cross full paragraph breaks.
* In cases of uneven start and end tokens:
   *  $..$$ is rendered as inline math with the extra $ beginning the following text (i.e., the $..$ is rendered).
   *  $$..$ does not render at all. Technically, $$ could be perceived as an empty inline block, leaving the closing $ by itself, but this would be weird and almost definitely unintended. 
* There is no way to create an explicitly blank math entity to fill in later, because any attempt of doing so (e.g., ``$$$$`` or ``$ $``) would potentially conflict with written text. Alternatives for the user might include a single character (e.g., ``$.$``, ``$$_$$``) or, for silent html, an empty tag (``$$< />$$``).   
* The KaTex and MathJax javascript renderers were surveyed and cookbook examples appear below.
* In developing the plugin, StackEdit, dillinger.io, Typora, and OSF were surveyed to see how they handle Math Syntax in markdown. Some notes about the what was observed follow:
   * `StackEdit <https://stackedit.io/>`'s default implementation matches the usage and features here. 
   * `Typora <https://typora.io/>`'s default math renderer is exclusively '$$' math blocks. There is no support for inline spans.
   * `dillinger.io <https://dillinger.io/>`'s default math implementation:
      * does not recognize the $..$ math span at all.
      * renders $$..$$ as an inline math span.
      * does not allow padded tokens, i.e. ``$$ \\alpha $$`` does not render but ``$$\\alpha$$`` does.
   * `OSF <https://osf.io>` is not a general markdown editor, but uses markdown with math for its wikis. It's implementation matches the usage and features here.

AST Rendering
-------------

The mathtex plugin renders AST as two distinct types:

* 'mathblock' for $$..$$ blocks
* 'mathspan' for inline $..$ notation 

In all math cases, the 'expression' tag is where the math expression is placed. The $'s and any preceeding space is stripped from the expression value.

Math blocks written inline in markdown create separate paragraphs for text before and after it in both HTML and AST renderers. 

For HTML renderers, inline math markdown creates one paragraph with the mathexpr span inside. In AST, the inline math markdown creates an outer paragraph object with the preceeding and following text as separate "text" elements at the same level in the paragraph's children. 

Refer to the ``mathblock.json`` and ``mathspan.json`` in ``tests/fixtures/json`` to see nunaces for how mathblocks and mathspans AST structures may render based on different markdown syntax.

Example
^^^^^^^

This is an example to generate an AST that only supports $$..$$ mathblock syntax.

.. code-block:: python

    import mistune

    markdown_analyzer = mistune.create_markdown(
        renderer='ast',
        plugins=[
            'mathblock' 
        ]
    )
    ast = markdown_analyzer(text)


HTML Rendering
--------------

The Math HTML renderer wraps the detected math html in the following way:

* The math signifier tokens ($/$$) are removed from the output.
* Both inline and block math are given class "mathexpr". They are given the same class to simplify identification and processing, and the html tag type is used to enforce the inline/block distinction:
   * Inline math ($..$) is rendered as ``<span class="mathexpr">..</span>``
   * Math blocks ($$..$$) are rendered as ``<div class="mathexpr">..</div>`` 
* If the user wishes to render $$ as inline (as dillinger.io does), they can add a ``display=inline`` CSS rule for ``div.mathexpr``

Refer to the ``mathblock.txt`` and ``mathspan.txt`` in ``tests/fixtures/`` to see nunaces for how mathblocks and mathspans html is rendered based on different markdown syntax.


Example
^^^^^^^

This is an example to generate html from markdown that includes both inline and block math syntax.

.. code-block:: python

    import mistune

    markdown_analyzer = mistune.create_markdown(
        plugins=[
            'math' 
        ]
    )

    def generate_html(markdown):
        html = standard_header() + 
            markdown_analyzer(text) + 
            standard_footer()
        return(html)


Using KaTex with the mathexpr plugin
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

See more about `KaTeX at their website <https://katex.org/>`

If you are using mistune to generate html with KaTeX, you will need to include the KaTeX javascript library in your header and code to identify and render the identified blocks. The following javascript example will render all of the generated blocks in your output, provided your mistune-generated markdown is static html and you need only call it once. If you retrieve mistune generated html dynamically, you will need to customize the function to handle the newly created elements.

.. code-block:: javascript

      //A global variable is required by KaTeX. See their documentation for details.
      const katex_macros = {}; 
      function renderMistuneKaTex(){        
          var mathelems = document.getElementsByClassName("mathexpr");
          for (var i = 0; i < mathelems.length; i++) {
               katex.render(mathelems[i].textContent, mathelems[i], {
               throwOnError: false,
               katex_macros
          });
      }

You do also need to include the KaTeX javascript libraries and stylesheet.  At the time of writing, the following additions included the libraries and also call ``renderMistuneKaTex`` when the page is loaded, which will need to be included or referenced in your page as well.

.. code-block:: html

    <head>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.13.21/dist/katex.min.css" integrity="sha384-4Y/XYS9mD9HJ+dIEpYViUGob3atehZCmTPqyUCOLZHfe1iKgH/3tCGDCIDx+WNZc" crossorigin="anonymous">

        <!-- The loading of KaTeX is deferred to speed up page rendering -->
        <script defer src="https://cdn.jsdelivr.net/npm/katex@0.13.21/dist/katex.min.js" integrity="sha384-YT8NmKMJkaFK5r+P/VDFRWM8rjcA0BdmAc0fH8+gbzCiRgmxOZf9ws29ixle0N5w" crossorigin="anonymous"></script>

        <!-- To automatically render math in text elements, include the auto-render extension: -->
        <script defer src="https://cdn.jsdelivr.net/npm/katex@0.13.21/dist/contrib/auto-render.min.js" integrity="sha384-+XBljXPPiv+OzfbB3cVmLHf4hdUFHlWNZN5spNQ7rmHTXpd7WvJum6fIACpNNfIR" crossorigin="anonymous"
            onload="renderMistuneKaTex();"></script>
        ...
    </head>

Using MathJax with the mathexpr plugin
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In contrast to KaTeX, MathJax is more of a greedy math processor as it assumes you want all of the math in a webpage automatically renders and it will attempt to do so. In many instances, if you generate html with mistune and the math plugin, simply including the MathJax javscript library will automatically find and resolve your math. There are many customizations available in the `MathJax <https://docs.mathjax.org/>` if you have specific math dialects or additional customization needs.

If you do want to limit the MathJax to only look inside the generated "mathexpr" blocks, here are two ways to do it. 

MathJax via Element Identification
##################################

You can also specify the elements to be rendered if they are available during configuration. The HTML structure for the code would begin like this, assuming you are using the default mathexpr classes as created by the math plugin:

.. code-block:: html

    <!DOCTYPE html>
    <html>
        <head>
            <script type="text/javascript" async
            src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js?config=TeX-MML-AM_CHTML">
            var mathelems = document.getElementsByClassName("mathexpr");
            MathJax.Hub.Config({
                elements: mathelems
            });
            </script>
        </head>
 

MathJax via CSS Classes
#######################

As all of the mathexpr identified blocks are given the css class "mathexpr", you can you limit MathJax if you also have a class assigned to your body or an outermost content div.  Note that the *processClass* option is only for elements within blocks that are not rendered due to *ignoreClass*, and anything outside the ``ignoredClass`` blocks will still be processed. 

.. code-block:: javascript

      MathJax.Hub.Config({
        tex2jax: {
            ignoreClass: "content",
            processClass: "mathexpr",
        }
    });

The HTML structure for the above code would look like this:

.. code-block:: html

    <!DOCTYPE html>
    <html>
        <head>
            <script type="text/javascript" async
            src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js?config=TeX-MML-AM_CHTML">

            MathJax.Hub.Config({
                tex2jax: {
                    ignoreClass: "content",
                    processClass: "mathexpr",
                }
            });
            </script>
        </head>
    
        <body class="content">
        ... html with mistune generated elements ...
        </body>
    </html>



Author
-------

The mathexpr plugin is open source and distributed under the BSD-3 Clause License. Its initial version was written by Kevin Crouse, 2021. All rights reserved.  