import argparse
import sys
from typing import TYPE_CHECKING, Optional

from . import __version__ as version
from . import create_markdown
from .renderers.markdown import MarkdownRenderer
from .renderers.rst import RSTRenderer

if TYPE_CHECKING:
    from .core import BaseRenderer
    from .markdown import Markdown


def _md(args: argparse.Namespace) -> "Markdown":
    renderer = args.renderer
    if args.plugin:
        plugins = args.plugin
    elif renderer == "rst":
        # RSTRenderer does not provide render methods for any of the
        # default plugins. Loading them anyway makes the documented
        # `python -m mistune -f README.md -r rst` command crash with a
        # raw AttributeError on any document containing a footnote or
        # a table.
        plugins = []
    elif renderer == "markdown":
        # MarkdownRenderer supports strikethrough and tables, but not
        # footnotes: reformatting a document containing a footnote would
        # crash the same way.
        plugins = ["strikethrough", "table"]
    else:
        # default plugins
        plugins = ["strikethrough", "footnotes", "table"]

    if renderer == "rst":
        renderer = RSTRenderer()
    elif renderer == "markdown":
        renderer = MarkdownRenderer()
    else:
        renderer = args.renderer
    return create_markdown(
        escape=args.escape,
        hard_wrap=args.hardwrap,
        renderer=renderer,
        plugins=plugins,
    )


def _output(text: str, args: argparse.Namespace) -> None:
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        _ensure_stdout_utf8()
        print(text)


CMD_HELP = """Mistune, a sane and fast Python Markdown parser.

Examples:

    $ python -m mistune -m "Hi **Markdown**"
    <p>Hi <strong>Markdown</strong></p>

    $ python -m mistune -f README.md
    <p>...

    $ cat README.md | python -m mistune
    <p>...
"""


def cli() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m mistune",
        description=CMD_HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-m",
        "--message",
        help="the Markdown message to convert",
    )
    parser.add_argument(
        "-f",
        "--file",
        help="the Markdown file to convert",
    )
    parser.add_argument(
        "-p",
        "--plugin",
        metavar="NAME",
        action="extend",
        nargs="+",
        help="specify a plugin to use",
    )
    parser.add_argument(
        "--escape",
        action="store_true",
        help="enable the escape option",
    )
    parser.add_argument(
        "--hardwrap",
        action="store_true",
        help="enable the hardwrap option",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="write the rendered result into file",
    )
    parser.add_argument(
        "-r",
        "--renderer",
        default="html",
        help="specify the output renderer",
    )
    parser.add_argument("--version", action="version", version="mistune " + version)
    args = parser.parse_args()

    message = args.message
    if not message and not args.file:
        message = read_stdin()

    if message:
        md = _md(args)
        text = md(message)
        assert isinstance(text, str)
        _output(text, args)
    elif args.file:
        md = _md(args)
        text = md.read(args.file)[0]
        assert isinstance(text, str)
        _output(text, args)
    else:
        print("You must specify a message or file")
        sys.exit(1)


def _ensure_stdout_utf8() -> None:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8")


def read_stdin() -> Optional[str]:
    is_stdin_pipe = not sys.stdin.isatty()
    if is_stdin_pipe:
        return sys.stdin.read()
    else:
        return None


if __name__ == "__main__":
    cli()
