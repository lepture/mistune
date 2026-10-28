import io
import subprocess
import sys
from contextlib import redirect_stdout
from unittest.mock import patch

import pytest

from mistune.__main__ import cli
from tests import BaseTestCase


class TestCliMessage(BaseTestCase):
    def parse(self, text: str) -> str:
        with patch.object(sys, "argv", ["python -m mistune", "-m", text]):
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli()
        output = buf.getvalue()
        if output.endswith("\n"):
            output = output[:-1]
        return output


TestCliMessage.load_fixtures("cli.txt")


def _run_cli(args, input_text=""):
    return subprocess.run(
        [sys.executable, "-m", "mistune", *args],
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )


@pytest.mark.parametrize(("renderer", "expected_stdout"), [("html", "\n"), ("markdown", "\n\n"), ("rst", "\n\n")])
@pytest.mark.parametrize(
    ("args", "input_text"),
    [(["-m", ""], "ignored **input**"), (["-m", ""], ""), ([], "")],
)
def test_empty_cli_document(renderer, expected_stdout, args, input_text):
    result = _run_cli([*args, "-r", renderer], input_text)
    assert result.returncode == 0
    assert result.stdout == expected_stdout
    assert result.stderr == ""


def test_explicit_empty_message_precedes_file(tmp_path):
    source = tmp_path / "source.md"
    source.write_text("ignored **file**", encoding="utf-8")
    result = _run_cli(["-m", "", "-f", str(source)])
    assert result.returncode == 0
    assert result.stdout == "\n"
    assert result.stderr == ""


def test_empty_cli_document_writes_output_file(tmp_path):
    output = tmp_path / "output.html"
    output.write_text("old contents", encoding="utf-8")
    result = _run_cli(["-m", "", "-o", str(output)], "ignored input")
    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""
    assert output.read_bytes() == b""


@pytest.mark.parametrize(("renderer", "expected_stdout"), [("html", "\n"), ("markdown", "\n\n"), ("rst", "\n\n")])
def test_empty_cli_file_control(tmp_path, renderer, expected_stdout):
    source = tmp_path / "empty.md"
    source.write_bytes(b"")
    result = _run_cli(["-f", str(source), "-r", renderer], "ignored input")
    assert result.returncode == 0
    assert result.stdout == expected_stdout
    assert result.stderr == ""


def test_cli_missing_terminal_input_control(capsys):
    with patch.object(sys, "argv", ["python -m mistune"]), patch("mistune.__main__.read_stdin", return_value=None):
        with pytest.raises(SystemExit) as error:
            cli()
    assert error.value.code == 1
    assert capsys.readouterr().out == "You must specify a message or file\n"
