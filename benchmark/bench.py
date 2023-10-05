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

    import mistune
    from mistune.directives import (
        RSTDirective, Admonition, TableOfContents, Include,
    )

    parsers[f'mistune ({mistune.__version__})'] = mistune.html
    parsers[f'mistune (slow)'] = mistune.create_markdown(escape=False)
    parsers[f'mistune (fast)'] = mistune.create_markdown(
        escape=False, plugins=['speedup'])
    parsers['mistune (full)'] = mistune.create_markdown(
        escape=False,
        plugins=[
            'url', 'abbr', 'ruby',
            'strikethrough', 'mark', 'insert', 'subscript', 'superscript',
            'footnotes', 'def_list', 'math', 'table', 'task_lists',
            RSTDirective([
                Admonition(),
                TableOfContents(),
                Include(),
            ]),
            'speedup',
        ],
    )

    try:
        import mistune_v1
        parsers[f'mistune ({mistune_v1.__version__})'] = mistune_v1.markdown
    except ImportError:
        pass

    try:
        import markdown
        parsers[f'markdown ({markdown.__version__})'] = markdown.markdown
    except ImportError:
        pass

    try:
        from markdown2 import Markdown, __version__ as m2v
        markdowner = Markdown()
        parsers[f'markdown2 ({m2v})'] = markdowner.convert
    except ImportError:
        pass

    try:
        import mistletoe
        parsers[f'mistletoe ({mistletoe.__version__})'] = mistletoe.markdown
    except ImportError:
        pass

    try:
        from markdown_it import MarkdownIt, __version__ as mitv
        md = MarkdownIt()
        parsers[f'markdown_it ({mitv})'] = md.render
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
        'atx',
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
