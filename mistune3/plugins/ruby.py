"""
<ruby>
~~~~~~

- [漢字(ㄏㄢˋㄗˋ)]
- [漢(ㄏㄢˋ)字(ㄗˋ)]

- [漢字(ㄏㄢˋㄗˋ)][link]
- [漢字(ㄏㄢˋㄗˋ)](/url "title")
"""

from ..util import safe_entity, unikey
from ..helpers import parse_link, parse_link_label


RUBY_PATTERN = (
  r'\['
  r'(?:\w+\(\w+\))+'
  r'\]'
)


def parse_ruby(inline, m, state):
    text = m.group(0)[1:-2]
    items = text.split(')')
    tokens = []
    for item in items:
        rb, rt = item.split('(')
        tokens.append({
            'type': 'ruby',
            'raw': rb,
            'attrs': {'rt': rt}
        })

    end_pos = m.end()

    # repeat link logic
    if end_pos < len(state.src):
        c = state.src[end_pos]
        if c == '(':
            # standard link [text](<url> "title")
            attrs, pos2 = parse_link(state.src, end_pos + 1)
            if pos2:
                state.append_token({
                    'type': 'link',
                    'children': inline.render_tokens(tokens),
                    'attrs': attrs,
                })
                return pos2

        elif c == '[':
            # standard ref link [text][label]
            label, pos2 = parse_link_label(state.src, end_pos + 1)
            if label and pos2:
                ref_links = state.env['ref_links']
                key = unikey(label)
                attrs = ref_links.get(key)
                if attrs:
                    state.append_token({
                        'type': 'link',
                        'children': inline.render_tokens(tokens),
                        'attrs': attrs,
                    })
                else:
                    for tok in tokens:
                        state.append_token(tok)
                    state.append_token({
                        'type': 'text',
                        'raw': safe_entity('[' + label + ']'),
                    })
                return pos2

    for tok in tokens:
        state.append_token(tok)
    return end_pos



def render_ruby(renderer, text, rt):
    return '<ruby><rb>' + text + '</rb><rt>' + rt + '</rt></ruby>'


def ruby(md):
    md.inline.register_rule('ruby', RUBY_PATTERN, parse_ruby, before='link')
    if md.renderer and md.renderer.NAME == 'html':
        md.renderer.register('ruby', render_ruby)
