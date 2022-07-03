import re
from ..util import escape, safe_entity
from ..helpers import PREVENT_BACKSLASH

__all__ = ['abbr']

# https://michelf.ca/projects/php-markdown/extra/#abbr
REF_ABBR = (
  r'^ {0,3}\*\[(?P<abbr_key>[^\]]+)'+ PREVENT_BACKSLASH + r'\]:'
  r'(?P<abbr_text>(?:[ \t]*\n(?: {3,}|\t)[^\n]+)|(?:[^\n]*))$'
)


def parse_ref_abbr(block, m, state):
    ref = state.env.get('ref_abbrs')
    if not ref:
        ref = {}
    key = m.group('abbr_key')
    text = m.group('abbr_text')
    ref[key] = text.strip()
    state.env['ref_abbrs'] = ref
    # abbr definition can split paragraph
    state.append_token({'type': 'blank_line'})
    return m.end() + 1


def process_text(text, state):
    ref = state.env.get('ref_abbrs')
    if not ref:
        return state.append_token({'type': 'text', 'raw': safe_entity(text)})

    pattern = re.compile(r'|'.join(re.escape(k) for k in ref.keys()))
    pos = 0
    while pos < len(text):
        m = pattern.search(text, pos)
        if not m:
            break

        end_pos = m.start()
        if end_pos > pos:
            hole = text[pos:end_pos]
            state.append_token({'type': 'text', 'raw': safe_entity(hole)})

        label = m.group(0)
        state.append_token({
            'type': 'abbr',
            'raw': safe_entity(label),
            'attrs': {'title': ref[label]}
        })
        pos = m.end()

    if pos == 0:
        # special case, just pure text
        state.append_token({'type': 'text', 'raw': safe_entity(text)})
    elif pos < len(text):
        state.append_token({'type': 'text', 'raw': safe_entity(text[pos:])})


def render_abbr(renderer, text, title):
    if not title:
        return '<abbr>' + text + '</abbr>'
    return '<abbr title="' + escape(title) + '">' + text + '</abbr>'


def abbr(md):
    md.block.register('ref_abbr', REF_ABBR, parse_ref_abbr, before='paragraph')
    # replace process_text
    md.inline.process_text = process_text
    if md.renderer and md.renderer.NAME == 'html':
        md.renderer.register('abbr', render_abbr)
