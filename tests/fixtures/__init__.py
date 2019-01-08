import os
import re
import json

ROOT = os.path.join(os.path.dirname(__file__))

EXAMPLE_PATTERN = re.compile(
    r'^`{32} example\n([\s\S]*?)'
    r'^\.\n([\s\S]*?)'
    r'^`{32}$|^#{1,6} *(.*)$',
    flags=re.M
)


def load_json(filename):
    with open(os.path.join(ROOT, 'json', filename)) as f:
        return json.load(f)


def load_cases(TestClass, assert_method, filename, ignore=None):
    with open(os.path.join(ROOT, filename), 'rb') as f:
        content = f.read()
        s = content.decode('utf-8')
    parse_cases(TestClass, assert_method, s, ignore)


def parse_cases(TestClass, assert_method, s, ignore=None):
    def attach_case(n, text, html):
        def method(self):
            assert_method(self, n, text, html)

        name = 'test_{}'.format(n)
        method.__name__ = name
        setattr(TestClass, name, method)

    for n, text, html in parse_examples(s):
        if ignore and ignore(n):
            continue
        attach_case(n, text, html)


def parse_examples(text):
    data = EXAMPLE_PATTERN.findall(text)

    section = None
    count = 0
    for md, html, title in data:
        if title:
            count = 0
            section = title.lower().replace(' ', '_')

        if md and html:
            count += 1
            n = '%s_%03d' % (section, count)
            md = md.replace(u'\u2192', '\t')
            html = html.replace(u'\u2192', '\t')
            yield n, md, html
