__all__ = ['emoji']

EMOJI = r':[a-z0-9-]+:'


def parse_emoji(inline, m, state):
    text = m.group(0)
    state.append_token({
        'type': 'emoji',
        'raw': text,
    })
    return m.end()


def emoji(md):
    md.inline.register('emoji', EMOJI, parse_emoji, before='link')
