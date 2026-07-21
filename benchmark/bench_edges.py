"""Benchmark adversarial Markdown inputs.

Run one case with:

    python benchmark/bench_edges.py --case blank-list-continuations

The ``normalized`` column is the time growth divided by the input-size
growth.  Values near 1 indicate linear scaling; values near 2 indicate that
doubling the input takes roughly four times as long.
"""

from __future__ import annotations

import argparse
import statistics
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class EdgeCase:
    name: str
    category: str
    generate: Callable[[int], str]
    make_markdown: Callable[[str], object]
    sizes: tuple[int, ...]


@dataclass(frozen=True)
class Result:
    case: str
    renderer: str
    size: int
    bytes: int
    best: float
    mean: float
    growth: Optional[float]
    normalized_growth: Optional[float]


def markdown_factory(renderer: str = "html", plugins: Optional[list[str]] = None) -> Callable[[str], object]:
    def make_markdown(_renderer: str = renderer, _plugins: Optional[list[str]] = plugins):
        import mistune

        return mistune.create_markdown(renderer=_renderer, escape=False, plugins=_plugins)

    return make_markdown


CORE = markdown_factory()
SPOILER = markdown_factory(plugins=["spoiler"])
MATH = markdown_factory(plugins=["math"])
FOOTNOTES = markdown_factory(plugins=["footnotes"])
GITHUB = markdown_factory(plugins=["table", "task_lists"])


