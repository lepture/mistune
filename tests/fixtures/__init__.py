import os
import re
import json
from typing import Any, Iterable, Tuple

ROOT = os.path.join(os.path.dirname(__file__))

EXAMPLE_PATTERN = re.compile(
    r'^`{32} example\n([\s\S]*?)'
    r'^\.\n([\s\S]*?)'
    r'^`{32}$|^#{1,6} *(.*)$',
    flags=re.M
)


def load_ast(filename: str) -> Any:
    with open(os.path.join(ROOT, 'ast', filename)) as f:
        return json.load(f)


def load_json(filename: str) -> Any:
    with open(os.path.join(ROOT, filename)) as f:
        return json.load(f)


def load_examples(filename: str) -> Iterable[Tuple[str, str, str]]:
    if filename.endswith('.json'):
        data = load_json(filename)
        for item in data:
            section = item['section'].lower().replace(' ', '_')
            n = '%s_%03d' % (section, item['example'])
            yield n, item['markdown'], item['html']
    else:
        with open(os.path.join(ROOT, filename), 'rb') as f:
            content = f.read()
            s = content.decode('utf-8')
            yield from parse_examples(s)



def parse_examples(text: str) -> Iterable[Tuple[str, str, str]]:
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
