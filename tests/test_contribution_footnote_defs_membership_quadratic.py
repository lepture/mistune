"""Regression test synthesized by blackhole_agent.upstream_contribution.

Runs the minimized standalone repro for defect footnote-defs-membership-quadratic against the
patched source tree; the repro exits 0 only once the defect is repaired.
"""

import subprocess
import sys
from pathlib import Path

REPRO = Path(__file__).resolve().parent / 'footnote_defs_quadratic.py'
SRC = Path(__file__).resolve().parents[1] / 'src'


def test_footnote_defs_membership_quadratic_regression() -> None:
    proc = subprocess.run([sys.executable, str(REPRO), str(SRC)], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr[-400:]