EDGE_CASES = {
    "deep-blockquote": EdgeCase("deep-blockquote", "containers", lambda n: "> " * n + "text\n", CORE, (100, 1000, 10000)),
    "deep-list": EdgeCase("deep-list", "containers", lambda n: "- " * n + "text\n", CORE, (100, 1000, 10000)),
    "blockquote-depth-boundary": EdgeCase(
        "blockquote-depth-boundary", "containers", lambda n: "> " * n + "text\n", CORE, (99, 100, 101, 1000)
    ),
    "alternating-containers": EdgeCase(
        "alternating-containers", "containers", lambda n: "> - " * n + "text\n", CORE, (64, 128, 256)
    ),
    "deep-block-spoiler": EdgeCase(
        "deep-block-spoiler", "containers", lambda n: ">! " * n + "text\n", SPOILER, (100, 1000, 10000)
    ),
    "unmatched-links": EdgeCase("unmatched-links", "inline", lambda n: "[" * n + "\n", CORE, (1000, 10000, 100000)),
    "nested-link-labels": EdgeCase(
        "nested-link-labels", "inline", lambda n: "[" * n + "text" + "]" * n + "(/url)\n", CORE, (200, 1000, 5000)
    ),
    "nested-image-labels": EdgeCase(
        "nested-image-labels", "inline", lambda n: "![" * n + "text" + "](/url)" * n + "\n", CORE, (200, 1000, 5000)
    ),
    "dense-emphasis": EdgeCase("dense-emphasis", "inline", lambda n: "*a" * n + "\n", CORE, (1000, 10000, 100000)),
    "long-code-span-runs": EdgeCase(
        "long-code-span-runs", "inline", lambda n: "`" * n + "text" + "`" * (n - 1) + "\n", CORE, (1000, 10000, 100000)
    ),
    "successful-long-code-span": EdgeCase(
        "successful-long-code-span", "inline", lambda n: "`" * n + "text" + "`" * n + "\n", CORE, (1000, 10000, 100000)
    ),
    "many-wrong-code-runs": EdgeCase(
        "many-wrong-code-runs", "inline", lambda n: "``start " + "`x" * n + " ``\n", CORE, (1000, 10000, 100000)
    ),
    "link-label-long-code-runs": EdgeCase(
        "link-label-long-code-runs",
        "inline",
        lambda n: "[" + "`" * n + "text" + "`" * (n - 1) + "](/url)\n",
        CORE,
        (1000, 10000, 100000),
    ),
    "nested-text-directives": EdgeCase(
        "nested-text-directives", "inline", lambda n: ":x[" * n + "text" + "]" * n + "\n", CORE, (100, 500, 1000)
    ),
    "invalid-inline-math-closers": EdgeCase(
        "invalid-inline-math-closers", "inline", lambda n: "$x" + "$5" * n + "\n", MATH, (1000, 5000, 10000)
    ),
    "long-list-spacing": EdgeCase(
        "long-list-spacing", "blocks", lambda n: "- " + " " * n + "text\n", CORE, (1000, 10000, 100000)
    ),
    "blank-list-continuations": EdgeCase(
        "blank-list-continuations", "blocks", lambda n: "- first\n" + "\n" * n + "  last\n", CORE, (1000, 5000, 10000)
    ),
    "list-marker-interrupt": EdgeCase(
        "list-marker-interrupt", "blocks", lambda n: "paragraph\n1. " + " " * n + "\n", CORE, (1000, 10000, 100000)
    ),
    "unclosed-fence": EdgeCase(
        "unclosed-fence", "blocks", lambda n: "```\n" + "line\n" * n, CORE, (1000, 5000, 10000)
    ),
    "lazy-blockquote-lines": EdgeCase(
        "lazy-blockquote-lines", "blocks", lambda n: "> first\n" + "lazy continuation\n" * n, CORE, (1000, 5000, 10000)
    ),
    "many-empty-blockquotes": EdgeCase(
        "many-empty-blockquotes", "blocks", lambda n: ">\n" * n, CORE, (1000, 5000, 10000)
    ),
    "task-list-lines": EdgeCase(
        "task-list-lines", "blocks", lambda n: "- [x] item\n" * n, GITHUB, (1000, 5000, 10000)
    ),
    "ordered-list-markers": EdgeCase(
        "ordered-list-markers", "blocks", lambda n: "123456789. item\n" * n, CORE, (1000, 5000, 10000)
    ),
    "nested-directives": EdgeCase(
        "nested-directives", "containers", lambda n: ":::note\n" * n + "text\n" + ":::\n" * n, CORE, (64, 128, 256)
    ),
    "fenced-directive-attributes": EdgeCase(
        "fenced-directive-attributes", "blocks", lambda n: "```{note}\n" + ":key: value\n" * n + "```\n", CORE, (1000, 5000, 10000)
    ),
    "unclosed-reference-title": EdgeCase(
        "unclosed-reference-title", "references", lambda n: '[x]: /url "\n' + "line\n" * n + "\n[x]\n", CORE, (1000, 5000, 10000)
    ),
    "footnote-blank-continuations": EdgeCase(
        "footnote-blank-continuations",
        "references",
        lambda n: "[^x]: first\n" + "\n" * n + "  second\n\n[^x]\n",
        FOOTNOTES,
        (1000, 5000, 10000),
    ),
    "multiline-reference-label": EdgeCase(
        "multiline-reference-label", "references", lambda n: "[label\n" + "part\n" * n + "]: /url\n", CORE, (1000, 5000, 10000)
    ),
    "many-reference-definitions": EdgeCase(
        "many-reference-definitions", "references", lambda n: "".join("[x%d]: /url\n" % i for i in range(n)), CORE, (1000, 5000, 10000)
    ),
    "nested-html-containers": EdgeCase(
        "nested-html-containers", "html", lambda n: "<div>\n" * n + "</div>\n" * n, CORE, (64, 128, 256)
    ),
    "long-html-tag-name": EdgeCase(
        "long-html-tag-name", "html", lambda n: "<" + "x" * n + ">\ntext\n</" + "x" * n + ">\n", CORE, (1000, 10000, 100000)
    ),
    "html-many-attributes": EdgeCase(
        "html-many-attributes",
        "html",
        lambda n: '<div ' + " ".join('data-x%d="v"' % i for i in range(n)) + ">\ntext\n</div>\n",
        CORE,
        (100, 1000, 5000),
    ),
    "wide-table": EdgeCase(
        "wide-table",
        "tables",
        lambda n: "| " + " | ".join(["cell"] * n) + " |\n| " + " | ".join(["---"] * n) + " |\n",
        markdown_factory(plugins=["table"]),
        (100, 1000, 5000),
    ),
}


