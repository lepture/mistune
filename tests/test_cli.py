import io
import sys
from contextlib import redirect_stdout
from unittest.mock import patch

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
