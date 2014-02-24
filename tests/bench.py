
import os
import re
import time

root = os.path.dirname(__file__)

known = []


def listdir(folder):
    folder = os.path.join(root, folder)
    files = os.listdir(folder)
    files = filter(lambda o: o.endswith('.text'), files)
    return files


def mistune_runner(content):
    import mistune
    return mistune.markdown(content)


def misaka_runner(content):
    import misaka
    extensions = (
        misaka.EXT_NO_INTRA_EMPHASIS | misaka.EXT_TABLES |
        misaka.EXT_FENCED_CODE | misaka.EXT_AUTOLINK |
        misaka.EXT_STRIKETHROUGH
    )
    md = misaka.Markdown(misaka.HtmlRenderer(), extensions=extensions)
    return md.render(content)


def bench(runner=None):
    cases = []

    for name in listdir('cases'):
        with open(os.path.join(root, 'cases', name), 'r') as f:
            cases.append(f.read())

    for name in listdir('extra'):
        with open(os.path.join(root, 'extra', name), 'r') as f:
            cases.append(f.read())

    if runner is None:
        runner = mistune_runner

    begin = time.time()
    count = 100
    while count:
        count -= 1
        for text in cases:
            runner(text)

    end = time.time()
    return end - begin

print('misaka', bench(misaka_runner))
print('mistune', bench())
