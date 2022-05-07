import re


class Table:
    def __call__(self, md):
        md.block.register_rule()


class Footnotes:
    INLINE_FOOTNOTE = r'\[\^(' + LINK_LABEL + r')\]'
    DEF_FOOTNOTE = re.compile(r'( {0,3})\[\^(' + LINK_LABEL + r')\]:')

    @staticmethod
    def parse_def_footenote(block, line, cursor, state):
        pass

    @staticmethod
    def parse_inline_footnote(inline, m, state):
        pass

    @staticmethod
    def render_footnote_ref():
        pass

    def __call__(self, md):
        md.block.register_rule(
            name='def_footenote',
            func=self.parse_def_footenote,
            before='def_link',  # parse def footnote at first
        )
        md.inline.register_rule(
            name='footnote',
            pattern=self.INLINE_FOOTNOTE,
            func=self.parse_inline_footnote,
            before='link',
        )
        if md.renderer and md.renderer.NAME == 'html':
            md.renderer.register('footnote_ref', self.render_footnote_ref)
