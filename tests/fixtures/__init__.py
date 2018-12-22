import os
import re

ROOT = os.path.join(os.path.dirname(__file__))

EXAMPLE_PATTERN = re.compile(
    r'^`{32} example\n'
    r'([\s\S]*?)^\.\n'
    r'([\s\S]*?)^`{32}$|^#{1,6} *(.*)$',
    flags=re.M
)


def load(filename, prefix=None):
    with open(os.path.join(ROOT, filename), 'rb') as f:
        content = f.read()
        text = content.decode('utf-8')

    data = EXAMPLE_PATTERN.findall(text)

    section = None
    count = 0
    for md, html, title in data:
        if title:
            count = 0
            section = title.lower().replace(' ', '_')

        if prefix and not section.startswith(prefix):
            continue

        if md and html:
            count += 1
            n = '%s_%02d' % (section, count)
            md = md.replace(u'\u2192', '\t')
            html = html.replace(u'\u2192', '\t')
            yield n, md, html
