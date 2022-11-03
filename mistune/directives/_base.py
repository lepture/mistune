import re


class DirectiveParser:
    NAME = 'directive'

    @staticmethod
    def parse_name(m: re.Match):
        raise NotImplementedError()

    @staticmethod
    def parse_title(m: re.Match):
        raise NotImplementedError()

    @staticmethod
    def parse_content(m: re.Match):
        raise NotImplementedError()

    @classmethod
    def parse_tokens(cls, block, text, state):
        if state.depth() >= block.max_nested_level - 1:
            rules = list(block.rules)
            rules.remove(cls.NAME)
        else:
            rules = block.rules
        child = state.child_state(text)
        block.parse(child, rules)
        return child.tokens

    @staticmethod
    def parse_options(m: re.Match):
        text = m.group('options')
        if not text.strip():
            return []

        options = []
        for line in re.split(r'\n+', text):
            line = line.strip()[1:]
            if not line:
                continue
            i = line.find(':')
            k = line[:i]
            v = line[i + 1:].strip()
            options.append((k, v))
        return options


class BaseDirective:
    parser = DirectiveParser
    directive_pattern = None
    register_before = None

    def __init__(self, plugins):
        self._methods = {}
        self.__plugins = plugins

    def register(self, name, fn):
        self._methods[name] = fn

    def parse_method(self, name, block, m, state):
        method = self._methods.get(name)
        if method:
            try:
                token = method(block, m, state)
            except ValueError as e:
                token = {'type': 'block_error', 'raw': str(e)}
        else:
            text = m.group(0)
            token = {
                'type': 'block_error',
                'raw': text,
            }

        if isinstance(token, list):
            for tok in token:
                state.append_token(tok)
        else:
            state.append_token(token)
        return token

    def parse_directive(self, block, m, state):
        raise NotImplementedError()

    def __call__(self, md):
        md.block.register(
            self.parser.NAME,
            self.directive_pattern,
            self.parse_directive,
            before=self.register_before,
        )
        for plugin in self.__plugins:
            plugin.parser = self.parser
            plugin(self, md)


class DirectivePlugin:
    def __init__(self):
        self.parser = None

    def parse_options(self, m: re.Match):
        return self.parser.parse_options(m)

    def parse_name(self, m: re.Match):
        return self.parser.parse_name(m)

    def parse_title(self, m: re.Match):
        return self.parser.parse_title(m)

    def parse_content(self, m: re.Match):
        return self.parser.parse_content(m)

    def parse_tokens(self, block, text, state):
        return self.parser.parse_tokens(block, text, state)

    def parse(self, block, m, state):
        raise NotImplementedError()

    def __call__(self, md):
        raise NotImplementedError()
