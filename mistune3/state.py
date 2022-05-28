import re

_LINE_END = re.compile(r'\n|$')


class BlockState:
    def __init__(self, parent=None):
        self.src = ''
        self.tokens = []

        # current cursor position
        self.cursor = 0
        self.cursor_max = 0

        # current cursor at line
        self.line = 0

        # nested state
        self.line_root = 0

        # for list and block quote chain
        self.in_block = None
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

    def get_line(self):
        end_pos = self.find_line_end()
        text = self.get_text(end_pos)
        self.cursor = end_pos
        return text

    def get_text(self, end_pos):
        return self.src[self.cursor:end_pos]

    def match(self, regex):
        return regex.match(self.src, self.cursor)

    def prev_token(self):
        if self.tokens:
            return self.tokens[-1]

    def add_token(self, token, line_count, start_line=None):
        if start_line is None:
            start_line = self.line

        end_line = start_line + line_count
        token['start_line'] = self.line_root + start_line
        token['end_line'] = self.line_root + end_line

        if end_line < self.line:
            last_token = self.tokens.pop()
            self.tokens.append(token)
            self.tokens.append(last_token)
        else:
            self.tokens.append(token)
            self.line = end_line

    def append_paragraph(self):
        prev_token = self.prev_token()
        if prev_token and prev_token['type'] == 'paragraph':
            prev_token['text'] += self.get_line()
            prev_token['end_line'] =+ 1
            self.line += 1
            return True

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

    def scan_delims(self, start, split_marker):
        left_franking = True
        right_franking = True
        if start > 0:
            prev_char = self.src[start - 1]
        else:
            prev_char = ' '
        marker = self.src[start]

        pos = start + 1
        pos_max = len(self.src)
        while pos < pos_max and this.src[pos] == marker:
            pos += 1

        marker_count = pos - start
        if pos < pos_max:
            pos_char = this.src[pos]
        else:
            pos_char = ' '


    def copy(self):
        state = self.__class__(self.env)
        state.in_image = self.in_image
        state.in_link = self.in_link
        state.in_emphasis = self.in_emphasis
        state.in_strong = self.in_strong
        return state
