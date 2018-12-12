import os
import re

ROOT = os.path.join(os.path.dirname(__file__))


def load(filename):
    with open(os.path.join(ROOT, filename), 'rb') as f:
        content = f.read()
        content = content.decode('utf-8')

    sections = re.split(r'## (.*?)\n+', content)[1:]
    for i in range(0, len(sections), 2):
        name = sections[i]
        index = 0
        for text, html in parse_cases(sections[i + 1]):
            prefix = '%s_%02d' % (name, index)
            yield prefix, text, html
            index += 1


def parse_cases(text):
    cases = text.split('\n....')
    for s in cases:
        s = s.strip()
        if s:
            yield s.split('\n.\n')
