.. include:: ../README.rst

Developer Guide
---------------

Here is the API reference for mistune.

.. module:: mistune

.. autoclass:: Renderer
   :members:

.. autoclass:: Markdown
   :members:

.. autofunction:: markdown
.. autofunction:: escape

Changelog
----------

Here is the full history of mistune.

Version 0.4.1
~~~~~~~~~~~~~

Released on Oct. 12, 2014

* Add option for parse markdown in block level html.
* Fix on lheading, any number of underline = or - will work.
* Patch for setup if Cython is available but no C compiler.

Version 0.4
~~~~~~~~~~~

Released on Aug. 14, 2014

* Bugfix. Use inspect to detect renderer class.
* Move all meth:`escape` to renderer. Use renderer to escape everything.
* A little changes in code style and parameter naming.
* Don't parse text in a block html, behave like sundown.

Version 0.3.1
~~~~~~~~~~~~~

Released on Jul. 31, 2014

* Fix in meth:`Renderer.block_code`, no need to add ``\n`` in ``<code>``.
* Trim whitespace of code in code span via `#15`_.

.. _`#15`: https://github.com/lepture/mistune/issues/15

Version 0.3
~~~~~~~~~~~

Released on Jun. 27, 2014

* Add ``<hr>`` in footnotes renderer
* Add hard_wrap configuration for GFM linebreaks.
* Add text renderer, via `#9`_.
* Define features for lexers available via `#11`_.

.. _`#9`: https://github.com/lepture/mistune/pull/9
.. _`#11`: https://github.com/lepture/mistune/pull/11

Version 0.2
~~~~~~~~~~~

Released on Mar. 12, 2014

* Use tuple instead of list for efficient
* Add ``line_match`` and ``line_started`` property on InlineLexer, via `#4`_

.. _`#4`: https://github.com/lepture/mistune/pull/4

Version 0.1
~~~~~~~~~~~

First preview release.
