Upgrade Guide
=============


Upgrade from v2 to v3
---------------------


When customizing renderers, these methods' paramters are changed::


    -    link(self, link, text=None, title=None)
    +    link(self, text, url, title=None)

    -    image(self, src, alt="", title=None)
    +    image(self, alt, url, title=None)

    -    heading(self, text, level)
    +    heading(self, text, level, **attrs)

    -    list(self, text, ordered, level, start=None)
    +    list(self, text, ordered, **attrs)

    -    list_item(self, text, level)
    +    list_item(self, text, **attrs)

    -    table_cell(self, text, align=None, is_head=False)
    +    table_cell(self, text, align=None, head=False)
