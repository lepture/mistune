import re
from ..core import BlockState
from ..util import unikey, safe_entity
from ..helpers import LINK_LABEL

__all__ = ['footnotes']

_PARAGRAPH_SPLIT = re.compile(r'\n{2,}')
# https://michelf.ca/projects/php-markdown/extra/#footnotes
REF_FOOTNOTE = (
  r'^(?P<footnote_lead> {0,3})'
  r'\[\^(?P<footnote_key>' + LINK_LABEL + r')]:[ \t]'
  r'(?P<footnote_text>[^\n]*\n+'
  r'(?:(?P=footnote_lead) {1,3}(?! )[^\n]*\n+)*'
  r')'
)

INLINE_FOOTNOTE = r'\[\^(?P<footnote_key>' + LINK_LABEL + r')\]'


def parse_inline_footnote(inline, m, state):
    key = unikey(m.group('footnote_key'))
    ref = state.env.get('ref_footnotes')
    if ref and key in ref:
        footnotes = state.env.get('footnotes')
        if not footnotes:
            footnotes = []
        if key not in footnotes:
            footnotes.append(key)
            state.env['footnotes'] = footnotes
        state.append_token({
          'type': 'footnote_ref',
          'raw': key,
          'attrs': {'index': footnotes.index(key) + 1}
        })
    else:
        state.append_token({'type': 'text', 'raw': safe_entity(m.group(0))})
    return m.end()


def parse_ref_footnote(block, m, state: BlockState):
    ref = state.env.get('ref_footnotes')
    if not ref:
        ref = {}

    key = unikey(m.group('footnote_key'))
    if key not in ref:
        ref[key] = m.group('footnote_text')
        state.env['ref_footnotes'] = ref
    return m.end()


def parse_footnote_item(block, key, index, state):
    ref = state.env.get('ref_footnotes')
    text = ref[key]

    lines = text.splitlines()
    second_line = None
    for second_line in lines[1:]:
        if second_line:
            break

    if second_line:
      spaces = len(second_line) - len(second_line.lstrip())
      pattern = re.compile(r'^ {' + str(spaces) + r',}', flags=re.M)
      text = pattern.sub('', text).strip()
      items = _PARAGRAPH_SPLIT.split(text)
      children = [{'type': 'paragraph', 'text': s} for s in items]
    else:
      text = text.strip()
      children = [{'type': 'paragraph', 'text': text}]
    return {
        'type': 'footnote_item',
        'children': children,
        'attrs': {'key': key, 'index': index}
    }


def md_footnotes_hook(md, result, state: BlockState):
    footnotes = state.env.get('footnotes')
    if not footnotes:
        return result

    children = [
        parse_footnote_item(md.block, k, i + 1, state)
        for i, k in enumerate(footnotes)
    ]
    state = BlockState()
    state.tokens = [{'type': 'footnotes', 'children': children}]
    output = md.block.render(state, md.inline)
    return result + output


def render_footnote_ref(renderer, key, index):
    i = str(index)
    html = '<sup class="footnote-ref" id="fnref-' + i + '">'
    return html + '<a href="#fn-' + i + '">' + i + '</a></sup>'


def render_footnotes(renderer, text):
    return '<section class="footnotes">\n<ol>\n' + text + '</ol>\n</section>\n'


def render_footnote_item(renderer, text, key, index):
    i = str(index)
    back = '<a href="#fnref-' + i + '" class="footnote">&#8617;</a>'

    text = text.rstrip()
    if text.endswith('</p>'):
        text = text[:-4] + back + '</p>'
    else:
        text = text + back
    return '<li id="fn-' + i + '">' + text + '</li>\n'


def footnotes(md):
    md.inline.register(
        'footnote',
        INLINE_FOOTNOTE,
        parse_inline_footnote,
        before='link',
    )
    md.block.register(
        'ref_footnote',
        REF_FOOTNOTE,
        parse_ref_footnote,
        before='ref_link',
    )
    md.after_render_hooks.append(md_footnotes_hook)

    if md.renderer and md.renderer.NAME == 'html':
        md.renderer.register('footnote_ref', render_footnote_ref)
        md.renderer.register('footnote_item', render_footnote_item)
        md.renderer.register('footnotes', render_footnotes)
