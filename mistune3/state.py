import re

_LINE_END = re.compile(r'\n|$')


class BlockState:
    def __init__(self, parent=None):
        self.src = ''
        self.tokens = []

        # current cursor position
        self.cursor = 0
        self.cursor_max = 0

        # for list and block quote chain
        self.list_tight = True
        self.parent = parent

        # for saving def references
        if parent:
            self.env = parent.env
        else:
            self.env = {'ref_links': {}}

    def process(self, src):
        self.src = src
        self.cursor_max = len(src)

    def find_line_end(self):
        m = _LINE_END.search(self.src, self.cursor)
        return m.end()

    def get_text(self, end_pos):
        return self.src[self.cursor:end_pos]

    def match(self, regex):
        return regex.match(self.src, self.cursor)

    def last_token(self):
        if self.tokens:
            return self.tokens[-1]

    def prepend_token(self, token):
        self.tokens.insert(len(self.tokens) - 1, token)

    def append_token(self, token):
        self.tokens.append(token)

    def add_paragraph(self, text):
        last_token = self.last_token()
        if last_token and last_token['type'] == 'paragraph':
            last_token['text'] += text
        else:
            self.tokens.append({'type': 'paragraph', 'text': text})

    def append_paragraph(self):
        last_token = self.last_token()
        if last_token and last_token['type'] == 'paragraph':
            pos = self.find_line_end()
            last_token['text'] += self.get_text(pos)
            return pos

    def depth(self):
        d = 0
        parent = self.parent
        while parent:
            d += 1
            parent = parent.parent
        return d


class InlineState:
    def __init__(self, env):
        self.env = env
        self.src = ''
        self.tokens = []
        self.in_image = False
        self.in_link = False
        self.in_emphasis = False
        self.in_strong = False

    def insert_token(self, token):
        self.tokens.insert(len(self.tokens) - 1, token)

    def add_token(self, token):
        self.tokens.append(token)

    def copy(self):
        state = self.__class__(self.env)
        state.in_image = self.in_image
        state.in_link = self.in_link
        state.in_emphasis = self.in_emphasis
        state.in_strong = self.in_strong
        return state
