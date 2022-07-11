import os
import sys
import time

ROOT_DIR = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(ROOT_DIR, '..'))


CASES = {}


def load_case(filename):
    if filename == 'readme.txt':
        filepath = os.path.join(ROOT_DIR, '../README.md')
    else:
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
        from mistune3.plugins.speed import speed
        from mistune3.plugins.url import url
        from mistune3.plugins.formatting import strikethrough, mark, insert, subscript
        from mistune3.plugins.task_lists import task_lists
        from mistune3.plugins.table import table
        from mistune3.plugins.footnotes import footnotes
        from mistune3.plugins.def_list import def_list
        from mistune3.plugins.abbr import abbr
        from mistune3.plugins.math import math
        from mistune3.plugins.ruby import ruby
        from mistune3.directives import Admonition, DirectiveToc, DirectiveInclude

        parsers[f'mistune ({mistune3.__version__})'] = mistune3.html
        parsers['mistune (speed)'] = mistune3.create_markdown(
            escape=False,
            plugins=[speed],
        )
        parsers['mistune (full)'] = mistune3.create_markdown(
            escape=False,
            plugins=[
                url, strikethrough, mark, insert, subscript, task_lists,
                table, footnotes, def_list, abbr, math, ruby,
                Admonition(), DirectiveToc(), DirectiveInclude(),
            ],
        )
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
    cases = [
        # block
        'axt',
        'setext',
        'normal_ul',
        'insane_ul',
        'normal_ol',
        'insane_ol',
        'blockquote',
        'blockhtml',
        'fenced',
        'paragraph',

        # inline
        'emphasis',
        'auto_links',
        'std_links',
        'ref_links',

        'readme',
    ]
    if len(sys.argv) > 1:
        benchmarks(sys.argv[1:])
    else:
        benchmarks(cases)
