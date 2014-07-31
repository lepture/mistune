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

Version 0.3.1
~~~~~~~~~~~~~

Released on Jul. 31, 2014

* Fix in meth:`Renderer.block_code`, no need to add ``\n`` in ``<code>``.
* Trim whitespace of code in code span via `#15`_.

.. _`#15`: https://github.com/lepture/mistune/issues/15

Version 0.3.0
~~~~~~~~~~~~~

Released on Jun. 27, 2014

* Add ``<hr>`` in footnotes renderer
* Add hard_wrap configuration for GFM linebreaks.
* Add text renderer, via `#9`_.
* Define features for lexers available via `#11`_.

.. _`#9`: https://github.com/lepture/mistune/pull/9
.. _`#11`: https://github.com/lepture/mistune/pull/11

Version 0.2.0
~~~~~~~~~~~~~

Released on Mar. 12, 2014

* Use tuple instead of list for efficient
* Add ``line_match`` and ``line_started`` property on InlineLexer, via `#4`_

.. _`#4`: https://github.com/lepture/mistune/pull/4

Version 0.1.0
~~~~~~~~~~~~~

First preview release.
