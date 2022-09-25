import sys
import argparse
from . import (
    create_markdown,
    __version__ as version
)


def _md(args):
    if args.plugin:
        plugins = args.plugin
    else:
        # default plugins
        plugins = ['strikethrough', 'footnotes', 'table', 'speedup']
    return create_markdown(
        escape=args.escape,
        hard_wrap=args.hardwrap,
        renderer=args.renderer,
        plugins=plugins,
    )


def _output(text, args):
    if args.output:
        with open(args.output, 'w') as f:
            f.write(text)
    else:
        print(text)


CMD_HELP = '''Mistune, a sane and fast python markdown parser.

Here are some use cases of the command line tool:

    $ python -m mistune -m "Hi **Markdown**"
    <p>Hi <strong>Markdown</strong></p>

    $ python -m mistune -f README.md
    <p>...
'''


def cli():
    parser = argparse.ArgumentParser(
        prog='python -m mistune',
        description=CMD_HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '-m', '--message',
        help='the markdown message to convert',
    )
    parser.add_argument(
        '-f', '--file',
        help='the markdown file to convert',
    )
    parser.add_argument(
        '-p', '--plugin',
        metavar='NAME',
        action='extend',
        nargs='+',
        help='specifiy a plugin to use',
    )
    parser.add_argument(
        '--escape',
        action='store_true',
        help='turn on escape option',
    )
    parser.add_argument(
        '--hardwrap',
        action='store_true',
        help='turn on hardwrap option',
    )
    parser.add_argument(
        '-o', '--output',
        help='write the rendered result into file',
    )
    parser.add_argument(
        '-r', '--renderer',
        default='html',
        help='specify the output renderer',
    )
    parser.add_argument('--version', action='version', version='mistune ' + version)
    args = parser.parse_args()

    if not args.message and not args.file:
        print('You MUST specify a message or file')
        return sys.exit(1)

    if args.message:
        md = _md(args)
        text = md(args.message)
        _output(text, args)
    elif args.file:
        md = _md(args)
        text = md.read(args.file)[0]
        _output(text, args)


if __name__ == '__main__':
    cli()