def benchmark_case(edge_case: EdgeCase, sizes: list[int], iterations: int, warmup: int, renderer: str) -> list[Result]:
    markdown = edge_case.make_markdown(renderer)
    results = []
    previous_size = None
    previous_mean = None
    for size in sizes:
        text = edge_case.generate(size)
        for _ in range(warmup):
            markdown(text)

        timings = []
        for _ in range(iterations):
            started = time.perf_counter()
            markdown(text)
            timings.append(time.perf_counter() - started)

        mean = statistics.fmean(timings)
        growth = None if previous_mean is None else mean / previous_mean
        normalized = None if growth is None else growth / (size / previous_size)
        results.append(Result(edge_case.name, renderer, size, len(text.encode()), min(timings), mean, growth, normalized))
        previous_size = size
        previous_mean = mean
    return results


def parse_sizes(value: str) -> list[int]:
    try:
        sizes = sorted({int(item) for item in value.split(",")})
    except ValueError as exc:
        raise argparse.ArgumentTypeError("sizes must be comma-separated integers") from exc
    if not sizes or sizes[0] < 1:
        raise argparse.ArgumentTypeError("sizes must contain positive integers")
    return sizes


def format_duration(seconds: float) -> str:
    if seconds < 0.001:
        return "%.1fus" % (seconds * 1_000_000)
    if seconds < 1:
        return "%.2fms" % (seconds * 1_000)
    return "%.3fs" % seconds


def print_results(results: list[Result]) -> None:
    headers = ["case", "renderer", "size", "bytes", "best", "mean", "ns/unit", "growth", "normalized"]
    rows = []
    for result in results:
        rows.append(
            [
                result.case,
                result.renderer,
                str(result.size),
                str(result.bytes),
                format_duration(result.best),
                format_duration(result.mean),
                "%.1f" % (result.mean / result.size * 1_000_000_000),
                "-" if result.growth is None else "%.2fx" % result.growth,
                "-" if result.normalized_growth is None else "%.2fx" % result.normalized_growth,
            ]
        )
    widths = [len(header) for header in headers]
    for row in rows:
        widths = [max(width, len(value)) for width, value in zip(widths, row)]
    print("  ".join(header.ljust(width) for header, width in zip(headers, widths)))
    print("  ".join("-" * width for width in widths))
    for row in rows:
        print("  ".join(value.ljust(width) for value, width in zip(row, widths)))


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark adversarial Markdown parser inputs.")
    parser.add_argument("--case", default="all", choices=["all", *EDGE_CASES])
    parser.add_argument("--category", default="all", choices=["all", *sorted({case.category for case in EDGE_CASES.values()})])
    parser.add_argument("--sizes", type=parse_sizes, help="override comma-separated case sizes")
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--renderer", choices=["html", "ast"], default="html")
    args = parser.parse_args()
    if args.iterations < 1 or args.warmup < 0:
        raise SystemExit("iterations must be at least 1 and warmup must not be negative")
    if args.case != "all" and args.category != "all":
        raise SystemExit("--case and --category cannot be combined")

    if args.case != "all":
        cases = [EDGE_CASES[args.case]]
    elif args.category != "all":
        cases = [case for case in EDGE_CASES.values() if case.category == args.category]
    else:
        cases = list(EDGE_CASES.values())

    results = [
        result
        for case in cases
        for result in benchmark_case(case, args.sizes or list(case.sizes), args.iterations, args.warmup, args.renderer)
    ]
    print_results(results)


if __name__ == "__main__":
    main()
