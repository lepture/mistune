import re

inline_tags = [
    'a', 'em', 'strong', 'small', 's', 'cite', 'q', 'dfn', 'abbr', 'data',
    'time', 'code', 'var', 'samp', 'kbd', 'sub', 'sup', 'i', 'b', 'u', 'mark',
    'ruby', 'rt', 'rp', 'bdi', 'bdo', 'span', 'br', 'wbr', 'ins', 'del',
    'img', 'font',
]
_tag_end = r'(?!:/|[^\w\s@]*@)\b'
_tag_attr = r'''\s*[a-zA-Z\-](?:\=(?:"[^"]*"|'[^']*'|[^\s'">]+))?'''
_block_tag = r'(?!(?:%s)\b)\w+%s' % ('|'.join(inline_tags), _tag_end)


def _pure_pattern(regex):
    pattern = regex.pattern
    if pattern.startswith('^'):
        pattern = pattern[1:]
    return pattern


class BlockGrammar(object):
    """Grammars for block level tokens."""

    def_links = re.compile(
        r' *\[([^^\]]+)\]: *'  # [key]:
        r'<?([^\s>]+)>?'  # <link> or link
        r'(?: +["(]([^\n]+)[")])? *(?:\n+|$)'
    )
    def_footnotes = re.compile(
        r'\[\^([^\]]+)\]: *('
        r'[^\n]*(?:\n+|$)'  # [^key]:
        r'(?: {1,}[^\n]*(?:\n+|$))*'
        r')'
    )

    newline = re.compile(r'\n+')
    block_code = re.compile(r'( {4}[^\n]+\n*)+')
    fences = re.compile(
        r' *(`{3,}|~{3,}) *(\S+)? *\n'  # ```lang
        r'([\s\S]+?)\s*'
        r'\1 *(?:\n+|$)'  # ```
    )
    hrule = re.compile(r' {0,3}[-*_](?: *[-*_]){2,} *(?:\n+|$)')
    heading = re.compile(r' *(#{1,6}) *([^\n]+?) *#* *(?:\n+|$)')
    lheading = re.compile(r'([^\n]+)\n *(=|-)+ *(?:\n+|$)')
    block_quote = re.compile(r'( *>[^\n]+(\n[^\n]+)*\n*)+')
    list_block = re.compile(
        r'( *)([*+-]|\d+\.) [\s\S]+?'
        r'(?:'
        r'\n+(?=\1?(?:[-*_] *){3,}(?:\n+|$))'  # hrule
        r'|\n+(?=%s)'  # def links
        r'|\n+(?=%s)'  # def footnotes
        r'|\n{2,}'
        r'(?! )'
        r'(?!\1(?:[*+-]|\d+\.) )\n*'
        r'|'
        r'\s*$)' % (
            _pure_pattern(def_links),
            _pure_pattern(def_footnotes),
        )
    )
    list_item = re.compile(
        r'^(( *)(?:[*+-]|\d+\.) [^\n]*'
        r'(?:\n(?!\2(?:[*+-]|\d+\.) )[^\n]*)*)',
        flags=re.M
    )
    list_bullet = re.compile(r'^ *(?:[*+-]|\d+\.) +')
    paragraph = re.compile(
        r'((?:[^\n]+\n?(?!'
        r'%s|%s|%s|%s|%s|%s|%s|%s|%s'
        r'))+)\n*' % (
            _pure_pattern(fences).replace(r'\1', r'\2'),
            _pure_pattern(list_block).replace(r'\1', r'\3'),
            _pure_pattern(hrule),
            _pure_pattern(heading),
            _pure_pattern(lheading),
            _pure_pattern(block_quote),
            _pure_pattern(def_links),
            _pure_pattern(def_footnotes),
            '<' + _block_tag,
        )
    )
    block_html = re.compile(
        r' *(?:%s|%s|%s) *(?:\n{2,}|\s*$)' % (
            r'<!--[\s\S]*?-->',
            r'<(%s)((?:%s)*?)>([\s\S]*?)<\/\1>' % (_block_tag, _tag_attr),
            r'<%s(?:%s)*?\s*\/?>' % (_block_tag, _tag_attr),
        )
    )
    table = re.compile(
        r' *\|(.+)\n *\|( *[-:]+[-| :]*)\n((?: *\|.*(?:\n|$))*)\n*'
    )
    nptable = re.compile(
        r' *(\S.*\|.*)\n *([-:]+ *\|[-| :]*)\n((?:.*\|.*(?:\n|$))*)\n*'
    )
    text = re.compile(r'[^\n]+')


