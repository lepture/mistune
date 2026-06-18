import re
try:
    from urllib.parse import quote
    import html
except ImportError:
    from urllib import quote
    html = None


PUNCTUATION = r'''\\!"#$%&'()*+,./:;<=>?@\[\]^`{}|_~-'''
ESCAPE_TEXT = r'\\[' + PUNCTUATION + ']'


def escape(s, quote=True):
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    if quote:
        s = s.replace('"', "&quot;")
    return s


def escape_url(link):
    safe = (
        ':/?#@'           # gen-delims - '[]' (rfc3986)
        '!$&()*+,;='      # sub-delims - "'" (rfc3986)
        '%'               # leave already-encoded octets alone
    )

    if html is None:
        return quote(link.encode('utf-8'), safe=safe)
    return html.escape(quote(_unescape(link), safe=safe))


def escape_html(s):
    if html is not None:
        return html.escape(_unescape(s)).replace('&#x27;', "'")
    return escape(s)


def unikey(s):
    return ' '.join(s.split()).lower()


_charref = re.compile(r"&(?:#[0-9]+|#[xX][0-9a-fA-F]+|[^\t\n\f <&#;]{1,32});")


def _unescape(s):
    """Unescape HTML and numeric entities in string.

    Python's `html.unescape`_ is quite aggressive in that it will recognize and
    unescape as HTML entities character strings that *are not* terminated by a
    semicolon.

    The `HTML5 standard`_ is pretty clear the entities *must* be terminated by a
    semicolon.

    This essentially does the same thing as ``html.unescape`` except that it
    requires that entities be terminated by semicolons.

    Note that since the implementation of the function currently relies on
    ``html.unescape``, it will only work under Python 3.

    _html.unescape: https://docs.python.org/3/library/html.html#html.unescape
    _HTML5 standard: https://html.spec.whatwg.org/multipage/syntax.html#character-references

    """
    return _charref.sub(lambda match: html.unescape(match.group(0)), s)
