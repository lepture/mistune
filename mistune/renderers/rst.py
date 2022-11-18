from typing import Dict, Any
from textwrap import indent
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

    def iter_tokens(self, tokens, state):
        prev = None
        for tok in tokens:
            tok['prev'] = prev
            prev = tok
            yield self.render_token(tok, state)

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
        return '--------------\n\n'

    def block_text(self, token: Dict[str, Any], state: BlockState) -> str:
        return self.render_children(token, state) + '\n'

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
        text = indent(self.render_children(token, state), '   ')
        prev = token['prev']
        if prev and prev['type'] != 'paragraph':
            text = '.. \n\n' + text
        return text

    def block_html(self, token: Dict[str, Any], state: BlockState) -> str:
        raw = token['raw']
        return '.. raw:: html\n\n' + indent(raw, '   ') + '\n\n'

    def block_error(self, token: Dict[str, Any], state: BlockState) -> str:
        return ''

    def list(self, token: Dict[str, Any], state: BlockState) -> str:
        attrs = token['attrs']
        if attrs['ordered']:
            children = self._render_ordered_list(token, state)
        else:
            children = self._render_unordered_list(token, state)

        text = ''.join(children)
        parent = token.get('parent')
        if parent:
            if parent['tight']:
                return text
            return text + '\n'
        return strip_end(text) + '\n'

    def _render_list_item(self, parent, item, state):
        leading = parent['leading']
        text = ''
        for tok in item['children']:
            if tok['type'] == 'list':
                tok['parent'] = parent
            text += self.render_token(tok, state)

        lines = text.splitlines()
        text = lines[0] + '\n'
        prefix = ' ' * len(leading)
        for line in lines[1:]:
            if line:
                text += prefix + line + '\n'
            else:
                text += '\n'
        return leading + text

    def _render_ordered_list(self, token, state):
        attrs = token['attrs']
        start = attrs.get('start', 1)
        for item in token['children']:
            leading = str(start) + token['bullet'] + ' '
            parent = {
                'leading': leading,
                'tight': token['tight'],
            }
            yield self._render_list_item(parent, item, state)
            start += 1

    def _render_unordered_list(self, token, state):
        parent = {
            'leading': token['bullet'] + ' ',
            'tight': token['tight'],
        }
        for item in token['children']:
            yield self._render_list_item(parent, item, state)
