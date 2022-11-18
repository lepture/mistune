from typing import Dict, Any
from ..core import BaseRenderer, BlockState
from ..util import safe_entity, strip_end


class RSTRenderer(BaseRenderer):
    """A renderer for converting Markdown to ReST."""
    NAME = 'rst'

    #: marker symbols for heading
    HEADING_MARKERS = {
      1: '=',
      2: '-',
      3: '~',
      4: '^',
      5: '"',
      6: "'",
    }
    INLINE_IMAGE_PREFIX = 'img-'

    def __call__(self, tokens, state: BlockState):
        state.env['inline_images'] = []
        out = self.render_tokens(tokens, state)
        out += '\n\n'.join(self.render_referrences(state))
        return strip_end(out)

    def render_referrences(self, state: BlockState):
        images = state.env['inline_images']
        for index, token in enumerate(images):
            attrs = token['attrs']
            alt = self.render_children(token, state)
            ident = self.INLINE_IMAGE_PREFIX + str(index)
            yield '.. |' + ident + '| image:: ' + attrs['url'] + '\n   :alt: ' + alt

    def render_children(self, token, state: BlockState):
        children = token['children']
        return self.render_tokens(children, state)

    def text(self, token: Dict[str, Any], state: BlockState) -> str:
        return safe_entity(token['raw'])

    def emphasis(self, token: Dict[str, Any], state: BlockState) -> str:
        return '*' + self.render_children(token, state) + '*'

    def strong(self, token: Dict[str, Any], state: BlockState) -> str:
        return '**' + self.render_children(token, state) + '**'

    def link(self, token: Dict[str, Any], state: BlockState) -> str:
        attrs = token['attrs']
        text = self.render_children(token, state)
        return '`' + text + ' <' + attrs['url'] + '>`__'

    def image(self, token: Dict[str, Any], state: BlockState) -> str:
        refs: list = state.env['inline_images']
        index = len(refs)
        refs.append(token)
        return '|' + self.INLINE_IMAGE_PREFIX + str(index) + '|'

    def codespan(self, token: Dict[str, Any], state: BlockState) -> str:
        return '``' + self.render_children(token, state) + '``'

    def linebreak(self, token: Dict[str, Any], state: BlockState) -> str:
        return '\n\n'

    def softbreak(self, token: Dict[str, Any], state: BlockState) -> str:
        return '\n'

    def inline_html(self, token: Dict[str, Any], state: BlockState) -> str:
        # rst does not support inline html
        return ''

    def paragraph(self, token: Dict[str, Any], state: BlockState) -> str:
        children = token['children']
        if len(children) == 1 and children[0]['type'] == 'image':
            image = children[0]
            attrs = image['attrs']
            title = attrs.get('title')
            alt = self.render_children(image, state)
            text = '.. figure:: ' + attrs['url']
            if title:
                text += '\n   :alt: ' + title
            text += '\n\n' + indent(alt, '   ')
        else:
            text = self.render_tokens(children, state)
        return text + '\n\n'

    def heading(self, token: Dict[str, Any], state: BlockState) -> str:
        attrs = token['attrs']
        text = self.render_children(token, state)
        marker = self.HEADING_MARKERS[attrs['level']]
        return text + '\n' + marker * len(text) + '\n\n'

    def blank_line(self, token: Dict[str, Any], state: BlockState) -> str:
        return ''

    def thematic_break(self, token: Dict[str, Any], state: BlockState) -> str:
        return '* * *\n\n'

    def block_text(self, token: Dict[str, Any], state: BlockState) -> str:
        return self.render_children(token, state)

    def block_code(self, token: Dict[str, Any], state: BlockState) -> str:
        attrs = token.get('attrs', {})
        info = attrs.get('info')
        if info:
            lang = info.split()[0]
            return '.. code:: ' + lang + '\n\n' + indent(token['raw'], '   ') + '\n\n'
        else:
            return '::\n\n' + indent(token['raw'], '    ') + '\n\n'
        return ''

    def block_quote(self, token: Dict[str, Any], state: BlockState) -> str:
        return ''

    def block_html(self, token: Dict[str, Any], state: BlockState) -> str:
        raw = token['raw']
        return '.. raw:: html\n\n' + indent(raw, '   ') + '\n\n'

    def block_error(self, token: Dict[str, Any]) -> str:
        return ''

    def list(self, token: Dict[str, Any], state: BlockState) -> str:
        return ''


def indent(text, spaces):
    out = spaces + text.replace('\n', '\n' + spaces)
