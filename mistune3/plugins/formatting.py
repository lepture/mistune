import re
from ..helpers import unescape_char, PREVENT_BACKSLASH

__all__ = ["strikethrough", "mark", "insert", "subscript"]

_STRIKE_END = re.compile(r'(.+?)' + PREVENT_BACKSLASH + r'~~', re.S)
_MARK_END = re.compile(r'(.+?)' + PREVENT_BACKSLASH + r'==', re.S)
_INSERT_END = re.compile(r'(.+?)' + PREVENT_BACKSLASH + r'\^\^', re.S)
SUBSCRIPT_PATTERN = r'~(?:\S|\\ )+?~'


def parse_strikethrough(inline, m, state):
    return _parse_to_end(inline, m, state, 'strikethrough', _STRIKE_END)


def render_strikethrough(renderer, text):
    return '<del>' + text + '</del>'


def parse_mark(inline, m, state):
    return _parse_to_end(inline, m, state, 'mark', _MARK_END)


def render_mark(renderer, text):
    return '<mark>' + text + '</mark>'


def parse_insert(inline, m, state):
    return _parse_to_end(inline, m, state, 'insert', _INSERT_END)


def render_insert(renderer, text):
    return '<ins>' + text + '</ins>'


def parse_subscript(inline, m, state):
    text = m.group(0)
    new_state = state.copy()
    new_state.src = text[1:-1].replace('\\ ', ' ')
    children = inline.render(new_state)
    state.append_token({
        'type': 'subscript',
        'children': children
    })
    return m.end()


def render_subscript(renderer, text):
    return '<sub>' + text + '</sub>'


def _parse_to_end(inline, m, state, tok_type, end_pattern):
    pos = m.end()
    m1 = end_pattern.match(state.src, pos)
    if not m1:
        return
    text = m1.group(1)
    new_state = state.copy()
    new_state.src = text
    children = inline.render(new_state)
    state.append_token({'type': tok_type, 'children': children})
    return m1.end()


def strikethrough(md):
    md.inline.register(
        'strikethrough',
        r'~~(?=[^\s~])',
        parse_strikethrough,
        before='link',
    )
    if md.renderer and md.renderer.NAME == 'html':
        md.renderer.register('strikethrough', render_strikethrough)


def mark(md):
    md.inline.register(
        'mark',
        r'==(?=[^\s=])',
        parse_mark,
        before='link',
    )
    if md.renderer and md.renderer.NAME == 'html':
        md.renderer.register('mark', render_mark)


def insert(md):
    md.inline.register(
        'insert',
        r'\^\^(?=[^\s\^])',
        parse_insert,
        before='link',
    )
    if md.renderer and md.renderer.NAME == 'html':
        md.renderer.register('insert', render_insert)


def subscript(md):
    md.inline.register('subscript', SUBSCRIPT_PATTERN, parse_subscript, before='linebreak')
    if md.renderer and md.renderer.NAME == 'html':
        md.renderer.register('subscript', render_subscript)
