Introduction
============


Extendable
----------

The v2 Mistune is created to be extendable. With the plugins and directives
system, developers can extend it easily.


Sane CommonMark
---------------

CommonMark has paid too much attention to the insane cases. Their tests
contain so many weird cases that normal people wouldn't write. Instead,
they missed some real problematic cases, take an example:

.. code-block:: text

    [<https://lepture.com>](/hello)

It turns out on https://spec.commonmark.org/dingus/:

.. code-block:: html

    <p><a href="/hello"><a href="https://lepture.com">https://lepture.com</a></a></p>

A link can not contain another link in HTML. This case is an usual case, unlike
other cases, we may generate different HTML in different parsers, but we should
not generate invalid HTML.

Mistune has tests for CommonMark, but when some insane tests failed, we
ignore them.


Safety
------
