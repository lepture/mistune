import os
import sys
import time

ROOT_DIR = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(ROOT_DIR, '..'))


CASES = {}


def load_case(filename):
    filepath = os.path.join(ROOT_DIR, 'cases', filename)
    with open(filepath, 'r') as f:
        content = f.read()

    name = filename.replace('.txt', '')
    CASES[name] = content
    return content


def run_case(method, content, count=100):
    # ignore first trigger
    method(content)

    start = time.time()

    while count > 0:
        method(content)
        count -= 1

    duration = time.time() - start
    return duration * 1000


def get_markdown_parsers():
    parsers = {}

    try:
        import mistune3
        parsers[f'mistune ({mistune3.__version__})'] = mistune3.html
    except ImportError:
        pass

    try:
        import mistune
        if hasattr(mistune, 'html'):
            func = mistune.html
        else:
            func = mistune.markdown
        parsers[f'mistune ({mistune.__version__})'] = func
    except ImportError:
        pass

    try:
        import markdown
        parsers[f'markdown ({markdown.__version__})'] = markdown.markdown
    except ImportError:
        pass

    try:
        import mistletoe
        parsers[f'mistletoe ({mistletoe.__version__})'] = mistletoe.markdown
    except ImportError:
        pass

    return parsers


def benchmarks(cases, count=100):
    methods = get_markdown_parsers()
    for name in cases:
        content = load_case(name + '.txt')

        for md_name in methods:
            func = methods[md_name]
            duration = run_case(func, content, count)
            print(f'{md_name} - {name}: {duration}ms')


if __name__ == '__main__':
    benchmarks([
        'axt',
        'setext',
        'ul',
        'ol',
        'blockquote',
        'fenced',
        'elements',
        'paragraph',
    ])
