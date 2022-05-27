import re
from urllib.parse import quote
from html import _replace_charref


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
    return escape(quote(unescape(link), safe=safe))


def safe_entity(s):
    return escape(unescape(s))


def unikey(s):
    key = ' '.join(s.split()).strip()
    return key.lower().upper()


_charref = re.compile(
    r'&(#[0-9]{1,7};'
    r'|#[xX][0-9a-fA-F]+;'
    r'|[^\t\n\f <&#;]{1,32};)'
)


def unescape(s):
    """
    Copy from `html.unescape`, but `_charref` is different. CommonMark
    does not accept entity references without a trailing semicolon
    """
    if not _replace_charref:
        return s

    if '&' not in s:
        return s
    return _charref.sub(_replace_charref, s)
