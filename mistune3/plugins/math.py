__all__ = ['math']

BLOCK_MATH = r'\$\$[ \t]*\n(?P<math_text>.+?)\n\$\$[ \t]*$'
INLINE_MATH = r'\$(?!\s)(?P<math_text>.+?)(?!\s)\$'


def parse_block_math(block, m, state):
    text = m.group('math_text')
    state.append_token({'type': 'block_math', 'raw': text})
    return m.end() + 1


def parse_inline_math(inline, m, state):
    text = m.group('math_text')
    state.append_token({'type': 'inline_math', 'raw': text})
    return m.end()


def render_block_math(renderer, text):
    return '<div class="math">$$\n' + text + '\n$$</div>\n'


def render_inline_math(renderer, text):
    return '<span class="math">$' + text + '$</span>'


def math(md):
    md.block.register_rule('block_math', BLOCK_MATH, parse_block_math, before='list')
    md.inline.register_rule('inline_math', INLINE_MATH, parse_inline_math, before='link')
    if md.renderer and md.renderer.NAME == 'html':
        md.renderer.register('block_math', render_block_math)
        md.renderer.register('inline_math', render_inline_math)