class InlineGrammar(object):
    """Grammars for inline level tokens."""

    escape = re.compile(r'\\(?P<escape1>[\\`*{}\[\]()#+\-.!_>~|])')  # \* \+ \! ....
    inline_html = re.compile(
        r'(?:%s|%s|%s)' % (
            r'<!--[\s\S]*?-->',
            r'<(?P<inline_html1>\w+%s)(?P<inline_html2>(?:%s)*?)\s*>(?P<inline_html3>[\s\S]*?)<\/(?P=inline_html1)>' %
                (_tag_end, _tag_attr),
            r'<\w+%s(?:%s)*?\s*\/?>' % (_tag_end, _tag_attr),
        )
    )
    autolink = re.compile(r'<(?P<autolink1>[^ >]+(?P<autolink2>@|:)[^ >]+)>')
    link = re.compile(
        r'!?\[(?P<link1>'
        r'(?:\[[^^\]]*\]|[^\[\]]|\](?=[^\[]*\]))*'
        r')\]\('
        r'''\s*(?P<link2><)?(?P<link3>[\s\S]*?)(?(link2)>)(?:\s+['"](?P<link4>[\s\S]*?)['"])?\s*'''
        r'\)'
    )
    reflink = re.compile(
        r'!?\[(?P<reflink1>'
        r'(?:\[[^^\]]*\]|[^\[\]]|\](?=[^\[]*\]))*'
        r')\]\s*\[(?P<reflink2>[^^\]]*)\]'
    )
    nolink = re.compile(r'!?\[(?P<nolink1>(?:\[[^\]]*\]|[^\[\]])*)\]')
    url = re.compile(r'''(?P<url1>https?:\/\/[^\s<]+[^<.,:;"')\]\s])''')
    double_emphasis = re.compile(
        r'_{2}(?P<double_emphasis1>[\s\S]+?)_{2}(?!_)'  # __word__
        r'|'
        r'\*{2}(?P<double_emphasis2>[\s\S]+?)\*{2}(?!\*)'  # **word**
    )
    emphasis = re.compile(
        r'\b_(?P<emphasis1>(?:__|[^_])+?)_\b'  # _word_
        r'|'
        r'\*(?P<emphasis2>(?:\*\*|[^\*])+?)\*(?!\*)'  # *word*
    )
    code = re.compile(r'(?P<code1>`+)\s*(?P<code2>[\s\S]*?[^`])\s*(?P=code1)(?!`)')  # `code`
    linebreak = re.compile(r' {2,}\n(?!\s*$)')
    strikethrough = re.compile(r'~~(?=\S)(?P<strikethrough1>[\s\S]*?\S)~~')  # ~~word~~
    footnote = re.compile(r'\[\^(?P<footnote1>[^\]]+)\]')
    text = re.compile(r'[\s\S]+?(?=[\\<!\[_*`~]|https?://| {2,}\n|$)')

    def hard_wrap(self):
        """Grammar for hard wrap linebreak. You don't need to add two
        spaces at the end of a line.
        """
        self.linebreak = re.compile(r' *\n(?!\s*$)')
        self.text = re.compile(
            r'[\s\S]+?(?=[\\<!\[_*`~]|https?://| *\n|$)'
        )
