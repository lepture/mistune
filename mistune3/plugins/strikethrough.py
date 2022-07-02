import re
from ..helpers import PREVENT_BACKSLASH

__all__ = ["strikethrough"]

_STRIKE_END = re.compile(r'(.+?)' + PREVENT_BACKSLASH + r'~~', re.S)


def render_strikethrough(renderer, text):
    return '<del>' + text + '</del>'


def parse_strikethrough(inline, m, state):
    pos = m.end()
    m1 = _STRIKE_END.match(state.src, pos)
    if not m1:
        inline.process_text(m.group(0), state)
        return pos
    text = m1.group(1)
    children = inline.render(text, state.copy())
    state.append_token({'type': 'strikethrough', 'children': children})
    return m1.end()


def strikethrough(md):
    md.inline.register_rule(
        'strikethrough',
        r'~~(?=[^\s~])',
        parse_strikethrough,
        before='link',
    )
    if md.renderer and md.renderer.NAME == 'html':
        md.renderer.register('strikethrough', render_strikethrough)
