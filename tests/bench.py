# coding: utf-8

import os
import time
import functools


class benchmark(object):
    suites = []

    def __init__(self, name):
        self._name = name

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(text, loops=1000):
            start = time.clock()
            while loops:
                func(text)
                loops -= 1
            end = time.clock()
            return end - start
        # register
        benchmark.suites.append((self._name, wrapper))
        return wrapper

    @classmethod
    def bench(cls, text, loops=1000):
        print('Parsing the Markdown Syntax document %d times...' % loops)
        for name, func in cls.suites:
            try:
                total = func(text, loops=loops)
                print('{0}: {1}'.format(name, total))
            except ImportError:
                print('{0} is not available'.format(name))


@benchmark('mistune')
def benchmark_mistune(text):
    import mistune
    mistune.markdown(text)


@benchmark('misaka')
def benchmark_misaka(text):
    import misaka as m
    # mistune has all these features
    extensions = (
        m.EXT_NO_INTRA_EMPHASIS | m.EXT_FENCED_CODE | m.EXT_AUTOLINK |
        m.EXT_TABLES | m.EXT_STRIKETHROUGH
    )
    md = m.Markdown(m.HtmlRenderer(), extensions=extensions)
    md.render(text)


@benchmark('markdown2')
def benchmark_markdown2(text):
    import markdown2
    extras = ['code-friendly', 'fenced-code-blocks', 'footnotes']
    markdown2.markdown(text, extras=extras)


@benchmark('markdown')
def benchmark_markdown(text):
    import markdown
    markdown.markdown(text, ['extra'])


@benchmark('cMarkdown')
def benchmark_cMarkdown(text):
    import cMarkdown
    cMarkdown.markdown(text)


@benchmark('discount')
def benchmark_discount(text):
    import discount
    discount.Markdown(text).get_html_content()


@benchmark('hoep')
def benchmark_hoep(text):
    import hoep as m
    # mistune has all these features
    extensions = (
        m.EXT_NO_INTRA_EMPHASIS | m.EXT_FENCED_CODE | m.EXT_AUTOLINK |
        m.EXT_TABLES | m.EXT_STRIKETHROUGH | m.EXT_FOOTNOTES
    )
    md = m.Hoep(extensions=extensions)
    md.render(text.decode('utf-8'))


if __name__ == '__main__':
    root = os.path.dirname(__file__)
    filepath = os.path.join(
        root, 'fixtures/normal', 'markdown_documentation_syntax.text'
    )
    with open(filepath, 'r') as f:
        text = f.read()

    benchmark.bench(text)
