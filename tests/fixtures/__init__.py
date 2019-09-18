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


def load_examples(filename):
    with open(os.path.join(ROOT, filename), 'rb') as f:
        content = f.read()
        s = content.decode('utf-8')
        return parse_examples(s)


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
